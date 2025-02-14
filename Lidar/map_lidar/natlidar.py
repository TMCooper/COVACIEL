import serial
import struct
import numpy as np
import matplotlib.pyplot as plt

# Configuration du port série
PORT = "/dev/serial0"  # Change si tu utilises un port différent
BAUDRATE = 230400

# Initialisation du graphique
plt.ion()  # Mode interactif pour mise à jour en temps réel
fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111, projection='polar')
ax.set_theta_zero_location('N')  # Placer 0° en haut
ax.set_theta_direction(-1)  # Sens antihoraire

# Fonction pour lire les données du LiDAR
def read_lidar_data():
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
            while True:
                if ser.read(1) == b'\x54':  # Début de la trame
                    frame = ser.read(47)  # Lire une trame complète
                    if len(frame) == 47:
                        process_data(frame)
    except Exception as e:
        print(f"Erreur : {e}")

# Fonction pour traiter les données de la trame
def process_data(frame):
    if frame[1] == 0x2C:  # Vérification de la longueur de la trame
        distances = []
        angles = []
        
        for i in range(12):  # LiDAR LD06 envoie 12 points par trame
            start = 6 + (i * 3)
            angle = struct.unpack("<H", frame[start:start+2])[0] / 100.0  # Angle en degrés
            distance = struct.unpack("<H", frame[start+2:start+4])[0]  # Distance en mm
            angles.append(np.radians(angle))  # Convertir en radians
            distances.append(distance)

        # Mettre à jour le graphique avec les nouvelles données
        ax.cla()  # Effacer l'ancien graphique
        ax.set_theta_zero_location('N')  # 0° en haut
        ax.set_theta_direction(-1)  # Sens antihoraire

        # Affichage des points autour de 360°
        ax.scatter(angles, distances, color='red', s=50)  # Points en rouge, taille ajustée (s=50)
        ax.set_title("LiDAR Détection en Temps Réel")
        plt.pause(0.1)  # Mise à jour de l'affichage

if __name__ == "__main__":
    read_lidar_data()
