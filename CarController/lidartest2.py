import time
import os
import sys
import RPi.GPIO as gpio

# Ajouter le dossier parent au path pour importer les modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Pilote.function.Pilote import Pilote
from Lidar.Lidar_table_nv.lidar_table_SIG import LidarKit

class CarController:
    def __init__(self):
        self.lidar = LidarKit("/dev/ttyS0", debug=True)
        self.pilot = Pilote(0.0, 0.0, 32, 33, 35)
        self.gain = -1.0
        self.vitesse_avance = 0.13
        self.lidar.start()

    def calculer_erreur_laterale(self, g, d):
        if g <= 0: g = 1
        if d <= 0: d = 1
        erreur = (g - d) / (g + d)
        return erreur

    def run(self):
        try:
            while True:
                # Utilisation directe de la méthode get_distance_at_angles
                distances = self.lidar.get_distance_at_angles([270, 90])
                g, d = distances[0], distances[1]

                # Affichage pour vérification
                print(f"Gauche (270°) : {g:.2f} m | Droite (90°) : {d:.2f} m")

                # Remplacement des valeurs invalides
                g = max(g, 0)
                d = max(d, 0)

                erreur = self.calculer_erreur_laterale(g, d)
                direction = self.gain * erreur

                print(f"Erreur : {erreur:.2f} → Direction : {direction:.1f}")

                if direction < 0:
                    self.pilot.UpdateDirectionCar(-1.0)  # Tourner à droite
                else:
                    self.pilot.UpdateDirectionCar(1.0)   # Tourner à gauche

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
