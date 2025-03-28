from picamera2 import Picamera2
import cv2
import numpy as np
import time

# Initialisation de la caméra
picam2 = Picamera2()
picam2.start()

# Définition des plages de couleurs en HSV
lower_red = np.array([0, 120, 70])
upper_red = np.array([10, 255, 255])
lower_green = np.array([35, 50, 50])
upper_green = np.array([85, 255, 255])

# Capture et traitement des images
for i in range(10):
    frame = picam2.capture_array()  # Capture une image
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Conversion pour OpenCV

    # Appliquer un flou gaussien
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)

    # Conversion en HSV
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # Détection des couleurs
    mask_red = cv2.inRange(hsv, lower_red, upper_red)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    # Dessin des contours
    for mask, color in [(mask_red, (0, 0, 255)), (mask_green, (0, 255, 0))]:
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if cv2.contourArea(cnt) > 500:
                cv2.drawContours(frame, [cnt], -1, color, 2)

    # Sauvegarde et affichage
    filename = f"capture_{i+1}.jpg"
    cv2.imwrite(filename, frame)
    print(f"Capture {i+1} enregistrée : {filename}")
    cv2.imshow("Détection", frame)

    # Attendre 0.1s, quitter si "ESC" est pressé
    if cv2.waitKey(100) & 0xFF == 27:
        break

# Nettoyage
picam2.stop()
cv2.destroyAllWindows()
print("Fin du programme.")
