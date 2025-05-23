import time
import os
import sys
import RPi.GPIO as gpio
import numpy as np
import cv2

# Ajoute le dossier parent au path pour importer les modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Pilote.function.Pilote import Pilote
from Lidar.Lidar_table_nv.lidar_table_SIG import LidarKit
from typing import List

class CarController:
    def __init__(self):
        self.lidar = LidarKit("/dev/ttyS0", debug=True)
        self.pilot = Pilote(0.0, 0.0, 32, 33, 35)  # Remplace ces pins si besoin
        self.lidar.start()
        self.gain = -1.0
        self.vitesse_avance = 0.13

    def calculer_erreur_laterale(self, g, d):
        if g <= 0: g = 1
        if d <= 0: d = 1
        erreur = (g - d) / (g + d)
        return erreur

    def run(self):
        try:
            while True:
                distances = self.lidar.get_distance_at_angles([270, 90])
                g, d = distances[0], distances[1]

                # Si la distance est invalide (< 0), on met une grande valeur
                g = g if g >= 0 else 10000
                d = d if d >= 0 else 10000

                erreur = self.calculer_erreur_laterale(g, d)
                direction = self.gain * erreur

                print(f"[LiDAR] G: {g:.2f} m | D: {d:.2f} m | e: {erreur:.2f} → Dir: {direction:.1f}")

                if direction < 0:
                    self.pilot.UpdateDirectionCar(1.0)  # Tourne à droite
                else:
                    self.pilot.UpdateDirectionCar(-1.0)  # Tourne à gauche

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
