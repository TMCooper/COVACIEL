import RPi.GPIO as GPIO
import time

# Paramètres
periode = 20e-3  # Période de 20ms
rapport_cyclique = 7.5 / 100  # 7.5% de rapport cyclique
temps_haut = rapport_cyclique * periode  # Temps en haut (1.5)
temps_bas = periode - temps_haut  # Temps en bas (0)

# Broche GPIO à utiliser pour le signal PWM
broche_pwm = 27  # Exemple de broche GPIO 18 (Vérifie quelle broche tu veux utiliser)

# Initialisation de la GPIO
GPIO.setmode(GPIO.BCM)  # Mode BCM pour utiliser le numéro de broche
GPIO.setup(broche_pwm, GPIO.OUT)  # Configuration de la broche en sortie

# Création du signal PWM avec une fréquence de 50Hz (1/20ms)
pwm = GPIO.PWM(broche_pwm, 50)  # Fréquence de 50Hz (période de 20ms)
pwm.start(0)  # Démarrer le signal PWM avec un rapport cyclique initial de 0%

try:
    while True:
        # Envoie un signal PWM de 7.5% de rapport cyclique
        pwm.ChangeDutyCycle(7.5)  # 7.5% de rapport cyclique
        time.sleep(periode)  # Attendre la durée de la période (20ms)
        
        # Envoie un signal PWM de 0% de rapport cyclique (signal à l'état bas)
        pwm.ChangeDutyCycle(0)  # 0% de rapport cyclique
        time.sleep(temps_bas)  # Attendre le temps restant pour une période complète (92.5% du temps)
        
except KeyboardInterrupt:
    print("Arrêt du programme")

finally:
    pwm.stop()  # Arrêter le PWM
    GPIO.cleanup()  # Nettoyage de la configuration GPIO
