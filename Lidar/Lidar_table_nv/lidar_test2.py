import time
from lidar_table_SIG import LidarKit  # Vérifie que lidar_table.py est bien le nom du fichier

lidar = LidarKit()
lidar.start()

try:
    while True:
        distances = lidar.get_distance_at_angles([0, 90, 270])
        print(f"0°: {distances[0]:.2f} m | 90°: {distances[1]:.2f} m | 270°: {distances[2]:.2f} m")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Arrêt utilisateur.")
finally:
    lidar.stop()
