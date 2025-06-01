import RPi.GPIO as GPIO
import time

# Broche GPIO utilisée pour le signal PWM
fourche = 15  # Vérifie bien la broche utilisée

# Initialisation de la GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(fourche, GPIO.IN)

try:
    while True:
        etat = GPIO.input(fourche)  # Lecture de l'état de la broche
        print(f"État de la fourche optique : {etat}")
        time.sleep(0.1)  # Petite pause pour éviter de surcharger l'affichage

except KeyboardInterrupt:
    print("\nArrêt du programme")

finally:
    GPIO.cleanup()  # Nettoyage GPIO
