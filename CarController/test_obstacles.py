import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Pilote.function.Pilote import Pilote
from Lidar.Lidar_table_nv.lidar_SIG import LidarKit

import time
import RPi.GPIO as gpio
import numpy as np


class CarController:
    def __init__(self):
        self.pilote = Pilote(motor_pin=32, servo_pin=33)
        self.lidar = LidarKit(port="/dev/ttyS0", baudrate=230400, debug=False)
        self.lidar.start()

    def check_distances(self):
        """Lit les distances à gauche (90°), droite (270°) et face (0°)"""
        angle_map = self.lidar.get_angle_map()

        def valid_cm(angle):
            mm = angle_map[angle]
            return mm / 10 if 20 < mm < 2000 else 999.0  # En cm, valeurs aberrantes ignorées

        left = valid_cm(90)
        right = valid_cm(270)
        front = valid_cm(0)

        return left, right, front

    def run(self):
        try:
            while True:
                left, right, front = self.check_distances()
                print(f"[LIDAR] Left: {left:.1f} cm | Right: {right:.1f} cm | Front: {front:.1f} cm")

                if front < 25:
                    print("🛑 Obstacle en face → arrêt immédiat")
                    self.pilote.adjustSpeed(0.0)
                    self.pilote.changeDirection(0.0)

                elif right < 30:
                    print("➡️ Obstacle à droite → tourner à gauche")
                    self.pilote.changeDirection(-0.5)
                    self.pilote.adjustSpeed(0.3)

                elif left < 30:
                    print("⬅️ Obstacle à gauche → tourner à droite")
                    self.pilote.changeDirection(0.5)
                    self.pilote.adjustSpeed(0.3)

                else:
                    print("✅ Route libre → avancer tout droit")
                    self.pilote.changeDirection(0.0)
                    self.pilote.adjustSpeed(0.5)

                time.sleep(0.1)

        except KeyboardInterrupt:
            print("Arrêt manuel du programme.")
        finally:
            self.lidar.stop()
            self.pilote.adjustSpeed(0)
            print("Système arrêté proprement.")


    def stop(self):
        self.pilot.stop()
        self.lidar.stop()
        gpio.cleanup()
        print("🛑 Contrôleur arrêté proprement.")


if __name__ == "__main__":
    car = CarController()
    car.drive()
