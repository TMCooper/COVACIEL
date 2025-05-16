import time
import os
import sys
import RPi.GPIO as gpio
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Pilote.function.Pilote import Pilote
from Lidar.Lidar_table_nv.lidar_table_SIG import LidarKit

class LidarOnlyNavigator:
    def __init__(self):
        self.lidar = LidarKit("/dev/ttyS0", debug=True)
        self.pilot = Pilote(0.0, 0.0, 32, 33)
        self.lidar.start()

    def get_lidar_readings(self):
        """Retourne la distance moyenne à 0°, 90° et 270°"""
        points = self.lidar.get_points()
        if not points:
            return None

        get_avg = lambda a_min, a_max: np.mean([
            p.distance for p in points 
            if a_min <= p.angle <= a_max and p.distance < 300
        ]) if any(a_min <= p.angle <= a_max for p in points) else 999

        front = get_avg(355, 360) + get_avg(0, 5)
        front /= 2
        left = get_avg(85, 95)
        right = get_avg(265, 275)

        return front, left, right

    def back_and_turn(self):
        print("⚠️ Blocage total détecté. Recul et rotation.")
        self.pilot.UpdateControlCar(-1.0)
        time.sleep(0.6)
        self.pilot.UpdateDirectionCar(1.0)
        self.pilot.UpdateControlCar(0.2)
        time.sleep(0.8)
        self.pilot.UpdateControlCar(0.0)
        self.pilot.UpdateDirectionCar(0.0)

    def drive(self):
        try:
            while True:
                lidar_data = self.get_lidar_readings()
                if lidar_data is None:
                    print("❌ Aucune donnée LiDAR.")
                    self.pilot.UpdateControlCar(0.0)
                    time.sleep(0.1)
                    continue

                front, left, right = lidar_data
                print(f"[LIDAR] Front: {front:.1f} cm | Left: {left:.1f} cm | Right: {right:.1f} cm")

                if front < 30:
                    if left > right and left > 20:
                        print("🔁 Obstacle devant → Évitement à gauche")
                        self.pilot.UpdateControlCar(0.13)
                        self.pilot.UpdateDirectionCar(-1.0)
                    elif right >= left and right > 20:
                        print("🔁 Obstacle devant → Évitement à droite")
                        self.pilot.UpdateControlCar(0.13)
                        self.pilot.UpdateDirectionCar(1.0)
                    else:
                        self.back_and_turn()
                    time.sleep(0.5)
                    self.pilot.UpdateDirectionCar(0.0)
                else:
                    print("✅ Route libre → Avancer")
                    self.pilot.UpdateControlCar(0.13)
                    self.pilot.UpdateDirectionCar(0.0)

                time.sleep(0.1)

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.pilot.stop()
        self.lidar.stop()
        gpio.cleanup()
        print("Arrêt du système.")

if __name__ == "__main__":
    bot = LidarOnlyNavigator()
    bot.drive()
