import time
import os
import sys
import RPi.GPIO as gpio
import numpy as np
import cv2


# Ajoute le chemin parent au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Camera.test_capture_color import ColorDetector
from Pilote.function.Pilote import Pilote
from Lidar.Lidar_table_nv.lidar import LidarKit


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

        left_color = "red" if red_left_pct > 2 else "none"
        right_color = "green" if green_right_pct > 2 else "none"

        # Si les couleurs sont inversées (rouge à droite et vert à gauche), retourne "incorrect"
        if left_color == "green" and right_color == "red":
            return "incorrect"
        elif left_color == "red" or right_color == "green":
            return "correct"
        else:
            return "incorrect"

    def check_obstacles(self):
        """Analyse les données du LiDAR et retourne l'état de la trajectoire"""
        points = self.lidar.get_points()
        if not points:
            return None

        # Filtrer les points pour les angles spécifiques de 60°, 90°, 270°, et 300°
        right_60 = next((p.distance for p in points if 55 <= p.angle <= 65), 0)  # Point à 60°
        right_90 = next((p.distance for p in points if 85 <= p.angle <= 95), 0)  # Point à 90°
        left_270 = next((p.distance for p in points if 265 <= p.angle <= 275), 0)  # Point à 270°
        left_300 = next((p.distance for p in points if 295 <= p.angle <= 305), 0)  # Point à 300°
        min_front = min(p.distance for p in points if p.angle <= 5 or p.angle >= 355) if any(p.angle <= 5 or p.angle >= 355 for p in points) else 999

        return min_front, right_60, right_90, left_270, left_300


    def turn_around(self):
        """Effectue un demi-tour si la détection couleur est mauvaise"""
        print("Mauvaise couleur détectée. Demi-tour...")
        self.pilot.UpdateControlCar(-1.0)
        time.sleep(0.8)
        self.pilot.UpdateDirectionCar(-1.0)
        time.sleep(1.2)
        self.pilot.UpdateControlCar(0.0)
        self.pilot.UpdateDirectionCar(0.0)

    def avoid_obstacle(self, direction):
        """Évite un obstacle en changeant de direction momentanément"""
        print(f"Obstacle détecté. Évitement vers {direction}.")
        self.pilot.UpdateControlCar(0.1)
        if direction == "left":
            self.pilot.UpdateDirectionCar(-1.0)
        else:
            self.pilot.UpdateDirectionCar(1.0)
        time.sleep(0.6)
        self.pilot.UpdateDirectionCar(0.0)
        time.sleep(0.5)

    def drive(self):
        try:
            while True:
                color_status = self.get_color_status()
                check = self.check_obstacles()
                if check is None:
                    print("Aucune donnée LIDAR")
                    self.pilot.UpdateControlCar(0.0)
                    time.sleep(0.1)
                    continue

                min_front, right_60, right_90, left_270, left_300 = check

                print(f"[DEBUG] Front min: {min_front:.1f} mm | Right 60°: {right_60:.1f} mm | Right 90°: {right_90:.1f} mm | Left 270°: {left_270:.1f} mm | Left 300°: {left_300:.1f} mm")

                # 1. SÉCURITÉ : obstacle trop proche devant (< 10 cm)
                if min_front < 0.20:
                    print("⚠️ Obstacle critique très proche ! Recul en urgence.")
                    self.pilot.UpdateControlCar(-1.0)
                    time.sleep(0.4)
                    self.pilot.UpdateControlCar(0.0)
                    continue

                # 2. PRIORITÉ : virages couleur
                if color_status == "incorrect":
                    self.turn_around()
                    continue

                # 3. OBSTACLE (mais pas en virage couleur)
                if min_front < 0.35:
                    print(f"🚧 Obstacle devant à {min_front:.1f} mm")
                    if (left_270 + left_300) > (right_60 + right_90):
                        self.avoid_obstacle("left")
                    else:
                        self.avoid_obstacle("right")
                    continue

                elif (right_60 + right_90) < 35:
                    self.avoid_obstacle("left")
                    continue
                elif (left_270 + left_300) < 35:
                    self.avoid_obstacle("right")
                    continue

                # 4. TOUT EST OK
                elif color_status == "correct":
                    self.pilot.UpdateControlCar(0.01)
                    self.pilot.UpdateDirectionCar(0.0)

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
