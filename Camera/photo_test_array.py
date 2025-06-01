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
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    height, width, _ = frame.shape  # Dimensions de l'image
    mid_x = width // 2  # Milieu de l'image

    # Conversion en HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Masques de couleur
    mask_red = cv2.inRange(hsv, lower_red1, upper_red1) + cv2.inRange(hsv, lower_red2, upper_red2)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    # Détection des contours
    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_green, _ = cv2.findContours(mask_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Variables pour stocker les détections
    red_detected_left = 0
    green_detected_right = 0

    # Vérification des contours rouges (gauche)
    for cnt in contours_red:
        if cv2.contourArea(cnt) > 500:
            x, _, _, _ = cv2.boundingRect(cnt)  # x = position horizontale du contour
            if x < mid_x:  # Si dans la partie gauche
                red_detected_left = 1
                break  # On arrête dès qu'on trouve un rouge valide à gauche

    # Vérification des contours verts (droite)
    for cnt in contours_green:
        if cv2.contourArea(cnt) > 500:
            x, _, _, _ = cv2.boundingRect(cnt)
            if x >= mid_x:  # Si dans la partie droite
                green_detected_right = 1
                break  # On arrête dès qu'on trouve un vert valide à droite

    # Stockage des résultats
    results.append([i + 1, red_detected_left, green_detected_right])

    print(f"Capture {i+1}: Rouge à gauche={red_detected_left}, Vert à droite={green_detected_right}")
    time.sleep(0.1)  # Pause pour éviter la surcharge

# Création du DataFrame et export en CSV
df = pd.DataFrame(results, columns=["Photo n° ", "Rouge à gauche", "Vert à droite"])
df.to_csv('out.csv', index=False)

# Nettoyage
picam2.stop()
print("Fin du programme. Résultats sauvegardés dans 'out.csv'.")
