import RPi.GPIO as GPIO
import time

broche_fourche = 35  # Broche physique (BOARD) = GPIO19

def etat_callback(channel):
    print("Changement détecté, état actuel :", GPIO.input(broche_fourche))

def main():
    print("Initialisation...")
    GPIO.setmode(GPIO.BOARD)

    try:
        GPIO.setup(broche_fourche, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Important : ne pas appeler add_event_detect plusieurs fois sur la même broche
        GPIO.add_event_detect(broche_fourche, GPIO.BOTH, callback=etat_callback, bouncetime=200)

        print("Détection d'événements activée. Appuyez sur Ctrl+C pour quitter.")
        while True:
            time.sleep(0.1)

    except RuntimeError as e:
        print("Erreur d'initialisation GPIO :", e)
    except KeyboardInterrupt:
        print("\nArrêt du programme par l'utilisateur.")
    finally:
        GPIO.cleanup()
        print("Nettoyage GPIO terminé.")

if __name__ == '__main__':
    main()
