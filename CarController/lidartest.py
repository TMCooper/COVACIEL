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

        self.seuil_obstacle = 0.4

    def run(self):
        try:
            self.lidar.start()
            time.sleep(1.5)  # Laisse le temps au LIDAR de se lancer

            while True:
                angle_map = self.lidar.get_angle_map()

                distance_droite = angle_map[90]   # mm
                distance_gauche = angle_map[270]  # mm

                print(f"Distance droite (90°) : {distance_droite} mm")
                print(f"Distance gauche (270°) : {distance_gauche} mm")

                if 0 < distance_droite < self.seuil_obstacle and (distance_gauche < 0 or distance_gauche >= self.seuil_obstacle):
                    print("Obstacle à droite → tourner à gauche")
                    self.pilot.UpdateDirectionCar(-1)
                elif 0 < distance_gauche < self.seuil_obstacle and (distance_droite < 0 or distance_droite >= self.seuil_obstacle):
                    print("Obstacle à gauche → tourner à droite")
                    self.pilot.UpdateDirectionCar(1)
                elif 0 < distance_gauche < self.seuil_obstacle and 0 < distance_droite < self.seuil_obstacle:
                    print("Obstacles des deux côtés → demi-tour")
                    self.pilot.UpdateDirectionCar(-1)
                else:
                    print("Pas d'obstacle → tout droit")
                    self.pilot.UpdateDirectionCar(0)

                # Avance à vitesse constante
                self.pilot.UpdateControlCar(0.15)
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("Arrêt manuel")
            self.pilot.stop()
            self.lidar.stop()

if __name__ == "__main__":
    car = CarController()
    car.run()
