import time
import os
import sys
import numpy as np 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Pilote.function.Pilote import Pilote
from Camera.class_array import ColorDetector
# from Lidar.lidar_test.lidar_code_restruct import LidarController

class CarController:
    def __init__(self):
        self.pilote = Pilote(1, 0.0, 11, 13)  # Départ à 30% de vitesse
        self.camera = ColorDetector(num_frames=1)
        # self.lidar = LidarController()

    def check_colors(self):
        self.camera.run_detection()
        red_left, green_right = self.camera.results[-1][1], self.camera.results[-1][2]
        return red_left, green_right

    def check_obstacles(self):
        # return self.lidar.get_best_angle()
        return None  # Simulation pour éviter les erreurs

    def navigate(self):
        print("Démarrage de la navigation...")
        self.pilote.adjustSpeed(0.8)  # Démarre avec une vitesse de 30%
        
        while True:
            red_left, green_right = self.check_colors()

            if red_left and green_right:
                print("✅ Couleurs correctes")
                self.pilote.adjustSpeed(0.8)  # Maintien la vitesse
            else:
                print("❌ Couleurs incorrectes, demi-tour.")
                self.pilote.adjustSpeed(0.8)  # Reculer légèrement
                time.sleep(0.5)  # Juste un court instant
                self.pilote.adjustSpeed(0.8)  # Repartir après correction
            
            # Détection d'obstacle
            best_angle = self.check_obstacles()
            if best_angle is not None:
                if best_angle < -10:
                    print("🛑 Obstacle à droite, tourner à gauche.")
                    self.pilote.direction = 0.8
                elif best_angle > 10:
                    print("🛑 Obstacle à gauche, tourner à droite.")
                    self.pilote.direction = 0.8
                else:
                    self.pilote.direction = 0.0  # Droit si pas d'obstacle

            time.sleep(0.1)  # Pause pour éviter surcharge CPU

if __name__ == "__main__":
    car = CarController()
    car.navigate()