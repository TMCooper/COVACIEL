import pandas as pd
from picamera2 import Picamera2
from libcamera import Transform
import cv2
import numpy as np
import time

class ColorDetector:
    def __init__(self, flip_horizontal=True, flip_vertical=True):
        # Initialisation de la caméra
        self.picam2 = Picamera2()
        transform = Transform(hflip=flip_horizontal, vflip=flip_vertical)
        camera_config = self.picam2.create_preview_configuration(transform=transform)
        self.picam2.configure(camera_config)
        self.picam2.start()

        # Plages HSV pour le rouge et le vert
        self.lower_red1 = np.array([0, 120, 70])
        self.upper_red1 = np.array([2, 255, 255])
        self.lower_red2 = np.array([170, 120, 70])
        self.upper_red2 = np.array([180, 255, 255])
        self.lower_green = np.array([35, 50, 50])
        self.upper_green = np.array([85, 255, 255])

        self.results = []

    def process_frame(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask_red = cv2.inRange(hsv, self.lower_red1, self.upper_red1) + \
                   cv2.inRange(hsv, self.lower_red2, self.upper_red2)
        mask_green = cv2.inRange(hsv, self.lower_green, self.upper_green)

        height, width = mask_red.shape
        mid_x = width // 2

        left_area = height * mid_x
        right_area = height * (width - mid_x)

        red_left = np.sum(mask_red[:, :mid_x] > 0)
        red_right = np.sum(mask_red[:, mid_x:] > 0)
        green_right = np.sum(mask_green[:, mid_x:] > 0)
        green_left = np.sum(mask_green[:, :mid_x] > 0)

        red_left_pct = (red_left / left_area) * 100
        green_right_pct = (green_right / right_area) * 100

        warning = ""
        if red_right > 0.05 * right_area:
            warning += "Rouge à droite "
        if green_left > 0.05 * left_area:
            warning += "Vert à gauche"

        return red_left_pct, green_right_pct, warning.strip()

    def run_detection(self):
        print("Appuyez sur 'q' pour arrêter.")
        frame_count = 0

        try:
            while True:
                frame = self.picam2.capture_array()
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                red_pct, green_pct, warning = self.process_frame(frame)
                frame_count += 1

                self.results.append([
                    frame_count,
                    round(red_pct, 2),
                    round(green_pct, 2),
                    warning
                ])

                print(f"Frame {frame_count} : Rouge gauche = {red_pct:.2f}%, Vert droite = {green_pct:.2f}%"
                      + (f" | ⚠️ {warning}" if warning else ""))

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Arrêt demandé.")
                    break

                time.sleep(0.1)
        finally:
            self.picam2.stop()
            print("Caméra arrêtée.")

    def save_results(self, filename='out.csv'):
        df = pd.DataFrame(self.results, columns=["Frame", "Red_Left_%", "Green_Right_%", "Warning"])
        df.to_csv(filename, index=False)
        print(f"Résultats sauvegardés dans '{filename}'.")

# --- Exécution ---
if __name__ == "__main__":
    detector = ColorDetector()
    detector.run_detection()
    detector.save_results()
