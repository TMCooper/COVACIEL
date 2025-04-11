import pandas as pd
from picamera2 import Picamera2
from libcamera import Transform
import cv2
import numpy as np
import time

class ColorDetector:
    def __init__(self, num_frames=10, flip_horizontal=True, flip_vertical=True):
        self.picam2 = Picamera2()
        transform = Transform(hflip=flip_horizontal, vflip=flip_vertical)
        camera_config = self.picam2.create_preview_configuration(transform=transform)
        self.picam2.configure(camera_config)
        self.picam2.start()

        self.num_frames = num_frames

        self.lower_red1 = np.array([0, 120, 70])
        self.upper_red1 = np.array([2, 255, 255])
        self.lower_red2 = np.array([170, 120, 70])
        self.upper_red2 = np.array([180, 255, 255])
        self.lower_green = np.array([35, 50, 50])
        self.upper_green = np.array([85, 255, 255])

        self.results = []

    def process_frame(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        height, width, _ = frame.shape
        mid_x = width // 2

        # Masques rouge et vert
        mask_red = cv2.inRange(hsv, self.lower_red1, self.upper_red1) + \
                   cv2.inRange(hsv, self.lower_red2, self.upper_red2)
        mask_green = cv2.inRange(hsv, self.lower_green, self.upper_green)

        # Moitiés gauche (rouge) et droite (vert)
        left_red_mask = mask_red[:, :mid_x]
        right_green_mask = mask_green[:, mid_x:]

        # Nombre de pixels colorés
        red_pixels_left = np.count_nonzero(left_red_mask)
        green_pixels_right = np.count_nonzero(right_green_mask)

        total_left_pixels = left_red_mask.shape[0] * left_red_mask.shape[1]
        total_right_pixels = right_green_mask.shape[0] * right_green_mask.shape[1]

        # Pourcentages
        red_percent = (red_pixels_left / total_left_pixels) * 100
        green_percent = (green_pixels_right / total_right_pixels) * 100

        # Dominance
        dominance = "Aucune"
        if red_percent >= 80:
            dominance = "Rouge"
        elif green_percent >= 80:
            dominance = "Vert"

        return red_percent, green_percent, dominance

    def run_detection(self):
        print("Début de la détection...")
        for i in range(self.num_frames):
            frame = self.picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            red_pct, green_pct, dominance = self.process_frame(frame)

            self.results.append([i + 1, round(red_pct, 2), round(green_pct, 2), dominance])

            print(f"Capture {i+1}: Rouge ={red_pct:.2f}%, Vert ={green_pct:.2f}%, Dominance={dominance}")

            time.sleep(0.1)

        print("Détection terminée.")

    def save_results(self, filename='out.csv'):
        df = pd.DataFrame(self.results, columns=["Frame", "Red_Left(%)", "Green_Right(%)", "Dominance"])
        df.to_csv(filename, index=False)
        print(f"Résultats sauvegardés dans '{filename}'.")

    def cleanup(self):
        self.picam2.stop()
        print("Caméra arrêtée.")

# --- Exécution ---
if __name__ == "__main__":
    detector = ColorDetector(num_frames=10)
    try:
        detector.run_detection()
        detector.save_results('out.csv')
    finally:
        detector.cleanup()
