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

        print(f"Rouge gauche : {red_left_pct:.1f} % | Vert droite : {green_right_pct:.1f} %")

        # Si au moins une couleur est bien présente, on continue
        if red_left_pct > 3 and green_right_pct > 3:
            return "correct"
        elif red_left_pct > 25 and green_right_pct < 3:
            return "turn_right"  # Peut-être un virage à droite
        elif green_right_pct > 25 and red_left_pct < 3:
            return "turn_left"  # Peut-être un virage à gauche
        else:
            return "incorrect"


    def check_obstacles(self):
        """Analyse les données du LiDAR et retourne l'état de la trajectoire"""
        points = self.lidar.get_points()
        if not points:
            return None

        # Filtrer les points pour les angles de 90° et 270°
        left = [p.distance for p in points if 85 <= p.angle <= 95]  # Autour de 90°
        right = [p.distance for p in points if 265 <= p.angle <= 275]  # Autour de 270°
        front = [p.distance for p in points if p.angle <= 5 or p.angle >= 355]

        avg_left = sum(left) / len(left) if left else 0
        avg_right = sum(right) / len(right) if right else 0
        min_front = min(front) if front else 999

        return min_front, avg_left, avg_right

    def turn_around(self):
        """Effectue un demi-tour si la détection couleur est mauvaise"""
        print("Mauvaise couleur détectée. Demi-tour...")
        self.pilot.UpdateControlCar(-1.0)
        time.sleep(0.8)
        self.pilot.UpdateDirectionCar(1.0)
        time.sleep(1.2)
        self.pilot.UpdateControlCar(0.0)
        self.pilot.UpdateDirectionCar(0.0)

    def avoid_obstacle(self, direction):
        """Évite un obstacle en changeant de direction momentanément"""
        print(f"Obstacle détecté. Évitement vers {direction}.")
        self.pilot.UpdateControlCar(0.13)
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

                min_front, avg_left, avg_right = check

                print(f"[DEBUG] Front min: {min_front:.1f} cm | Left avg: {avg_left:.1f} cm | Right avg: {avg_right:.1f} cm")

                # 1. SÉCURITÉ : obstacle trop proche devant (< 10 cm)
                if min_front < 0.10:
                    print("⚠️ Obstacle critique très proche ! Recul en urgence.")
                    self.pilot.UpdateControlCar(-1.0)
                    time.sleep(0.4)
                    self.pilot.UpdateControlCar(0.0)
                    continue

               

                # 3. OBSTACLE (mais pas en virage couleur)
                if min_front < 0.50:
                    print(f"🚧 Obstacle devant à {min_front:.1f} cm")
                    if avg_left > avg_right:
                        self.avoid_obstacle("left")
                    else:
                        self.avoid_obstacle("right")
                    continue
                
                elif avg_left < 35:
                    self.avoid_obstacle("right")
                    continue
                elif avg_right < 35:
                    self.avoid_obstacle("left")
                    continue

                # 4. TOUT EST OK
                elif color_status == "correct":
                    self.pilot.UpdateControlCar(0.13)
                    self.pilot.UpdateDirectionCar(0.0)

                # 5. Problème couleur
                else:
                    self.turn_around()

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
