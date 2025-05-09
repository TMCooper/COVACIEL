import time
import os
import sys
import RPi.GPIO as gpio
import numpy as np
import cv2
from threading import Thread

# Ajoute le chemin parent au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Camera.test_capture_color import ColorDetector
from Pilote.function.Pilote import Pilote
from Lidar.Lidar_table_nv.lidar_table_SIG import LidarKit  # nouvelle version

class CarController:
    def __init__(self):
        self.camera = ColorDetector()
        self.lidar  = LidarKit("/dev/ttyS0", debug=True)
        self.pilot  = Pilote(0.0, 0.0, 32, 33)

        # Démarrage du LIDAR
        self.lidar.start()

    def get_color_status(self):
        """Analyse les couleurs détectées et retourne 'correct' ou 'incorrect'."""
        frame = self.camera.picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        red_left_pct, green_right_pct, _ = self.camera.process_frame(frame)

        left  = "red"   if red_left_pct   > 5 else "none"
        right = "green" if green_right_pct > 5 else "none"
        return "correct" if (left=="red" and right=="green") else "incorrect"

    def check_obstacles(self):
        """Utilise le tableau angle→distance pour décider de la trajectoire."""
        amap = self.lidar.get_angle_map()
        # pas encore de données ?
        if all(d < 0 for d in amap):
            return None

        # zones avant / gauche / droite (en m)
        front = [amap[a]/1000.0 for a in range(0,21)]   + [amap[a]/1000.0 for a in range(340,360)]
        left  = [amap[a]/1000.0 for a in range(240,301)]
        right = [amap[a]/1000.0 for a in range(60,121)]

        # filtrer valeurs valides
        front = [d for d in front  if d >= 0]
        left  = [d for d in left   if d >= 0]
        right = [d for d in right  if d >= 0]

        front_clear = all(d > 3.5 for d in front) if front else False
        left_avg     = sum(left)  / len(left)  if left  else float('inf')
        right_avg    = sum(right) / len(right) if right else float('inf')

        if not front_clear:
            return "left" if left_avg > right_avg else "right"
        return "clear"

    def turn_around(self):
        """Demi-tour en cas de mauvaise détection couleur."""
        print("Mauvaise couleur détectée. Demi-tour...")
        self.pilot.UpdateControlCar(-1)
        time.sleep(0.8)
        self.pilot.UpdateDirectionCar(1)
        time.sleep(1.2)
        self.pilot.UpdateControlCar(0.0)
        self.pilot.UpdateDirectionCar(0.0)

    def avoid_obstacle(self, direction):
        """Evitement d’un obstacle à gauche ou à droite."""
        print(f"Obstacle détecté. Évitement vers {direction}.")
        self.pilot.UpdateControlCar(0.13)
        self.pilot.UpdateDirectionCar(1 if direction=="left" else -1)
        time.sleep(0.6)
        self.pilot.UpdateDirectionCar(0.0)

    def drive(self):
        """Boucle principale de conduite autonome."""
        try:
            while True:
                # 1) Gestion de la couleur
                if self.get_color_status() == "incorrect":
                    self.turn_around()
                    continue

                # 2) Gestion des obstacles
                obs = self.check_obstacles()
                if obs == "clear":
                    self.pilot.UpdateControlCar(0.25)
                    self.pilot.UpdateDirectionCar(0.0)
                elif obs in ("left","right"):
                    self.avoid_obstacle(obs)
                else:
                    # pas encore de données
                    self.pilot.UpdateControlCar(0.0)
                    print("Attente données LiDAR…")

                time.sleep(0.1)

        except KeyboardInterrupt:
            # Arrêt propre
            self.stop()

    def stop(self):
        """Arrête tout et libère les GPIO."""
        print("Arrêt du contrôleur…")
        self.pilot.stop()
        self.lidar.stop()
        self.camera.picam2.stop()
        gpio.cleanup()

if __name__ == "__main__":
    car = CarController()
    car.drive()
