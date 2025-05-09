# example_minimal.py

from c_lidar import LidarKit
import time

def main():
    # 1) Instanciation
    lidar = LidarKit(port="/dev/ttyS0", baudrate=230400, timeout=0.01, debug=True)

    # 2) Démarrage du thread de lecture
    lidar.start()

    try:
        while True:
            # 3a) Récupérer la carte angulaire (360 valeurs en mm)
            angle_map = lidar.get_angle_map()
            # Exemple : afficher la distance à 0°, 90°, 180°, 270°
            print(f"0°: {angle_map[0]:.0f} mm, "
                  f"90°: {angle_map[90]:.0f} mm, "
                  f"180°: {angle_map[180]:.0f} mm, "
                  f"270°: {angle_map[270]:.0f} mm")

            # 3b) (Optionnel) récupérer les nouveaux points structurés
            points = lidar.get_points()
            for p in points:
                # ex. afficher le premier point reçu
                print(f"Point → angle {p.angle:.1f}°, dist {p.distance:.3f} m, conf {p.confidence}")
                break

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("⇨ Arrêt demandé par l'utilisateur")

    finally:
        # 4) Arrêt propre
        lidar.stop()
        print("⇨ LIDAR arrêté")

if __name__ == "__main__":
    main()

 #un exemple minimaliste