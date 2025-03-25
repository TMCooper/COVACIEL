# code OK !

import RPi.GPIO as GPIO
import time

# Paramètres
periode = 20e-3  # Période de 20 ms
temps_haut = 1.6e-3  # Début à 1.6 ms (0 m/s)
# max_temps_haut = 2e-3  # 2 ms = vitesse max
temps_bas = periode - temps_haut  # Temps à l'état bas

# Broche GPIO utilisée pour le signal PWM
broche_pwm = 11  # Vérifie la broche utilisée

# Initialisation de la GPIO
GPIO.setmode(GPIO.BOARD)  
GPIO.setup(broche_pwm, GPIO.OUT)

pwm = GPIO.PWM(broche_pwm, 50)  # Fréquence 50 Hz (1/20 ms)
pwm.start((temps_haut / periode) * 100)  # Démarrer avec le bon rapport cyclique
print((temps_haut/periode) * 100) # 8%

try:
    while True:
        GPIO.output(broche_pwm, GPIO.HIGH)  # Met la broche à 1 (signal HIGH)
        time.sleep(temps_haut)  # Maintenir l'état haut pendant 1.6 ms

        GPIO.output(broche_pwm, GPIO.LOW)  # Met la broche à 0 (signal LOW)
        time.sleep(temps_bas)  # Maintenir l'état bas pendant 18.4 ms

        # print(temps_bas + temps_haut)
        # print(f"temps haut : {temps_haut} \ntemps bas : {temps_bas} \nperiode : {periode} \npwm : {pwm} \nrapport cyclique : {rapport_cyclique}")

except KeyboardInterrupt:
    print("Arrêt du programme")

finally:
    GPIO.cleanup()  # Nettoyage GPIO
