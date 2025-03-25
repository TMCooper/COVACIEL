import time
from camera_module import ColorDetector
from lidar_module import LidarController
from pilote_module import Pilote

class CarController:
    def __init__(self):
        self.camera = ColorDetector(num_frames=10)
        self.lidar = LidarController()
        self.pilote = Pilote(0.0, 0.0, 11, 13)
    
    def run(self):
        try:
            print("Démarrage du contrôleur principal...")
            
            while True:
                # Capture et traitement des données de la caméra
                frame = self.camera.picam2.capture_array()
                frame = self.camera.process_frame(frame, frame.shape[1] // 2)
                red_left, green_right = frame
                
                # Analyse des données du LiDAR
                obstacles = self.lidar.get_obstacles()
                
                # Logique de prise de décision
                if red_left:
                    print("Bord rouge détecté à gauche, correction de trajectoire...")
                    self.pilote.changeDirection(-10)
                elif green_right:
                    print("Bord vert détecté à droite, correction de trajectoire...")
                    self.pilote.changeDirection(10)
                
                if obstacles:
                    print("Obstacle détecté, freinage...")
                    self.pilote.applyBrakes(True)
                else:
                    self.pilote.applyBrakes(False)
                    self.pilote.adjustSpeed(30)  # Ajustement de la vitesse
                
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Arrêt du programme...")
            self.camera.cleanup()
            self.lidar.stop()
            
if __name__ == "__main__":
    car = CarController()
    car.run()
