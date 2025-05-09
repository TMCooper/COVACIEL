import time
import os
import sys
import RPi.GPIO as gpio
import numpy as np
import cv2
import RPi.GPIO as gpio


# Ajoute le chemin parent au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Camera.test_capture_color import ColorDetector
from Pilote.function.Pilote import Pilote
from Lidar.Lidar_table_nv.lidar_table_SIG import LidarKit


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

        left_color = "red" if red_left_pct > 5 else "none"
        right_color = "green" if green_right_pct > 5 else "none"

        if left_color == "red" and right_color == "green":
            return "correct"
        else:
            return "incorrect"

    def adjust_to_center(self):
        """Ajuste la direction pour rester au centre de la piste"""
        points = self.lidar.get_points()
        if not points:
            return None

    # Sélectionne les points dans une zone large autour de 90° (droite) et 270° (gauche)
        left = [p for p in points if 265 <= p.angle <= 275]
        right = [p for p in points if 85 <= p.angle <= 95]

        if len(left) < 3 or len(right) < 3:
            print("Données insuffisantes du LiDAR à gauche/droite")
            self.pilot.UpdateDirectionCar(0.0)
            return

        avg_left = sum(left) / len(left)
        avg_right = sum(right) / len(right)
        diff = avg_right - avg_left

        print(f"Gauche: {avg_left:.1f} cm | Droite: {avg_right:.1f} cm | Diff: {diff:.1f} cm")

        if abs(diff) < 2:  # moins de 2 cm = centré
            self.pilot.UpdateDirectionCar(0)
        elif diff > 0:
            self.pilot.UpdateDirectionCar(-1)  # Trop à gauche → tourner à droite
        else:
            self.pilot.UpdateDirectionCar(1)   # Trop à droite → tourner à gauche



    def turn_around(self):
        """Effectue un demi-tour si la détection couleur est mauvaise"""
        print("Mauvaise couleur détectée. Demi-tour...")
        self.pilot.UpdateControlCar(-1)
        time.sleep(0.8)
        self.pilot.UpdateDirectionCar(1)
        time.sleep(1.2)
        self.pilot.UpdateControlCar(0.0)
        self.pilot.UpdateDirectionCar(0.0)

    def avoid_obstacle(self, direction):
        """Évite un obstacle en changeant de direction momentanément"""
        print(f"Obstacle détecté. Évitement vers {direction}.")
        self.pilot.UpdateControlCar(0.13)
        if direction == "left":
            self.pilot.UpdateDirectionCar(1)
        elif direction == "right":
            self.pilot.UpdateDirectionCar(-1)
        time.sleep(0.6)
        self.pilot.UpdateDirectionCar(0.0)

    def drive(self):
        """Boucle principale de conduite autonome avec centrage LiDAR"""
        try:
            while True:
                color_status = self.get_color_status()
                if color_status == "incorrect":
                    self.turn_around()
                    continue

                self.pilot.UpdateControlCar(0.13)
                self.adjust_to_center()
                time.sleep(0.1)

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Arrête le contrôleur et nettoie les ressources"""
        self.pilot.stop()
        self.lidar.stop()
        self.camera.picam2.stop()
        gpio.cleanup()  # Nettoyer les GPIO
        print("Contrôleur arrêté.")

if __name__ == "__main__":
    car = CarController()
    car.drive()
