import serial
import struct
import numpy as np
import matplotlib.pyplot as plt

# Configuration du port UART
PORT = "/dev/serial0"
BAUDRATE = 230400

def read_lidar_data():
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
            while True:
                if ser.read(1) == b'\x54':  # Début de trame
                    frame = ser.read(47)  # Lire le reste
                    if len(frame) == 47:
                        process_data(frame)
    except Exception as e:
        print(f"Erreur : {e}")

def process_data(frame):
    if frame[1] == 0x2C:  # Vérification longueur trame
        timestamp = struct.unpack("<H", frame[2:4])[0]
        speed = struct.unpack("<H", frame[4:6])[0] / 100.0  # RPM
        distances = []
        angles = []

        for i in range(12):  # 12 points par trame
            start = 6 + (i * 3)
            angle = struct.unpack("<H", frame[start:start+2])[0] / 100.0
            distance = struct.unpack("<H", frame[start+2:start+4])[0]
            distances.append(distance)
            angles.append(angle)

        print(f"Vitesse: {speed} RPM, Timestamp: {timestamp}")
        print(f"Angles: {angles}")
        print(f"Distances: {distances}")

        # Affichage en carte polaire
        plt.polar(np.radians(angles), distances, 'ro')
        plt.pause(0.01)
        plt.clf()

if __name__ == "__main__":
    read_lidar_data()
