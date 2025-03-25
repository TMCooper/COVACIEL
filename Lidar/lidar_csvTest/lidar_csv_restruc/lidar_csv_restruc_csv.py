import numpy as np
import matplotlib.pyplot as plt
import serial
from enum import Enum
import struct
import csv
import RPi.GPIO as GPIO

# ----------------------------------------------------------------------
# System Constants
# ----------------------------------------------------------------------
SERIAL_PORT = "/dev/ttyS0"
MEASUREMENTS_PER_PLOT = 1100
PLOT_MAX_RANGE = 4  # in meters
PLOT_AUTO_RANGE = False
PLOT_CONFIDENCE = True
PLOT_CONFIDENCE_COLOUR_MAP = "bwr_r"
PRINT_DEBUG = False

# PWM settings
PWM_PIN = 12  # GPIO pin for PWM output
PWM_FREQUENCY = 3600 # Initial PWM frequency in Hz

# ----------------------------------------------------------------------
# Main Packet Format
# ----------------------------------------------------------------------
PACKET_LENGTH = 47
MEASUREMENT_LENGTH = 12
MESSAGE_FORMAT = "<xBHH" + "HB" * MEASUREMENT_LENGTH + "HHB"

class State(Enum): # Utilisé pour définir les différents états de synchronisation des données série.
    SYNC0 = 1
    SYNC1 = 2
    SYNC2 = 3
    LOCKED = 4
    UPDATE_PLOT = 5

class LidarDataParser: #Classe pour analyser les données brutes du LiDAR et les convertir en mesures utilisables.
    @staticmethod
    def parse_lidar_data(data): #Analyse les données brutes du LiDAR et retourne les mesures sous forme de liste de tuples (angle, distance, confiance)
        length, speed, start_angle, *pos_data, stop_angle, timestamp, crc = \
            struct.unpack(MESSAGE_FORMAT, data)
        start_angle = float(start_angle) / 100.0
        stop_angle = float(stop_angle) / 100.0
        if stop_angle < start_angle:
            stop_angle += 360.0
        step_size = (stop_angle - start_angle) / (MEASUREMENT_LENGTH - 1)
        angle = [start_angle + step_size * i for i in range(0, MEASUREMENT_LENGTH)]
        distance = pos_data[0::2]
        confidence = pos_data[1::2]
        if PRINT_DEBUG:
            print(length, speed, start_angle, *pos_data, stop_angle, timestamp, crc)
        return list(zip(angle, distance, confidence))

class LidarPlotter: # Classe pour gérer la visualisation des données LiDAR en utilisant Matplotlib
    def __init__(self): #Initialise le graphique et configure les paramètres de visualisation.
        plt.ion()
        plt.rcParams['figure.figsize'] = [10, 10]
        plt.rcParams['lines.markersize'] = 2.0
        if PLOT_CONFIDENCE:
            self.graph = plt.scatter([], [], c=[], marker=".", vmin=0, vmax=255, cmap=PLOT_CONFIDENCE_COLOUR_MAP)
        else:
            self.graph = plt.plot([], [], ".")[0]
        self.graph.figure.canvas.mpl_connect('close_event', self.on_plot_close)
        plt.xlim(-PLOT_MAX_RANGE, PLOT_MAX_RANGE)
        plt.ylim(-PLOT_MAX_RANGE, PLOT_MAX_RANGE)

    def on_plot_close(self, event): # Gère l'événement de fermeture de la fenêtre de visualisation.
        self.running = False

    def update_plot(self, measurements): # Met à jour le graphique avec les nouvelles mesures 
        x, y, c = self.get_xyc_data(measurements)
        if PLOT_AUTO_RANGE:
            max_val = max([max(abs(x)), max(abs(y))]) * 1.2
            plt.xlim(-max_val, max_val)
            plt.ylim(-max_val, max_val)
        self.graph.remove()
        if PLOT_CONFIDENCE:
            self.graph = plt.scatter(x, y, c=c, marker=".", vmin=0, vmax=255, cmap=PLOT_CONFIDENCE_COLOUR_MAP)
        else:
            self.graph = plt.plot(x, y, 'b.')[0]
        plt.pause(0.00001)

    @staticmethod
    def get_xyc_data(measurements): # Convertit les mesures en coordonnées cartésiennes pour le tracé
        angle = np.array([measurement[0] for measurement in measurements])
        distance = np.array([measurement[1] for measurement in measurements])
        confidence = np.array([measurement[2] for measurement in measurements])
        x = np.sin(np.radians(angle)) * (distance / 1000.0)
        y = np.cos(np.radians(angle)) * (distance / 1000.0)
        return x, y, confidence

class CsvWriter: # Classe pour gérer l'écriture des distances à l'angle 0 dans un fichier CSV
    def __init__(self, filename="lidar_distance_at_zero.csv"):
        self.filename = filename
        self.init_csv()

    def init_csv(self):
        try:
            with open(self.filename, mode='x', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Distance at 0° (cm)"])
        except FileExistsError:
            pass

    def write_distance_at_zero(self, distance_mm):
        distance_cm = distance_mm / 10.0
        with open(self.filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([distance_cm])

class PWMController: # Classe pour gérer la configuration et le contrôle du signal PWM
    def __init__(self, pin, frequency=PWM_FREQUENCY): # Initialise la broche PWM avec une fréquence spécifiée
        self.pin = pin
        self.frequency = frequency
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, self.frequency)

    def set_speed(self, duty_cycle): # vitesse de rotation 
        """Set the motor speed using PWM duty cycle (0-100%)."""
        self.pwm.start(duty_cycle)

    def change_frequency(self, new_frequency): # Change la fréquence du signal PWM
        """Change the PWM frequency."""
        self.pwm.ChangeFrequency(new_frequency)
        self.frequency = new_frequency  # Update the internal frequency value

    def stop(self):
        """Stop the PWM signal."""
        self.pwm.stop()

class LidarController: # Classe principale pour contrôler le LiDAR, traiter les données et gérer la visualisation.
    def __init__(self, port=SERIAL_PORT):
        self.lidar_serial = serial.Serial(port, 230400, timeout=0.5)
        self.measurements = []
        self.data = b''
        self.state = State.SYNC0
        self.plotter = LidarPlotter()
        self.csv_writer = CsvWriter()
        self.pwm_controller = PWMController(PWM_PIN)
        self.running = True

    def run(self):
        # Set initial motor speed (e.g., 50% duty cycle)
        self.pwm_controller.set_speed(50)

        # Example of changing the PWM frequency
        self.pwm_controller.change_frequency(1000)  # Change to 1000 Hz

        while self.running:
            if self.state == State.SYNC0:
                self.data = b''
                self.measurements = []
                if self.lidar_serial.read() == b'\x54':
                    self.data = b'\x54'
                    self.state = State.SYNC1
            elif self.state == State.SYNC1:
                if self.lidar_serial.read() == b'\x2C':
                    self.state = State.SYNC2
                    self.data += b'\x2C'
                else:
                    self.state = State.SYNC0
            elif self.state == State.SYNC2:
                self.data += self.lidar_serial.read(PACKET_LENGTH - 2)
                if len(self.data) != PACKET_LENGTH:
                    self.state = State.SYNC0
                    continue
                self.measurements += LidarDataParser.parse_lidar_data(self.data)
                self.state = State.LOCKED
            elif self.state == State.LOCKED:
                self.data = self.lidar_serial.read(PACKET_LENGTH)
                if self.data[0] != 0x54 or len(self.data) != PACKET_LENGTH:
                    print("WARNING: Serial sync lost")
                    self.state = State.SYNC0
                    continue
                self.measurements += LidarDataParser.parse_lidar_data(self.data)
                if len(self.measurements) > MEASUREMENTS_PER_PLOT:
                    self.state = State.UPDATE_PLOT
            elif self.state == State.UPDATE_PLOT:
                self.plotter.update_plot(self.measurements)
                self.save_distance_at_zero(self.measurements)
                self.state = State.LOCKED
                self.measurements = []

    def save_distance_at_zero(self, measurements):
        for angle, distance, _ in measurements:
            # Debugging: Print angle and distance
            print(f"Angle: {angle}, Distance: {distance} mm")
            if abs(angle) < 1e-6:  # Check if angle is approximately 0
                self.csv_writer.write_distance_at_zero(distance)
                break

if __name__ == "__main__":
    try:
        controller = LidarController()
        controller.run()
    finally:
        GPIO.cleanup()
