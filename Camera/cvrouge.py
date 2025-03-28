from picamera2 import Picamera2 , Preview
from libcamera import Transform
import cv2
import numpy as np
import time

# Initialisation de la caméra
try :
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

    while True:
        frame = picam2.capture_array()  # Capture une image depuis la caméra
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Conversion en format OpenCV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Création du masque pour détecter le rouge
        mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask_red = mask_red1 + mask_red2  # Combinaison des deux masques rouges

        # Création du masque pour détecter le vert
        mask_green = cv2.inRange(hsv, lower_green, upper_green)

        # Trouver et dessiner les contours pour le rouge
        contours_red, _ = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_red:
            if cv2.contourArea(cnt) > 500:  # Éviter les petits bruits
                cv2.drawContours(frame, [cnt], -1, (0, 0, 255), 2)  # Dessine le contour en rouge

        # Trouver et dessiner les contours pour le vert
        contours_green, _ = cv2.findContours(mask_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_green:
            if cv2.contourArea(cnt) > 500:
                cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)  # Dessine le contour en vert

        # Affichage de l'image en couleur avec les détections
        cv2.imshow("Detection Rouge et Vert", frame)

        # Sortie si on appuie sur 'ESC'
        if cv2.waitKey(1) & 0xFF == 27:
            break

        time.sleep(0.1)  # Pause pour éviter une surcharge de la capture

except KeyboardInterrupt:
    cv2.destroyAllWindows()
    picam2.stop()

finally:
    print("Exit...")