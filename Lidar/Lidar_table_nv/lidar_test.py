from lidar_SIG import LidarKit
import time

PORT = "/dev/ttyS0"  # adapte à ton port réel
BAUDRATE = 230400
DEBUG = False

# Angles cibles exacts
TARGET_ANGLES = {0, 90, 180}

lidar = LidarKit(port=PORT, baudrate=BAUDRATE, debug=DEBUG)

try:
    print("[INFO] Lecture en temps réel sur angles 0, 90, 180...")

    lidar.start()

    while True:
        points = lidar.get_points()
        if points:
            for pt in points:
                angle_int = int(pt['angle'])  # arrondi au degré entier
                if angle_int in TARGET_ANGLES:
                    print(f"{angle_int}° : {int(pt['distance'] * 1000)} mm")
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n[INFO] Arrêt demandé par l'utilisateur.")

finally:
    lidar.stop()
    print("[INFO] LIDAR arrêté.")
