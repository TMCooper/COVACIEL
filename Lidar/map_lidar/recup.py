import serial
import numpy as np
import matplotlib.pyplot as plt

# Configuration du port série
PORT = "/dev/serial0"  # Change si nécessaire
BAUDRATE = 230400      # Vitesse de transmission du LiDAR

# Initialisation du graphique
plt.ion()
fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111, projection='polar')
ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)

# Dictionnaire pour stocker les distances mises à jour en fonction de l'angle
lidar_data = {}

def read_lidar_data():
    """Lit les données du LiDAR et les traite"""
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
            while True:
                if ser.read(1) == b'\x54':  # Attendre le début de la trame
                    frame = ser.read(46)   # Lire la trame complète
                    
                    if len(frame) == 46:
                        process_data(frame)  # On passe bien 'frame' à la fonction
                        plt.pause(0.1)  # Rafraîchissement du graphique
    except Exception as e:
        print(f"Erreur : {e}")

def process_data(frame):
    """Met à jour les distances selon l'angle détecté"""
    if frame[0] != 0x2C:  # Vérification de la trame valide
        return

    # Extraction des angles de début et fin
    start_angle = (frame[3] + (frame[4] << 8)) / 100.0  # degrés
    end_angle = (frame[-6] + (frame[-5] << 8)) / 100.0  # degrés

    # Gérer le cas où l'angle traverse 0° (ex: 350° → 10°)
    if end_angle < start_angle:
        end_angle += 360

    # Générer les angles interpolés en radians
    angles = np.radians(np.linspace(start_angle, end_angle, 12, endpoint=True) % 360)

    # Extraction des distances et mise à jour du dictionnaire
    for i in range(12):
        idx = 5 + (i * 3)

        # Vérifier que l'index est valide avant d'accéder aux données
        if idx + 1 >= len(frame):
            print(f"Index hors limites : {idx} (longueur de frame : {len(frame)})")
            return  # On ignore cette trame

        dist_low = frame[idx]
        dist_high = frame[idx + 1]
        distance = ((dist_high << 8) | dist_low) / 1000.0  # Convertir en mètres

        if distance >= 0.5:  # Filtrage des distances < 0.5m
            lidar_data[angles[i]] = distance

    # Mise à jour du graphique
    ax.cla()
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 1)  # Limite max de 1m (ajustable)

    # Dessiner les points mis à jour
    ax.scatter(list(lidar_data.keys()), list(lidar_data.values()), color='red', s=10)

if __name__ == "__main__":
    read_lidar_data()  # Lancer la lecture du LiDAR
