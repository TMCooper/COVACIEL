import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Pilote.function.Pilote import Pilote
from Lidar.Lidar_table_nv.lidar_table_SIG import LidarKit

import time
import RPi.GPIO as gpio
import numpy as np

class CarController:
    def __init__(self):
        self.lidar = LidarKit("/dev/ttyS0", debug=True)
        self.pilot = Pilote(0.0, 0.0, 32, 33)
        self.lidar.start()

    def check_obstacles(self):
        """Utilise les angles clés : 0 (devant), 30, 90 (gauche), 270 (droite), 330."""
        points = self.lidar.get_points()
        if not points:
            return None

        angle_dist = {0: None, 30: None, 90: None, 270: None, 330: None}

        for p in points:
            angle = round(p["angle"])  # ✅ dictionnaire, pas attribut
            if angle in angle_dist:
                if angle_dist[angle] is None:
                    angle_dist[angle] = p["distance"]
                else:
                    angle_dist[angle] = min(angle_dist[angle], p["distance"])

    # Valeurs par défaut si aucun point
        center = angle_dist[0] if angle_dist[0] is not None else 999.0
        left = angle_dist[90] if angle_dist[90] is not None else 999.0
        right = angle_dist[270] if angle_dist[270] is not None else 999.0
        front_left = angle_dist[30] if angle_dist[30] is not None else 999.0
        front_right = angle_dist[330] if angle_dist[330] is not None else 999.0

        return left, right, front_left, front_right, center


    def avoid_obstacle(self, direction):
        """Évite un obstacle en tournant légèrement."""
        print(f"🔁 Obstacle devant → Évitement à {direction}")
        self.pilot.UpdateControlCar(0.10)
        if direction == "left":
            self.pilot.UpdateDirectionCar(-1.0)
        else:
            self.pilot.UpdateDirectionCar(1.0)
        time.sleep(0.5)
        self.pilot.UpdateDirectionCar(0.0)
        time.sleep(0.3)

    def drive(self):
        try:
            while True:
                check = self.check_obstacles()
                if check is None:
                    print("⚠️ Aucune donnée LiDAR")
                    self.pilot.UpdateControlCar(0.0)
                    time.sleep(0.1)
                    continue

                left, right, front_left, front_right, center = check
                front = min(front_left, front_right, center)

                print(f"[LIDAR] Front: {front:.1f} cm | Left: {left:.1f} cm | Right: {right:.1f} cm")

                # 🟥 Obstacle très proche devant : recule
                if front < 0.20:
                    print("🚨 Obstacle trop proche ! Recul...")
                    self.pilot.UpdateControlCar(-1.0)
                    time.sleep(0.4)
                    self.pilot.UpdateControlCar(0.0)
                    continue

            # 🟧 Obstacle modéré devant : choisir le côté le plus ouvert
                elif front < 0.35:
                    print("🟠 Obstacle devant → évitement")
                    self.pilot.UpdateControlCar(0.13)
                    if left > right:
                        self.pilot.UpdateDirectionCar(-1.0)  # Va à gauche
                    else:
                        self.pilot.UpdateDirectionCar(1.0)   # Va à droite
                    time.sleep(0.4)
                    self.pilot.UpdateDirectionCar(0.0)
                    continue

            # 🟨 Trop proche d’un mur à droite → va à gauche
                elif right < 20:
                    print("➡️ Trop à droite → correction vers la gauche")
                    self.pilot.UpdateControlCar(0.13)
                    self.pilot.UpdateDirectionCar(-1.0)
                    time.sleep(0.3)
                    self.pilot.UpdateDirectionCar(0.0)
                    continue

            # 🟨 Trop proche d’un mur à gauche → va à droite
                elif left < 20:
                    print("⬅️ Trop à gauche → correction vers la droite")
                    self.pilot.UpdateControlCar(0.13)
                    self.pilot.UpdateDirectionCar(1.0)
                    time.sleep(0.3)
                    self.pilot.UpdateDirectionCar(0.0)
                    continue

            # ✅ Route libre → tout droit
                else:
                    print("✅ Route libre → Avancer tout droit")
                    self.pilot.UpdateControlCar(0.13)
                    self.pilot.UpdateDirectionCar(0.0)

                time.sleep(0.1)

        except KeyboardInterrupt:
            self.stop()


    def stop(self):
        """Arrête tous les composants proprement"""
        self.pilot.stop()
        self.lidar.stop()
        gpio.cleanup()
        print("🛑 Contrôleur arrêté proprement.")


if __name__ == "__main__":
    car = CarController()
    car.drive()
