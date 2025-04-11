import RPi.GPIO as GPIO
import time

# Initialisation GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(15, GPIO.OUT)  # Remplace 15 par la broche que tu utilises

# Créer un objet PWM pour piloter le servo
pwm = GPIO.PWM(15, 50)  # Fréquence de 50 Hz pour un servo classique
pwm.start(0)  # Démarrer avec un duty cycle de 0%

# Fonction pour piloter le servo en fonction de l'angle demandé
def piloter_direction(angle):
    # Calcul du rapport cyclique en fonction de l'angle (en °)
    
    if angle == 0:
        duty_cycle = 6.9  # Correspond à 0° avec un temps haut de 1.38 ms
    elif angle == 10:
        duty_cycle = 7.7  # Correspond à +10° avec un temps haut de 1.54 ms
    elif angle == -10:
        duty_cycle = 6.1  # Correspond à -10° avec un temps haut de 1.22 ms
    else:
        # Pour d'autres angles, tu peux interpoler linéairement entre ces valeurs.
        # Exemple simplifié pour les angles entre -10° et 10°, sinon ajuster avec d'autres mesures.
        duty_cycle = 6.9 + (angle * 0.1)  # Une interpolation simple (à ajuster selon tes besoins)
    
    # Appliquer le duty cycle au signal PWM
    pwm.ChangeDutyCycle(duty_cycle)
    print(f"Angle demandé : {angle}°, Rapport cyclique : {duty_cycle}%")
    time.sleep(1)  # Attendre un peu pour permettre au servo de réagir

# Fonction pour obtenir la consigne de direction
def obtenir_consigne():
    try:
        consigne = float(input("Entrez une consigne de direction entre -10 et 10 (ex: -10, 0, 10) : "))
        if consigne >= -10 and consigne <= 10:
            piloter_direction(consigne)
        else:
            print("Erreur : La consigne doit être entre -10 et 10.")
    except ValueError:
        print("Erreur : Veuillez entrer un nombre valide.")

try:
    while True:
        obtenir_consigne()  # Demander à l'utilisateur de saisir la consigne
        time.sleep(1)  # Attendre un peu avant de redemander

except KeyboardInterrupt:
    pwm.stop()  # Arrêter le PWM
    GPIO.cleanup()  # Nettoyer les GPIO
