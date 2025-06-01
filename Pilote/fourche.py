import RPi.GPIO as GPIO

# GPIO 19 correspond à la broche physique 35
broche_fourche = 35

# Configuration de la broche en mode entrée avec résistance de tirage interne activée

def etat_callback():
    print("Changement détecté, état actuel :", GPIO.input(broche_fourche))  # 1 ou 0 selon si le capteur détecte quelque chose

def main():
        try:
            GPIO.add_event_callback(broche_fourche, GPIO.BOTH, callback=etat_callback)

        except KeyboardInterrupt:
            print("Arrêt du programme")

        finally:
            GPIO.cleanup()  # Libère les broches GPIO

if __name__ == '__main__':
    # Utilise la numérotation BOARD
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(broche_fourche, GPIO.IN, pull_up_down=GPIO.PUD_UP)
     