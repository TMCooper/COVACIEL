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
        self.pilote = Pilote(0.0, 0.0, 11, 13)  # Pins moteur et direction
        self.camera = ColorDetector(num_frames=1)
        self.lidar = LidarController()
    
    def check_colors(self):
        self.camera.run_detection()
        red_left, green_right = self.camera.results[-1][1], self.camera.results[-1][2]
        return red_left, green_right
    
    def check_obstacles(self):
        measurements = self.lidar.measurements  # Récupérer les mesures du LiDAR
        distances = LidarAngleDistance.get_distances(measurements)
        return distances
    
    def find_best_angle(self):
        best_angle = None
        max_distance = 0
        for angle, distance, _ in self.lidar.measurements:
            if distance > max_distance:
                max_distance = distance
                best_angle = angle
        return best_angle
    
    def navigate(self):
        while True:
            red_left, green_right = self.check_colors()
            distances = self.check_obstacles()
            
            if red_left and green_right:
                print("Couleurs correctes, avancée.")
                self.pilote.adjustSpeed(0.15)
            else:
                print("Couleurs incorrectes, demi-tour.")
                self.pilote.adjustSpeed(0)
                time.sleep(1)
            
            distance_right = distances.get(0)  # Distance à 0°    
            distance_left = distances.get(180)  # Distance à 180°

            obstacle_right = distance_right is not None and distance_right < 5  # 50 cm
            obstacle_left = distance_left is not None and distance_left < 5  # 50 cm
            
            if obstacle_right or obstacle_left:
                best_angle = self.find_best_angle()
                if best_angle is not None:
                    print(f"Obstacle détecté ! Aller vers l'angle {best_angle}°")
                    direction = -0.5 if best_angle > 180 else 0.5
                    #self.pilote.adjustDirection(direction)
                else:
                    print("Aucun bon angle trouvé, arrêt.")
                    self.pilote.adjustSpeed(0.0)
            #else:
                #self.pilote.adjustDirection(0.0)  # Aller tout droit
            
            time.sleep(0.1)  # Pause pour éviter la surcharge CPU

if __name__ == "__main__":
    car = CarController()
    car.navigate()
