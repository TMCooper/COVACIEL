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
        time.sleep(2)
        self.gain = -1.0
        self.seuil_obstacle = 0.55
        self.seuil_urgence = 0.2
        self.vitesse_avance = 0.05
        self.history = []  # Historique pour la moyenne mobile

    def calculer_erreur_laterale(self, g, d):
        """Calcule l'erreur latérale en fonction des distances gauche et droite."""
        if g <= 0: g = 1
        if d <= 0: d = 1
        erreur = (g - d) / (g + d)
        return erreur

    def moyenne_mobile(self, valeur):
        """Calcule la moyenne mobile pour lisser les données."""
        self.history.append(valeur)
        if len(self.history) > 5:  # Utilise les 5 dernières valeurs
            self.history.pop(0)
        return np.mean(self.history)

    def run(self):
        """Boucle principale pour contrôler la voiture."""
        self.lidar.start()
        time.sleep(2)
        try:
            while True:
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
                direction = self.moyenne_mobile(self.gain * erreur)  # Utilise la moyenne mobile

                # Détection d'obstacle devant à 0°
                if front < self.seuil_obstacle:
                    if (g + g_320) < (d + d_40):
                        self.pilot.UpdateCar(1, -1)  # Tourne à droite
                    else:
                        self.pilot.UpdateCar(1, 1)  # Tourne à gauche
                else:
                    if direction < -0.1:
                        self.pilot.UpdateCar(1, -1)  # Tourne à droite
                    elif direction > 0.1:
                        self.pilot.UpdateCar(1, 1)  # Tourne à gauche
                    else:
                        self.pilot.UpdateCar(1, 0)  # Tout droit

                self.pilot.UpdateCar(0, self.vitesse_avance)

                time.sleep(0.1)

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
