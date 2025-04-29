import pandas as pd
from picamera2 import Picamera2
from libcamera import Transform
import cv2
import numpy as np
import time

class ColorDetector:
    def __init__(self, flip_horizontal=True, flip_vertical=True):
        # Initialisation caméra
        self.picam2 = Picamera2()
        transform = Transform(hflip=flip_horizontal, vflip=flip_vertical)
        config = self.picam2.create_preview_configuration(transform=transform)
        self.picam2.configure(config)
        self.picam2.start()

        # Définition des plages de couleurs en HSV
        self.lower_red1 = np.array([0, 120, 70])
        self.upper_red1 = np.array([2, 255, 255])
        self.lower_red2 = np.array([170, 120, 70])
        self.upper_red2 = np.array([180, 255, 255])
        self.lower_green = np.array([35, 50, 50])
        self.upper_green = np.array([85, 255, 255])

        self.results = []

    def process_frame(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Masques de couleur
        mask_red = cv2.inRange(hsv, self.lower_red1, self.upper_red1) + \
                   cv2.inRange(hsv, self.lower_red2, self.upper_red2)
        mask_green = cv2.inRange(hsv, self.lower_green, self.upper_green)

        height, width = mask_red.shape
        mid_x = width // 2

        # Partie gauche pour le rouge
        red_left = np.sum(mask_red[:, :mid_x] > 0)

        # Partie droite pour le vert
        green_right = np.sum(mask_green[:, mid_x:] > 0)

        return red_left, green_right

    def run_detection(self):
        print("Appuyez sur Ctrl+C pour arrêter...")
        frame_count = 0
        try:
            while True:
                frame = self.picam2.capture_array()
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                red_pixels, green_pixels = self.process_frame(frame)

                frame_count += 1
                self.results.append([frame_count, red_pixels, green_pixels])
                print(f"Frame {frame_count} : Rouge gauche = {red_pixels} px, Vert droite = {green_pixels} px")

                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\nArrêt demandé par l'utilisateur.")

    def save_results(self, filename='out.csv'):
        df = pd.DataFrame(self.results, columns=["Frame", "Red_Left_Pixels", "Green_Right_Pixels"])
        df.to_csv(filename, index=False)
        print(f"Résultats sauvegardés dans '{filename}'.")

    def cleanup(self):
        self.picam2.stop()
        print("Caméra arrêtée.")

# --- Exécution ---
if __name__ == "__main__":
    detector = ColorDetector()
    try:
        detector.run_detection()
    finally:
        detector.save_results('out.csv')
        detector.cleanup()
