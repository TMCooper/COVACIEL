import time
import os
import sys
import numpy as np 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Pilote.function.Pilote import Pilote
from Camera.class_array import ColorDetector
from Lidar.GPIO import LidarController, LidarAngleDistance

class CarController:
    def __init__(self):
        self.pilote = Pilote(0.0, 0.0, 11, 13)  # Moteur sur GPIO 11, direction sur GPIO 13
        self.camera = ColorDetector(num_frames=1)
        self.lidar = LidarController()
    
    def check_colors(self):
        self.camera.run_detection()
        red_left, green_right = self.camera.results[-1][1], self.camera.results[-1][2]
        return red_left, green_right
    
    def check_obstacles(self):
        measurements = self.lidar.measurements  # Récupération des mesures du LiDAR
        distances = LidarAngleDistance.get_distances(measurements)
        
        distance_right = distances.get(0)  # Distance à 0° (devant)
        distance_left = distances.get(180)  # Distance à 180° (derrière)

        obstacle_right = distance_right is not None and distance_right < 5  # 50 cm
        obstacle_left = distance_left is not None and distance_left < 5  # 50 cm

        return obstacle_right, obstacle_left
    
    def navigate(self):
        while True:
            red_left, green_right = self.check_colors()

            if red_left and green_right:
                print("Couleurs correctes, avancée.")
                self.pilote.adjustSpeed(0.3)
            else:
                print("Couleurs incorrectes, demi-tour.")
                self.pilote.adjustSpeed(0.15)
                time.sleep(1)

            # Vérification des obstacles
            obstacle_right, obstacle_left = self.check_obstacles()

            if obstacle_right:
                print("Obstacle à droite, tourner à gauche.")
                #self.pilote.adjustDirection(-0.5)
            elif obstacle_left:
                print("Obstacle à gauche, tourner à droite.")
                #self.pilote.adjustDirection(0.5)
            else:
                print("Trajet dégagé.")
                #self.pilote.adjustDirection(0.0)

            time.sleep(0.1)  # Pause pour éviter une surcharge CPU

if __name__ == "__main__":
    car = CarController()
    car.navigate()
