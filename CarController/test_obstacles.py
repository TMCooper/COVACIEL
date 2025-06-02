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
        self.lidar = LidarKit("/dev/ttyS0", debug=True)
        self.pilot = Pilote(0.0, 0.0, 32, 33, 35)
        self.lidar.start()
        self.gain = -1.0
        self.seuil_obstacle = 0.8
        self.seuil_urgence = 0.35
        self.vitesse_avance = 0.05

    def calculer_erreur_laterale(self, g, d):
        """Calcule l'erreur latérale en fonction des distances gauche et droite."""
        if g <= 0: g = 1
        if d <= 0: d = 1
        erreur = (g - d) / (g + d)
        return erreur

    def run(self):
        """Boucle principale pour contrôler la voiture."""
        self.lidar.start()
        try:
            while True:
                angle_map = self.lidar.get_angle_map()

                # Accéder aux distances pour les angles spécifiques
                g = angle_map[270] if 270 < len(angle_map) else 10000
                d = angle_map[90] if 90 < len(angle_map) else 10000
                front = angle_map[0] if 0 < len(angle_map) else 10000  # Distance devant la voiture à 0°
                g_320 = angle_map[320] if 320 < len(angle_map) else 10000  # Distance à 320°
                d_40 = angle_map[40] if 40 < len(angle_map) else 10000  # Distance à 40°

                # Assure-toi que les valeurs ne sont pas négatives
                g = max(g, 0)
                d = max(d, 0)
                front = max(front, 0)
                g_320 = max(g_320, 0)
                d_40 = max(d_40, 0)

                # Calcul de l'erreur latérale en utilisant les angles supplémentaires
                erreur = self.calculer_erreur_laterale(g + g_320, d + d_40)
                direction = self.gain * erreur  # K * e

                # Détection d'obstacle devant à 0°
                if front < self.seuil_obstacle:  # Seuil de distance pour détecter un obstacle devant
                    if (g + g_320) < (d + d_40):
                        # Si l'obstacle est plus proche à gauche, tourne à droite
                        self.pilot.UpdateCar(1, -1)
                    else:
                        # Sinon, tourne à gauche
                        self.pilot.UpdateCar(1, 1)
                else:
                    # Sinon, ajuste la direction en fonction de l'erreur latérale
                    if direction < 0:
                        self.pilot.UpdateCar(1, -1)
                    else:
                        self.pilot.UpdateCar(1, 1)

                self.pilot.UpdateCar(0, self.vitesse_avance)  # Vitesse constante

                time.sleep(0.1)  # Réduire le temps de sommeil pour diminuer la latence

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Arrête la voiture et nettoie les ressources."""
        self.lidar.stop()
        self.pilot.stop()
        print("Contrôleur arrêté.")

if __name__ == "__main__":
    car = CarController()
    car.run()
