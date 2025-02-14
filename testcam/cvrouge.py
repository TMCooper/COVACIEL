from picamera2 import Picamera2
import cv2
import numpy as np

# Initialisation de la caméra
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

# Plages de couleur rouge en HSV
lower_red1 = np.array([0, 120, 70])
upper_red1 = np.array([10, 255, 255])
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

    # Combinaison des masques rouge et vert
    mask = cv2.bitwise_or(mask_red, mask_green)

    # Détection des contours
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for c in cnts:
        if cv2.contourArea(c) > 600:  # Filtrer les petits objets
            x, y, w, h = cv2.boundingRect(c)
            # Vérification de la couleur de l'objet détecté
            if np.any(mask_red[y:y+h, x:x+w]):  # Si le rouge est présent
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Rectangle rouge
                cv2.putText(frame, "ROUGE DETECTE", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            elif np.any(mask_green[y:y+h, x:x+w]):  # Si le vert est présent
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Rectangle vert
                cv2.putText(frame, "VERT DETECTE", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Affichage de l'image en couleur avec les détections
    cv2.imshow("Detection Rouge et Vert", frame)

    # Sortie si on appuie sur 'ESC'
    if cv2.waitKey(1) & 0xFF == 27:
        break

cv2.destroyAllWindows()
picam2.stop()
