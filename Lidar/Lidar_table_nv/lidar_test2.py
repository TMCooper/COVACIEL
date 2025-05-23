import time
from lidar import LidarKit  # Assure-toi que lidar.py est dans le même dossier

def main():
    lidar = LidarKit(port="/dev/ttyS0", baudrate=230400, debug=False)  # Change le port si besoin

    try:
        print("Démarrage du LIDAR...")
        lidar.start()
        time.sleep(2)  # Laisse le temps au LIDAR de se stabiliser

        while True:
            angle_map = lidar.get_angle_map()

            dist_0 = angle_map[0]
            dist_90 = angle_map[90]

            if dist_0 > 0:
                print(f"Angle 0°: {dist_0:.2f} m", end=' | ')
            else:
                print("Angle 0°: ---", end=' | ')

            if dist_90 > 0:
                print(f"Angle 90°: {dist_90:.2f} m")
            else:
                print("Angle 90°: ---")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nArrêt demandé par l'utilisateur.")

    finally:
        lidar.stop()
        print("LIDAR arrêté.")

if __name__ == "__main__":
    main()
