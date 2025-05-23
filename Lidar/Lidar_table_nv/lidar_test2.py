import time
from lidar_table_SIG import LidarKit  # Vérifie que lidar_table.py est bien le nom du fichier

def main():
    lidar = LidarKit(port="/dev/ttyS0", baudrate=230400, debug=False)

    try:
        print("Démarrage du LIDAR...")
        lidar.start()
        time.sleep(2)  # Laisse le temps au LIDAR de se stabiliser

        while True:
            distances = lidar.get_distance_at_angles([0, 90])

            dist_0 = distances[0]
            dist_90 = distances[1]

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
