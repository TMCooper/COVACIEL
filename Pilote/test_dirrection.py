import RPi.GPIO as gpio
import time

# Initialisation GPIO
gpio.setmode(gpio.BCM)  
gpio.setup(17, gpio.OUT)  # Servo direction sur GPIO 17 (Pin 11)

# Fréquence PWM de 50 Hz (période 20 ms)
pwm_direction = gpio.PWM(17, 50)
pwm_direction.start(6.9)  # Position neutre (~1.38 ms)

try:
    while True:
        print("Tourne à gauche (-10°)")
        pwm_direction.ChangeDutyCycle(6.1)  # 1.22 ms (gauche)
        time.sleep(1)  # Maintien 1s

        print("Retour au centre (0°)")
        pwm_direction.ChangeDutyCycle(6.9)  # 1.38 ms (neutre)
        time.sleep(1)  # Maintien 1s

        print("Tourne à droite (+10°)")
        pwm_direction.ChangeDutyCycle(7.7)  # 1.54 ms (droite)
        time.sleep(1)  # Maintien 1s

        print("Retour au centre (0°)")
        pwm_direction.ChangeDutyCycle(6.9)  # 1.38 ms (neutre)
        time.sleep(1)  # Maintien 1s

except KeyboardInterrupt:
    print("Arrêt du programme")
    gpio.cleanup()
