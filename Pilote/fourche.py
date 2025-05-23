import RPi.GPIO as GPIO
import time

# Utilise la numérotation BCM
GPIO.setmode(GPIO.BOARD)

# GPIO 19 correspond à la broche physique 35
broche_fourche = 35

# Configuration de la broche en mode entrée avec résistance de tirage interne activée
GPIO.setup(broche_fourche, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        etat = GPIO.input(broche_fourche)
        print("Signal :", etat)  # 1 ou 0 selon si le capteur détecte quelque chose
        time.sleep(0.1)  # Petite pause pour ne pas spammer la sortie

except KeyboardInterrupt:
    print("Arrêt du programme")

finally:
    GPIO.cleanup()  # Libère les broches GPIO
