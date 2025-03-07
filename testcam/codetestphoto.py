from picamera2 import Picamera2
import numpy as np
import cv2

# Initialiser la caméra
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())

# Capturer une image (array)
image_array = picam2.capture_array()

# Convertir en HSV et appliquer un flou
hsv = cv2.cvtColor(image_array, cv2.COLOR_BGR2HSV)
blurred = cv2.GaussianBlur(hsv, (15, 15), 0)

# Afficher l'image traitée
cv2.imshow("Image Traitée", blurred)

cv2.waitKey(0)
cv2.destroyAllWindows()