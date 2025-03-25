import RPi.GPIO as GPIO
import time

# Paramètres
periode = 20e-3  # 20 ms (50 Hz)
temps_haut = 1.6e-3  # 1.6 ms HIGH
rapport_cyclique = (temps_haut / periode) * 100  # 8% duty cycle

# Broche GPIO utilisée pour le signal PWM
broche_pwm = 11  # Vérifie la broche utilisée

# Initialisation de la GPIO
GPIO.setmode(GPIO.BOARD)  
GPIO.setup(broche_pwm, GPIO.OUT)

# Création du signal PWM
pwm = GPIO.PWM(broche_pwm, 50)  # Fréquence stable à 50 Hz
pwm.start(rapport_cyclique)  # Démarrer avec 8% de PWM

print(f"Démarrage du moteur à {rapport_cyclique}% de PWM")

try:
    while True:
        # Vérification du signal et maintien du PWM stable
        pwm.ChangeDutyCycle(rapport_cyclique)
        #time.sleep(0.1)  # Évite une surcharge CPU et stabilise le signal

except KeyboardInterrupt:
    print("Arrêt du programme")

finally:
    pwm.stop()  # Stopper proprement le PWM
    GPIO.cleanup()  # Nettoyage GPIO
