import time
import os
import sys
import numpy as np 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Pilote.function.Pilote import Pilote
from Camera.class_array import ColorDetector
from Lidar.lidar_test.lidar_test import LidarSystem

class CarController:
    def __init__(self):
        self.pilote = Pilote(0.15, 0.0, 11, 13)  # Départ à 30% de vitesse
        self.camera = ColorDetector(num_frames=1)
        self.lidar = LidarSystem()

    def check_colors(self):
        self.camera.run_detection()
        red_left, green_right = self.camera.results[-1][1], self.camera.results[-1][2]
        return red_left, green_right

    def _get_distances_90_270(self, measurements):
        distances = {90: None, 270: None}
        for angle, dist, _ in measurements:
            if round(angle) == 90:
                distances[90] = dist
            elif round(angle) == 270:
                distances[270] = dist
        return distances

    def check_obstacles(self):
        measurements = self.lidar.measurements
        if not measurements:
            return None

        distances = self._get_distances_90_270(measurements)
        distance_90 = distances[90] if distances[90] is not None else float('inf')
        distance_270 = distances[270] if distances[270] is not None else float('inf')

        print(f"📏 Distance 90° (droite) : {distance_90:.2f} cm")
        print(f"📏 Distance 270° (gauche): {distance_270:.2f} cm")

        if distance_90 < 300 or distance_270 < 300:  # Seuil à ajuster si besoin
            if distance_90 < distance_270:
                return "left"   # obstacle à droite
            else:
                return "right"  # obstacle à gauche
        return "clear"

    def navigate(self):
        print("🚗 Démarrage de la navigation...")
        self.pilote.adjustSpeed(0.15)  # Vitesse de départ

        while True:
            red_left, green_right = self.check_colors()

            if red_left and green_right:
                print("✅ Couleurs correctes")
                self.pilote.adjustSpeed(0.15)
            else:
                print("❌ Couleurs incorrectes, demi-tour.")
                self.pilote.adjustSpeed(0.15)
                time.sleep(0.5)
                self.pilote.adjustSpeed(0.15)

            # ➤ Détection d'obstacles droite/gauche
            direction = self.check_obstacles()
            if direction == "left":
                print("🛑 Obstacle à droite → tourner à gauche")
                #self.pilote.adjustDirection(-1.0)
            elif direction == "right":
                print("🛑 Obstacle à gauche → tourner à droite")
                #self.pilote.adjustDirection(1.0)
            #else:
                #self.pilote.adjustDirection(0.0)

            time.sleep(0.1)

if __name__ == "__main__":
    car = CarController()
    car.navigate()
