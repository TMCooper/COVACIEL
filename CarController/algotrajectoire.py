import time
import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Pilote.function.Pilote import Pilote
from Camera.class_array import ColorDetector
from Lidar.Lidar_table_nv.lidar_table import LidarKit  

class CarController:
    def __init__(self):
        self.pilote = Pilote(0.0, 0.0, 11, 15)
        self.camera = ColorDetector(num_frames=1)
        self.lidar = LidarKit("/dev/ttyS0", debug=True)  
        self.lidar.start()

    def check_colors(self):
        self.camera.run_detection()
        red_left, green_right = self.camera.results[-1][1], self.camera.results[-1][2]
        return red_left, green_right

    def _get_distances_90_270(self, points):
        distances = {90: None, 270: None}
        for p in points:
            angle = round(p.angle)
            if angle == 90:
                distances[90] = p.distance * 100  # en cm
            elif angle == 270:
                distances[270] = p.distance * 100  # en cm
        return distances

    def check_obstacles(self):
        points = self.lidar.get_points()
        if not points:
            print("Aucune donnée du LiDAR.")
            return None

        angles = [round(p.angle) for p in points]

        distances = self._get_distances_90_270(points)
        distance_90 = distances[90] if distances[90] is not None else float('inf')
        distance_270 = distances[270] if distances[270] is not None else float('inf')

        print(f"Distance 90° (droite) : {distance_90:.2f} cm")
        print(f"Distance 270° (gauche): {distance_270:.2f} cm")

        if distance_90 < 300 or distance_270 < 300:
            if distance_90 < distance_270:
                return "left"
            else:
                return "right"
        return "clear"

    def navigate(self):
        print("Démarrage de la navigation...")
        self.pilote.adjustSpeed(0.15)
        last_direction = None  

        while True:
            red_left, green_right = self.check_colors()

            if red_left and green_right:
                print("Couleurs correctes")
                self.pilote.adjustSpeed(0.15)
            else:
                print("Couleurs incorrectes, demi-tour.")
                self.pilote.adjustSpeed(0.15)
                time.sleep(0.5)
                self.pilote.adjustSpeed(0.15)

            try: 
                direction = self.check_obstacles()
            except Exception as e: 
                print(f"Erreur lors de la vérification des obstacles : {e}")
                direction = None

            if direction == "left":
                new_direction = -1.0
            elif direction == "right":
                new_direction = 1.0
            else:
                new_direction = 0.0

            if new_direction != last_direction:
                print(f"Changement de direction : {new_direction}")
                self.pilote.changeDirection(new_direction)
                last_direction = new_direction

            time.sleep(0.1)

if __name__ == "__main__":
    car = CarController()
    car.navigate()
