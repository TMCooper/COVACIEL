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

        print(f"Rouge gauche : {red_left_pct:.1f} % | Vert droite : {green_right_pct:.1f} %")

        # Si au moins une couleur est bien présente, on continue
        if red_left_pct > 5 and green_right_pct > 5:
            return "correct"
        elif red_left_pct > 10 and green_right_pct < 3:
            return "turn_right"  # Peut-être un virage à droite
        elif green_right_pct > 10 and red_left_pct < 3:
            return "turn_left"  # Peut-être un virage à gauche
        else:
            return "incorrect"


    def check_obstacles(self):
        """Analyse les données du LiDAR et retourne l'état de la trajectoire"""
        points = self.lidar.get_points()
        if not points:
            return None

        # Filtrer les points pour les angles de 90° et 270°
        left_points = [p for p in points if 85 <= p.angle <= 95]  # Autour de 90°
        right_points = [p for p in points if 265 <= p.angle <= 275]  # Autour de 270°
        front_points = [p for p in points if p.angle <= 5 or p.angle >= 355]

        front_distances = [p.distance for p in front_points]
        left_distances = [p.distance for p in left_points]
        right_distances = [p.distance for p in right_points]

        if front_distances and min(front_distances) < 30:
            avg_left = sum(left_distances) / len(left_distances) if left_distances else 0
            avg_right = sum(right_distances) / len(right_distances) if right_distances else 0

            if avg_left > avg_right:
                return "turn_left"
            else:
                return "turn_right"
        
        if left_distances and min(left_distances) < 30:
            return "right"
        elif right_distances and min(right_distances) < 30:
            return "left"
        
        return "clear"



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
        elif direction == "right":
            self.pilot.UpdateDirectionCar(1.0)
        time.sleep(0.6)
        self.pilot.UpdateDirectionCar(0.0)

    def drive(self):
        """Boucle principale de conduite autonome"""
        try:
            while True:
                obstacle_status = self.check_obstacles()

                if obstacle_status == "turn_left":
                    self.avoid_obstacle("left")
                    continue
                elif obstacle_status == "turn_right":
                    self.avoid_obstacle("right")
                    continue
                elif obstacle_status == "left" or obstacle_status == "right":
                    self.avoid_obstacle(obstacle_status)
                    continue
                elif obstacle_status == "clear":
                    # On ne vérifie les couleurs que si la voie est libre
                    color_status = self.get_color_status()
                    if color_status == "incorrect":
                        self.turn_around()
                        continue
                    else:
                        self.pilot.UpdateControlCar(0.13)
                        self.pilot.UpdateDirectionCar(0.0)
                else:
                    self.pilot.UpdateControlCar(0.0)
                    print("Aucune donnée LIDAR")

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
