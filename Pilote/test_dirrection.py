import RPi.GPIO as GPIO
from time import sleep

broche_direction = 15

# Initialisation GPIO
# Initialisation de la GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(broche_direction, GPIO.OUT)

# Création du signal PWM
direction = GPIO.PWM(broche_direction, 50)  # Fréquence correcte (28 Hz)
direction.start(0)  # Démarrer avec le bon duty cycle

try:
    while True:
        # periode = 20e-3  # 20 ms 
        # temps_haut = 1.38e-3  # 1.54 ms
        # rapport_cyclique = (temps_haut / periode) * 100  # Duty cycle en %
        
        # print(f"Tourne à gauche(+10°)\n rapport cyclique : {rapport_cyclique}\n Temps Haut : {temps_haut}")
        direction.ChangeDutyCycle(7.7)
        sleep(5)
        direction.ChangeDutyCycle(6.9)
        sleep(5)
        direction.ChangeDutyCycle(6.1)
        sleep(5)

except KeyboardInterrupt:
    print("Arrêt du programme")
    GPIO.cleanup()
