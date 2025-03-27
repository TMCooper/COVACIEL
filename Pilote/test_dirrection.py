import RPi.GPIO as GPIO
import time

# Paramètres
periode = 20e-3  # 20 ms (50 Hz)
temps_haut = 2e-3  # 1.6 ms
rapport_cyclique = (temps_haut / periode) * 100  # Duty cycle en %

broche_direction = 12

# Initialisation GPIO
# Initialisation de la GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(broche_direction, GPIO.OUT)

# Création du signal PWM
pwm = GPIO.PWM(broche_direction, 28)  # Fréquence correcte (28 Hz)
pwm.start(rapport_cyclique)  # Démarrer avec le bon duty cycle

try:
    while True:
        periode = 20e-3  # 20 ms 
        temps_haut = 1.54e-3  # 1.54 ms
        rapport_cyclique = (temps_haut / periode) * 100  # Duty cycle en %
        
        print(f"Tourne à gauche(+10°)\n rapport cyclique : {rapport_cyclique}")
        broche_direction.ChangeDutyCycle(6.1)  # 1.22 ms (gauche)
        time.sleep(1)  # Maintien 1s

        
        periode = 20e-3  # 20 ms 
        temps_haut = 1.38e-3  # 1.38 ms
        rapport_cyclique = (temps_haut / periode) * 100  # Duty cycle en %
        
        print(f"Retour au centre (0°)\n rapport cyclique : {rapport_cyclique}")
        broche_direction.ChangeDutyCycle(6.9)  # 1.38 ms (neutre)
        time.sleep(1)  # Maintien 1s


        periode = 20e-3  # 20 ms 
        temps_haut = 1.22e-3  # 1.22 ms
        rapport_cyclique = (temps_haut / periode) * 100  # Duty cycle en %
        
        print(f"Tourne à droite (-10°)\n rapport cyclique : {rapport_cyclique}")
        broche_direction.ChangeDutyCycle(7.7)  # 1.54 ms (droite)
        time.sleep(1)  # Maintien 1s

except KeyboardInterrupt:
    print("Arrêt du programme")
    GPIO.cleanup()
