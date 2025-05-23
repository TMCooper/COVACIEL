import time
import os
import sys
import RPi.GPIO as gpio
import numpy as np
import cv2

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Pilote.function.Pilote import Pilote
from Lidar.Lidar_table_nv.lidar import LidarKit

class CarController:
    def __init__(self):
        self.lidar = LidarKit("/dev/ttyS0" , debug=True)
        self.pilot = Pilote(0.0, 0.0, 32, 33, 35)
        self.lidar.start()
        self.gain = -1.0
        self.vitesse_avance = 0.13

    def calculer_erreur_laterale(self, g, d):
        if g <= 0: g = 1
        if d <= 0: d = 1
        erreur = (g - d) / (g + d)  # ou ((G / (G + D)) * 2) - 1
        return erreur


    def run(self):
        self.lidar.start()
        try:
            while True:
                angle_map = self.lidar.get_angle_map()

                # Accéder aux distances pour les angles spécifiques
                g = angle_map[270] if 270 < len(angle_map) else 10000
                d = angle_map[90] if 90 < len(angle_map) else 10000

                # Assure-toi que les valeurs ne sont pas négatives
                g = max(g, 0)
                d = max(d, 0)

                erreur = self.calculer_erreur_laterale(g, d)
                direction = self.gain * erreur  # K * e
                print(direction)

                print(f"[LiDAR] G: {g} m | D: {d} m | e: {erreur:.2f} → Dir: {direction:.1f}")

                # Assure-toi que changeDirection est appelée correctement
                self.pilot.UpdateDirectionCar(direction)
                self.pilot.UpdateControlCar(self.vitesse_avance)

                time.sleep(0.1)

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.pilot.stop()
        self.lidar.stop()
        gpio.cleanup()
        print("Contrôleur arrêté.")

if __name__ == "__main__":
    car = CarController()
    car.run()