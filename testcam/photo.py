from picamera2 import Picamera2
import numpy as np
import time

try:
    picam2 = Picamera2()
    picam2.start()
    
    for _ in range(10):  # Effectuer 10 captures
        frame = picam2.capture_array("main")
        print("Capture réussie")  # Affichage dans le terminal
        
        time.sleep(0.1)  # Attendre 0.1 seconde pour obtenir 10 captures par seconde
    
    picam2.stop()

except Exception as e:
    print(f"Erreur pendant la capture: {e}")