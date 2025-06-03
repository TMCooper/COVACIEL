import time
import os
import sys
import RPi.GPIO as gpio
import numpy as np
import cv2
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Pilote.function.Pilote import Pilote
from Lidar.Lidar_table_nv.lidar_table_SIG import LidarKit
from Camera.test_capture_color import ColorDetector

class CarController:
    def __init__(self):
        self.lidar = LidarKit("/dev/ttyS0", debug=True)
        self.pilot = Pilote(0.0, 0.0, 32, 33, 35)
        self.color_detector = ColorDetector()
        self.lidar.start()  # Démarre le LiDAR ici
        time.sleep(2)  # Ajoute un délai pour permettre au LiDAR de démarrer correctement
        self.gain = -1.0
        self.seuil_obstacle = 0.55
        self.seuil_urgence = 0.2
        self.vitesse_avance = 0.05
        self.history = []
        self.running = True

    def calculer_erreur_laterale(self, g, d):
        """Calcule l'erreur latérale en fonction des distances gauche et droite."""
        if g <= 0: g = 1
        if d <= 0: d = 1
        erreur = (g - d) / (g + d)
        return erreur

    def moyenne_mobile(self, valeur):
        """Calcule la moyenne mobile pour lisser les données."""
        self.history.append(valeur)
        if len(self.history) > 5:
            self.history.pop(0)
        return np.mean(self.history)

    def get_color_status(self):
        """Analyse les couleurs détectées et retourne un état."""
        frame = self.color_detector.picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        red_left_pct, green_right_pct, _ = self.color_detector.process_frame(frame)

        left_color = "red" if red_left_pct > 5 else "none"
        right_color = "green" if green_right_pct > 5 else "none"

        if left_color == "red" and right_color == "green":
            return "correct"
        elif left_color == "green" and right_color == "red":
            return "inverted"
        else:
            return "single_color"

    def run(self):
        """Boucle principale pour contrôler la voiture."""
        try:
            while self.running:
                angle_map = self.lidar.get_angle_map()

                # Accéder aux distances pour les angles spécifiques
                g = angle_map[270] if 270 < len(angle_map) else 10000
                d = angle_map[90] if 90 < len(angle_map) else 10000
                front = angle_map[0] if 0 < len(angle_map) else 10000
                g_320 = angle_map[320] if 320 < len(angle_map) else 10000
                d_40 = angle_map[40] if 40 < len(angle_map) else 10000

                # Assure-toi que les valeurs ne sont pas négatives
                g = max(g, 0)
                d = max(d, 0)
                front = max(front, 0)
                g_320 = max(g_320, 0)
                d_40 = max(d_40, 0)

                # Calcul de l'erreur latérale en utilisant les angles supplémentaires
                erreur = self.calculer_erreur_laterale(g + g_320, d + d_40)
                direction = self.moyenne_mobile(self.gain * erreur)

                # Vérification de l'état des couleurs
                color_status = self.get_color_status()
                if color_status == "inverted":
                    print("Couleurs inversées, demi-tour")
                    self.pilot.UpdateCar(1, -1)
                    time.sleep(2)
                    continue

                # Détection d'obstacle devant à 0°
                if front < self.seuil_obstacle:
                    if (g + g_320) < (d + d_40):
                        print("Tourne à droite pour éviter l'obstacle")
                        self.pilot.UpdateCar(1, -1)
                    else:
                        print("Tourne à gauche pour éviter l'obstacle")
                        self.pilot.UpdateCar(1, 1)
                else:
                    if direction < -0.1:
                        print("Ajustement à droite")
                        self.pilot.UpdateCar(1, -1)
                    elif direction > 0.1:
                        print("Ajustement à gauche")
                        self.pilot.UpdateCar(1, 1)
                    else:
                        print("Tout droit")
                        self.pilot.UpdateCar(1, 0)

                # Maintien de la vitesse constante
                self.pilot.UpdateCar(0, self.vitesse_avance)

                time.sleep(0.1)

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Arrête la voiture et nettoie les ressources."""
        self.running = False
        self.pilot.stop()
        self.lidar.stop()
        self.color_detector.stop()
        print("Contrôleur arrêté.")

if __name__ == "__main__":
    car = CarController()
    car.run()
