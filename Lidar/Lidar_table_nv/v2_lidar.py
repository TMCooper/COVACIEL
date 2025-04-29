import serial
import threading
import numpy as np
import time
import matplotlib.pyplot as plt
from collections import namedtuple

# Définition d’un point de mesure Lidar
LidarPoint = namedtuple("LidarPoint", ["angle", "distance", "confidence", "timestamp"])

# Constantes pour le LD06
PACKET_LEN = 47
NUM_POINTS = 12
CONFIDENCE_THRESHOLD = 50

# Table de vérification CRC
CRC_TABLE = [
    0x00, 0x4d, 0x9a, 0xd7, 0x79, 0x34, 0xe3, 0xae,
    0xf2, 0xbf, 0x68, 0x25, 0x8b, 0xc6, 0x11, 0x5c,
    0xa9, 0xe4, 0x33, 0x7e, 0xd0, 0x9d, 0x4a, 0x07,
    0x5b, 0x16, 0xc1, 0x8c, 0x22, 0x6f, 0xb8, 0xf5
] + [0] * (256 - 32)


class LidarLD06:
    """
    Classe qui gère le fonctionnement du Lidar LD06
    """
    def __init__(self, port="/dev/ttyS0", baudrate=230400):
        self.ser = serial.Serial(port, baudrate, timeout=0.1)
        self.running = False
        self.thread = None

        # Tableau de 360 valeurs pour stocker les distances selon les angles
        # Exemple : tableau[90] = distance en mm mesurée à 90°
        self.tableau_lidar_mm = [0] * 360

    def calc_crc8(self, data):
        crc = 0
        for b in data[:46]:
            crc = CRC_TABLE[(crc ^ b) & 0xFF]
        return crc

    def start(self):
        """
        Démarre l’acquisition en lançant un thread de lecture.
        """
        self.running = True
        self.thread = threading.Thread(target=self.read_loop)
        self.thread.start()

    def stop(self):
        """
        Arrête proprement l’acquisition.
        """
        self.running = False
        self.thread.join()
        self.ser.close()

    def read_loop(self):
        """
        Boucle de lecture des paquets envoyés par le Lidar.
        Met à jour le tableau tableau_lidar_mm.
        """
        while self.running:
            # Synchronisation sur le premier octet du paquet
            byte = self.ser.read(1)
            if not byte or byte[0] != 0x54:
                continue

            # Lecture du reste du paquet (47 octets)
            packet = bytearray([0x54])
            while len(packet) < PACKET_LEN:
                packet += self.ser.read(PACKET_LEN - len(packet))
            if len(packet) < PACKET_LEN:
                continue

            if self.calc_crc8(packet) != packet[46]:
                continue  # Paquet corrompu, on ignore

            start_angle = int.from_bytes(packet[4:6], "little") / 100.0
            end_angle = int.from_bytes(packet[42:44], "little") / 100.0
            timestamp = int.from_bytes(packet[44:46], "little")
            step = (end_angle - start_angle + 360.0 if end_angle < start_angle else end_angle - start_angle) / (NUM_POINTS - 1)

            # Lecture des 12 points de mesure dans le paquet
            for i in range(NUM_POINTS):
                j = 6 + 3 * i
                dist = int.from_bytes(packet[j:j+2], "little")
                conf = packet[j+2]
                angle = int((start_angle + i * step) % 360)

                if conf >= CONFIDENCE_THRESHOLD and dist > 0:
                    self.tableau_lidar_mm[angle] = dist  # Enregistrement dans le tableau

    def get_distance(self, angle):
        """
        Retourne la distance mesurée à un angle donné (en degré).
        """
        angle = int(angle) % 360
        return self.tableau_lidar_mm[angle]

    def get_distances_range(self, angle_min, angle_max):
        """
        Retourne les distances pour un ensemble d’angles entre angle_min et angle_max.
        """
        angle_min = int(angle_min) % 360
        angle_max = int(angle_max) % 360

        if angle_min <= angle_max:
            return self.tableau_lidar_mm[angle_min:angle_max + 1]
        else:
            # Cas où l’intervalle est circulaire (ex : 350 à 10)
            return self.tableau_lidar_mm[angle_min:] + self.tableau_lidar_mm[:angle_max + 1]


class LidarViewer:
    """
    Classe pour afficher les données Lidar en graphique polaire.
    """
    def __init__(self, lidar: LidarLD06):
        self.lidar = lidar

    def show_polar_plot(self):
        teta = np.radians(np.arange(360))  # Angles en radians
        distances = np.array(self.lidar.tableau_lidar_mm)  # Distances

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='polar')
        ax.scatter(teta, distances, s=5)
        ax.set_title("Carte polaire du LIDAR LD06")
        ax.set_rmax(8000)
        ax.grid(True)
        plt.show()


# --- Code principal ---
if __name__ == "__main__":
    lidar = LidarLD06("/dev/ttyS0")
    lidar.start()

    try:
        print("Acquisition en cours (5 secondes)...")
        time.sleep(5)

        # Exemple d’usage des méthodes personnalisées
        print("Distance à 90° :", lidar.get_distance(90), "mm")
        print("Distances de 60° à 120° :", lidar.get_distances_range(60, 120))

    except KeyboardInterrupt:
        print("Arrêt par l'utilisateur.")
    finally:
        lidar.stop()

        viewer = LidarViewer(lidar)
        viewer.show_polar_plot()
