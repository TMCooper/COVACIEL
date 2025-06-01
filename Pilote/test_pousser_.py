import RPi.GPIO as GPIO
import time

# Paramètres
periode = 20e-3  # 20 ms (50 Hz)
temps_haut = 1.6e-3  # 1.6 ms HIGH
temps_bas = periode - temps_haut  # Temps bas
rapport_cyclique = (temps_haut / periode) * 100  # Duty cycle en %

# print(f"Fréquence calculée : {frequence:.2f} Hz")

# Broche GPIO utilisée pour le signal PWM
broche_pwm = 11  # Vérifie la broche utilisée

# Initialisation de la GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(broche_pwm, GPIO.OUT)

# Création du signal PWM
# pwm = GPIO.PWM(broche_pwm, 28)  # Fréquence correcte (50 Hz)
# pwm.start(rapport_cyclique)  # Démarrer avec le bon duty cycle

print(f"Démarrage du moteur à {rapport_cyclique:.2f}% de PWM")

# pwm.ChangeDutyCycle(rapport_cyclique)

try:
    while True:
        GPIO.output(broche_pwm, GPIO.HIGH)
        time.sleep(temps_haut)
        GPIO.output(broche_pwm, GPIO.LOW)
        time.sleep(temps_bas)


except KeyboardInterrupt:
    print("\nArrêt du programme")

finally:
    # broche_pwm.stop()  # Stopper proprement le PWM
    GPIO.cleanup()  # Nettoyage GPIO
