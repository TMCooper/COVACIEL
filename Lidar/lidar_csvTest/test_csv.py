import numpy as np
import matplotlib.pyplot as plt
import serial
from enum import Enum
import struct
import csv

# ----------------------------------------------------------------------
# Paramètres principaux
# ----------------------------------------------------------------------
SERIAL_PORT = "/dev/ttyS0"        # Modifiez selon votre configuration
MEASUREMENTS_PER_PLOT = 1100
PLOT_MAX_RANGE = 4.0             # En mètres
PLOT_AUTO_RANGE = False
PLOT_CONFIDENCE = True
PLOT_CONFIDENCE_COLOUR_MAP = "bwr_r"
PRINT_DEBUG = False

# Plage d'angles [0°, 45°]
ANGLE_MIN = 0.0
ANGLE_MAX = 45.0

# Nom du fichier CSV dans lequel on enregistre le tableau des mesures
CSV_FILENAME = "lidar_angle_0_45_table.csv"

# ----------------------------------------------------------------------
# Format du paquet (LD06)
# ----------------------------------------------------------------------
PACKET_LENGTH = 47
MEASUREMENT_LENGTH = 12
MESSAGE_FORMAT = "<xBHH" + "HB" * MEASUREMENT_LENGTH + "HHB"

State = Enum("State", ["SYNC0", "SYNC1", "SYNC2", "LOCKED", "UPDATE_PLOT"])

# ----------------------------------------------------------------------
# Fonctions utilitaires
# ----------------------------------------------------------------------

def parse_lidar_data(data):
    """
    Extrait les données utiles d'un paquet brut (bytes) selon MESSAGE_FORMAT.
    Retourne une liste de tuples (angle, distance, confiance).
    """
    length, speed, start_angle, *pos_data, stop_angle, timestamp, crc = \
        struct.unpack(MESSAGE_FORMAT, data)

    start_angle = float(start_angle) / 100.0
    stop_angle  = float(stop_angle) / 100.0

    # Gestion du cas où l'angle final est inférieur à l'angle initial
    if stop_angle < start_angle:
        stop_angle += 360.0

    step_size = (stop_angle - start_angle) / (MEASUREMENT_LENGTH - 1)

    angles     = [start_angle + step_size * i for i in range(MEASUREMENT_LENGTH)]
    distances  = pos_data[0::2]  # mm
    confidences= pos_data[1::2]

    if PRINT_DEBUG:
        print(f"length={length}, speed={speed}, start_angle={start_angle}, stop_angle={stop_angle}, "
              f"timestamp={timestamp}, crc={crc}")
    return list(zip(angles, distances, confidences))

def get_xyc_data(measurements):
    """
    Convertit la liste [ (angle, distance, confiance), ... ] en coordonnées x, y
    (en mètres) et en tableau de confiance.
    """
    angles     = np.array([m[0] for m in measurements])
    distances  = np.array([m[1] for m in measurements])
    confidences= np.array([m[2] for m in measurements])

    # Conversion polaire -> cartésien
    x = np.sin(np.radians(angles)) * (distances / 1000.0)
    y = np.cos(np.radians(angles)) * (distances / 1000.0)
    return x, y, confidences

def filter_angle_range(measurements, angle_min=ANGLE_MIN, angle_max=ANGLE_MAX):
    """
    Conserve uniquement les mesures dont l'angle est compris entre angle_min et angle_max.
    """
    return [m for m in measurements if angle_min <= m[0] <= angle_max]

def save_angle_range_csv(measurements, filename=CSV_FILENAME):
    """
    Enregistre dans un fichier CSV chaque mesure (angle, distance, confiance)
    dont l'angle est dans [ANGLE_MIN, ANGLE_MAX].
    Chaque ligne = [angle, distance(mm), confiance].
    """
    # On filtre d'abord les mesures
    filtered = filter_angle_range(measurements, ANGLE_MIN, ANGLE_MAX)

    # Création de l'entête si le fichier n'existe pas encore
    try:
        with open(filename, mode='x', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Angle (°)", "Distance (mm)", "Confiance"])
    except FileExistsError:
        pass

    # Écriture des mesures filtrées
    with open(filename, mode='a', newline='') as f:
        writer = csv.writer(f)
        for (angle, distance, confidence) in filtered:
            writer.writerow([f"{angle:.2f}", distance, confidence])

# ----------------------------------------------------------------------
# Programme principal
# ----------------------------------------------------------------------
def on_plot_close(event):
    global running
    running = False

if __name__ == "__main__":
    lidar_serial = serial.Serial(SERIAL_PORT, 230400, timeout=0.5)
    measurements = []
    data = b''
    state = State.SYNC0

    # Plot interactif
    plt.ion()
    plt.rcParams['figure.figsize'] = [10, 10]
    plt.rcParams['lines.markersize'] = 2.0

    if PLOT_CONFIDENCE:
        graph = plt.scatter([], [], c=[], marker=".", vmin=0, vmax=255,
                            cmap=PLOT_CONFIDENCE_COLOUR_MAP)
    else:
        graph = plt.plot([], [], ".")[0]

    graph.figure.canvas.mpl_connect('close_event', on_plot_close)
    plt.xlim(-PLOT_MAX_RANGE, PLOT_MAX_RANGE)
    plt.ylim(-PLOT_MAX_RANGE, PLOT_MAX_RANGE)

    running = True

    while running:
        if state == State.SYNC0:
            data = b''
            measurements = []
            # On attend le 1er octet 0x54
            if lidar_serial.read() == b'\x54':
                data = b'\x54'
                state = State.SYNC1

        elif state == State.SYNC1:
            # On attend le 2ème octet 0x2C
            if lidar_serial.read() == b'\x2C':
                state = State.SYNC2
                data += b'\x2C'
            else:
                state = State.SYNC0

        elif state == State.SYNC2:
            # On lit le reste du paquet
            data += lidar_serial.read(PACKET_LENGTH - 2)
            if len(data) != PACKET_LENGTH:
                state = State.SYNC0
                continue
            # Parse le paquet
            measurements += parse_lidar_data(data)
            state = State.LOCKED

        elif state == State.LOCKED:
            # On lit le prochain paquet
            data = lidar_serial.read(PACKET_LENGTH)
            if len(data) != PACKET_LENGTH or data[0] != 0x54:
                print("WARNING: Serial sync lost")
                state = State.SYNC0
                continue
            measurements += parse_lidar_data(data)

            # Quand on a accumulé assez de mesures, on passe à UPDATE_PLOT
            if len(measurements) > MEASUREMENTS_PER_PLOT:
                state = State.UPDATE_PLOT

        elif state == State.UPDATE_PLOT:
            # Filtrage sur la plage [0°, 45°]
            filtered_measurements = filter_angle_range(measurements, ANGLE_MIN, ANGLE_MAX)

            # Conversion en x, y pour affichage
            if filtered_measurements:
                x, y, c = get_xyc_data(filtered_measurements)
            else:
                x, y, c = np.array([]), np.array([]), np.array([])

            # Ajustement automatique du plot si nécessaire
            if PLOT_AUTO_RANGE and len(x) > 0 and len(y) > 0:
                max_val = max([max(abs(x)), max(abs(y))]) * 1.2
                plt.xlim(-max_val, max_val)
                plt.ylim(-max_val, max_val)

            # On met à jour le scatter plot
            graph.remove()
            if PLOT_CONFIDENCE:
                graph = plt.scatter(x, y, c=c, marker=".", vmin=0, vmax=255,
                                    cmap=PLOT_CONFIDENCE_COLOUR_MAP)
            else:
                graph = plt.plot(x, y, 'b.')[0]
            plt.pause(0.00001)

            # Enregistrement CSV de toutes les mesures (angle, distance, confiance) dans la plage [0°, 45°]
            save_angle_range_csv(measurements, CSV_FILENAME)

            # On repasse en mode LOCKED et on vide la liste
            state = State.LOCKED
            measurements = []
