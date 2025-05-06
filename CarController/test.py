import time
import os
import sys
import numpy as np
import cv2

# Ajoute le chemin parent au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Camera.test_capture_color import ColorDetector
from Pilote.function.Pilote import Pilote
from Lidar.Lidar_table_nv.lidar_table import LidarKit

class CarController:
    def __init__(self):
        self.camera = ColorDetector()
        self.lidar = LidarKit("/dev/ttyS0", debug=True)
        self.pilot = Pilote(0.0, 0.0, 32, 33)
        self.lidar.start()

    def get_color_status(self):
        """Analyse les couleurs détectées et retourne un état"""
        frame = self.camera.picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        red_left_pct, green_right_pct, _ = self.camera.process_frame(frame)

        left_color = "red" if red_left_pct > 10 else "none"
        right_color = "green" if green_right_pct > 10 else "none"

        if left_color == "red" and right_color == "green":
            return "correct"
        else:
            return "incorrect"

    def check_obstacles(self):
        """Analyse les données du LiDAR et retourne l'état de la trajectoire"""
        points = self.lidar.get_points()
        if not points:
            return None

        front = [p for p in points if (p.angle <= 20 or p.angle >= 340)]
        left = [p for p in points if 240 <= p.angle <= 300]
        right = [p for p in points if 60 <= p.angle <= 120]

        front_clear = all(p.distance > 0.3 for p in front)
        left_avg = sum(p.distance for p in left) / len(left) if left else float('inf')
        right_avg = sum(p.distance for p in right) / len(right) if right else float('inf')

        if not front_clear:
            return "left" if left_avg > right_avg else "right"
        return "clear"

    def turn_around(self):
         """Effectue un demi-tour si la détection couleur est mauvaise"""
         print("Mauvaise couleur détectée. Demi-tour...")
         self.pilot.adjustSpeed(-1)
         time.sleep(0.8)
         self.pilot.changeDirection(1)
         time.sleep(1.2)
         self.pilot.adjustSpeed(0.0)
         self.pilot.changeDirection(0.0)

    def avoid_obstacle(self, direction):
        """Évite un obstacle en changeant de direction momentanément"""
        print(f"Obstacle détecté. Évitement vers {direction}.")
        self.pilot.adjustSpeed(0.28)
        if direction == "left":
            self.pilot.changeDirection(-1)
        elif direction == "right":
            self.pilot.changeDirection(1)
        time.sleep(0.6)
        self.pilot.changeDirection(0.0)

    def drive(self):
        """Boucle principale de conduite autonome"""
        try:
            while True:
                color_status = self.get_color_status()
                if color_status == "incorrect":
                    self.turn_around()
                    continue

                obstacle_status = self.check_obstacles()
                if obstacle_status == "clear":
                    self.pilot.adjustSpeed(0.35)
                    self.pilot.changeDirection(0.0)
                elif obstacle_status in ("left", "right"):
                    self.avoid_obstacle(obstacle_status)
                else:
                    self.pilot.adjustSpeed(0.0)
                    print("Aucune donnée LIDAR")

                time.sleep(0.1)

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Arrête le contrôleur et nettoie les ressources"""
        self.pilot.stop()
        self.lidar.stop()
        self.camera.picam2.stop()
        print("Contrôleur arrêté.")

if __name__ == "__main__":
    car = CarController()
    car.drive()
