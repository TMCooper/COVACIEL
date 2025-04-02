import RPi.GPIO as GPIO
import time

broche_direction = 13

# Initialisation GPIO
# Initialisation de la GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(broche_direction, GPIO.OUT)

# Création du signal PWM
direction = GPIO.PWM(broche_direction, 28)  # Fréquence correcte (28 Hz)
direction.start(0)  # Démarrer avec le bon duty cycle

try:
    while True:
        periode = 20e-3  # 20 ms 
        temps_haut = 1.54e-3  # 1.54 ms
        rapport_cyclique = (temps_haut / periode) * 100  # Duty cycle en %
        
        print(f"Tourne à gauche(+10°)\n rapport cyclique : {rapport_cyclique}\n Temps Haut : {temps_haut}")
        direction.ChangeDutyCycle(rapport_cyclique)  # 1.22 ms (gauche)
        time.sleep(1)  # Maintien 1s

        
        periode = 20e-3  # 20 ms 
        temps_haut = 1.38e-3  # 1.38 ms
        rapport_cyclique = (temps_haut / periode) * 100  # Duty cycle en %
        
        print(f"Retour au centre (0°)\n rapport cyclique : {rapport_cyclique}\n Temps Haut : {temps_haut}")
        direction.ChangeDutyCycle(rapport_cyclique)  # 1.38 ms (neutre)
        time.sleep(1)  # Maintien 1s


        periode = 20e-3  # 20 ms 
        temps_haut = 1.22e-3  # 1.22 ms
        rapport_cyclique = (temps_haut / periode) * 100  # Duty cycle en %
        
        print(f"Tourne à droite (-10°)\n rapport cyclique : {rapport_cyclique}\n Temps Haut : {temps_haut}")
        direction.ChangeDutyCycle(rapport_cyclique)  # 1.54 ms (droite)
        time.sleep(1)  # Maintien 1s

except KeyboardInterrupt:
    print("Arrêt du programme")
    GPIO.cleanup()
