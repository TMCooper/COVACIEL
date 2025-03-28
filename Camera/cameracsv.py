import pandas as pd
from picamera2 import Picamera2
from libcamera import Transform
import cv2
import numpy as np
import time

# Initialisation de la caméra
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(transform=Transform(hflip=True, vflip=True))
picam2.configure(camera_config)
picam2.start()

# Plages de couleur rouge en HSV
lower_red1 = np.array([0, 120, 70])
upper_red1 = np.array([2, 255, 255])
lower_red2 = np.array([170, 120, 70])
upper_red2 = np.array([180, 255, 255])

# Plages de couleur verte en HSV
lower_green = np.array([35, 50, 50])
upper_green = np.array([85, 255, 255])

# Liste pour stocker les résultats
results = []

# Capture et traitement des images
for i in range(10):
    frame = picam2.capture_array()  # Capture une image
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Conversion pour OpenCV

    # Conversion en HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Création des masques pour le rouge (2 plages)
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = mask_red1 + mask_red2  # Combinaison des masques rouges

    # Création du masque pour le vert
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    # Détection et comptage des contours
    red_contours_count = len([cnt for cnt in cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0] if cv2.contourArea(cnt) > 500])
    green_contours_count = len([cnt for cnt in cv2.findContours(mask_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0] if cv2.contourArea(cnt) > 500])

    # Stockage des résultats
    results.append([i + 1, red_contours_count, green_contours_count])

    print(f"Capture {i+1}: {red_contours_count} rouges, {green_contours_count} verts")
    time.sleep(0.1)  # Pause pour éviter la surcharge

# Création du DataFrame et export en CSV
df = pd.DataFrame(results, columns=["Frame", "Red Contours", "Green Contours"])
df.to_csv('color.csv', index=False)

# Nettoyage
picam2.stop()
print("Fin du programme. Résultats sauvegardés dans 'out.csv'.")
