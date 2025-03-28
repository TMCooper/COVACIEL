import cv2
import numpy as np

# Ouvrir la caméra
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)  # Forcer l'utilisation de V4L2 pour la capture

# Vérifier si la caméra s'est bien ouverte
if not cap.isOpened():
    print("Erreur: impossible d'ouvrir la caméra")
    exit()



while True:
    ret, frame = cap.read()
    if not ret:
        break

    blurred_frame = cv2.GaussianBlur(frame, (15, 15), 0)  
    # Appliquer un flou avec un noyau de taille (15, 15)

    # Convertir l'image en HSV
    hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

    # Définir les plages de couleurs pour le rouge
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    # Définir la plage de couleurs pour le vert
    lower_green = np.array([40, 50, 50])
    upper_green = np.array([90, 255, 255])

    # Masques pour le rouge et le vert
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = mask_red1 + mask_red2  # Combiner les deux gammes du rouge
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    # Trouver les contours pour le rouge
    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours_red:
        if cv2.contourArea(cnt) > 500:  # Éviter les petits bruits
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 3)  # Rouge

    # Trouver les contours pour le vert
    contours_green, _ = cv2.findContours(mask_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours_green:
        if cv2.contourArea(cnt) > 500:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)  # Vert

    # Afficher le flux vidéo avec détection
    cv2.imshow("Detection Rouge et Vert", frame)

    # Quitter avec la touche 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
