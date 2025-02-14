import serial
import struct
import numpy as np
import matplotlib.pyplot as plt

# Configuration du port UART
PORT = "/dev/serial0"  # Port série du Raspberry Pi
BAUDRATE = 230400      # Vitesse de transmission du LiDAR

# Configuration de la figure matplotlib
plt.ion()  # Mode interactif
fig, ax = plt.subplots()
ax.set_xlim(-5, 5)
ax.set_ylim(-5, 5)
ax.set_xlabel("X (m)")
ax.set_ylabel("Y (m)")
scatter = ax.scatter([], [], color='red', s=10)  # Points vides au départ

def read_lidar_data():
    """Lit les données du LiDAR et les traite"""
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
            while True:
                if ser.read(1) == b'\x54':  # Vérification du début de trame
                    frame = ser.read(47)  # Lire les 47 octets de la trame
                    if len(frame) == 47:
                        process_data(frame)  # Traiter la trame si elle est valide
    except Exception as e:
        print(f"Erreur : {e}")

def process_data(frame):
    """Extraire et traiter les données du LiDAR"""
    if frame[1] == 0x2C:  # Vérification de la trame valide
        distances = []
        angles = []

        # Extraction des données de 12 points par trame
        for i in range(12):
            start = 6 + (i * 3)
            angle = struct.unpack("<H", frame[start:start+2])[0] / 100.0  # Conversion en degrés
            distance = struct.unpack("<H", frame[start+2:start+4])[0]  # Distance en millimètres
            distances.append(distance / 1000.0)  # Conversion en mètres
            angles.append(angle)

        # Convertir les angles et distances en coordonnées cartésiennes (X, Y)
        x_points = np.array(distances) * np.cos(np.radians(angles))
        y_points = np.array(distances) * np.sin(np.radians(angles))

        # Mise à jour de l'affichage des points
        scatter.set_offsets(np.c_[x_points, y_points])  # Met à jour les points sans réinitialiser
        plt.pause(0.01)  # Pause pour l'actualisation

if __name__ == "__main__":
    read_lidar_data()  # Commence à lire les données LiDAR
