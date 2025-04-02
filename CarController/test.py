import time
import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Pilote.function.Pilote import Pilote
from Camera.class_array import ColorDetector
from Lidar.lidar_test.lidar_test import LidarController, LidarAngleDistance

class CarController:
    def __init__(self):
        self.pilote = Pilote(0.0, 0.0, 11, 13)  # Moteur sur GPIO 11, direction sur GPIO 13
        self.camera = ColorDetector(num_frames=1)
        self.lidar = LidarController()

    def check_obstacles(self):
        measurements = self.lidar.get_measurements()  # Récupération des mesures du LiDAR

        # Vérification des données brutes du LiDAR
        if not measurements:
            print("❌ Aucune donnée LiDAR reçue !")
            return False, False

        distances = LidarAngleDistance.get_distances(measurements)

        distance_right = distances.get(90, float('inf'))  # Distance à 90° (droite)
        distance_left = distances.get(270, float('inf'))  # Distance à 270° (gauche)

        if distance_right == float('inf'):
            print("⚠️ Pas de donnée pour la droite, valeur par défaut utilisée.")
        if distance_left == float('inf'):
            print("⚠️ Pas de donnée pour la gauche, valeur par défaut utilisée.")

        print(f"Distance droite: {distance_right} cm, Distance gauche: {distance_left} cm")

        obstacle_right = distance_right < 5  # Seuil de 50 cm
        obstacle_left = distance_left < 5  # Seuil de 50 cm

        if obstacle_right or obstacle_left:
            print("🚨 Obstacle détecté !")
        else:
            print("✅ Aucun obstacle détecté.")

        return obstacle_right, obstacle_left

    def run_test(self):
        while True:
            self.check_obstacles()
            time.sleep(1)  # Pause pour éviter de spammer les logs

if __name__ == "__main__":
    car = CarController()
    car.run_test()
