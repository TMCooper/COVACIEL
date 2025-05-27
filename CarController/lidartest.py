import time
import os
import sys
import RPi.GPIO as gpio
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Pilote.function.Pilote import Pilote
from Lidar.Lidar_table_nv.lidar_table_SIG import LidarKit

class CarController:
    def __init__(self):
        self.lidar = LidarKit("/dev/ttyS0" , debug=True)
        # self.pilot = Pilote(0.0, 0.0, 32, 33, 35)
        self.lidar.start()
        self.gain = -1.0
        self.vitesse_avance = 0.5

    def calculer_erreur_laterale(self, g, d):
        if g <= 0: g = 1
        if d <= 0: d = 1
        erreur = (g - d) / (g + d)  # ou ((G / (G + D)) * 2) - 1
        return erreur

    def run(self):
        try:
            while True:
                t0 = time.time()
                distances = self.lidar.get_distance_at_angles([270, 90])
                g, d = distances

                g = max(g, 0)
                d = max(d, 0)

                erreur = self.calculer_erreur_laterale(g, d)
                direction = self.gain * erreur

                print(f"90°: {d:.2f} m | 270°: {g:.2f} m | erreur: {erreur:.3f} | direction: {direction:.3f}")

                # --- Désactivé temporairement pour tester la latence LiDAR uniquement ---
                # if direction < 0:
                #     self.pilot.UpdateDirectionCar(-1.0)
                # else: 
                #     self.pilot.UpdateDirectionCar(1.0)
                # self.pilot.UpdateControlCar(self.vitesse_avance)

                time.sleep(0.1)  # comme dans ton test sans latence
                print(f"⏱️ Loop duration: {time.time() - t0:.3f}s")

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        # self.pilot.stop()  # Commenté temporairement
        self.lidar.stop()
        gpio.cleanup()
        print("Contrôleur arrêté.")

if __name__ == "__main__":
    car = CarController()
    car.run()