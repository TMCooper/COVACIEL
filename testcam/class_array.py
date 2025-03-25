import pandas as pd
from picamera2 import Picamera2
from libcamera import Transform
import cv2
import numpy as np
import time

class ColorDetector:
    def __init__(self, num_frames=10, flip_horizontal=True, flip_vertical=True):
        # Initialisation caméra
        self.picam2 = Picamera2()
        transform = Transform(hflip=flip_horizontal, vflip=flip_vertical)
        camera_config = self.picam2.create_preview_configuration(transform=transform)
        self.picam2.configure(camera_config)
        self.picam2.start()

        # Nombre de captures à effectuer
        self.num_frames = num_frames

        # Définition des plages de couleurs en HSV
        self.lower_red1 = np.array([0, 120, 70])
        self.upper_red1 = np.array([2, 255, 255])
        self.lower_red2 = np.array([170, 120, 70])
        self.upper_red2 = np.array([180, 255, 255])
        self.lower_green = np.array([35, 50, 50])
        self.upper_green = np.array([85, 255, 255])

        # Liste pour stocker les résultats
        self.results = []

    def process_frame(self, frame, mid_x):
        # Convertir en HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Créer les masques
        mask_red = cv2.inRange(hsv, self.lower_red1, self.upper_red1) + \
                   cv2.inRange(hsv, self.lower_red2, self.upper_red2)
        mask_green = cv2.inRange(hsv, self.lower_green, self.upper_green)

        # Détecter les contours
        contours_red, _ = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_green, _ = cv2.findContours(mask_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        red_detected_left = 0
        green_detected_right = 0

        # Analyse des contours rouges (gauche)
        for cnt in contours_red:
            if cv2.contourArea(cnt) > 500:
                x, _, _, _ = cv2.boundingRect(cnt)
                if x < mid_x:
                    red_detected_left = 1
                    break

        # Analyse des contours verts (droite)
        for cnt in contours_green:
            if cv2.contourArea(cnt) > 500:
                x, _, _, _ = cv2.boundingRect(cnt)
                if x >= mid_x:
                    green_detected_right = 1
                    break

        return red_detected_left, green_detected_right

    def run_detection(self):
        print("Début de la détection...")
        for i in range(self.num_frames):
            # Capture image
            frame = self.picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            height, width, _ = frame.shape
            mid_x = width // 2

            # Traiter la frame
            red_left, green_right = self.process_frame(frame, mid_x)

            # Sauvegarder les résultats
            self.results.append([i + 1, red_left, green_right])

            print(f"Capture {i+1}: Rouge à gauche={red_left}, Vert à droite={green_right}")

            time.sleep(0.1)  # Pause pour éviter la surcharge

        print("Détection terminée.")

    def save_results(self, filename='out.csv'):
        df = pd.DataFrame(self.results, columns=["Frame", "Red_Detection", "Green_Detection"])
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
