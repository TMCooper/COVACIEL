import RPi.GPIO as GPIO
import time

servo_pin = 15  # Assurez-vous que c'est la bonne broche
GPIO.setmode(GPIO.BOARD)
GPIO.setup(servo_pin, GPIO.OUT)

# pwm = GPIO.PWM(servo_pin, 50)  # Fréquence de 50 Hz
# pwm.start(7.5)  # Duty cycle pour la position centrale (environ 10° degrés)

# Paramètres
periode = 20e-3  # 20 ms (50 Hz)
temps_haut = 1.38e-3  # 0.5 ms
temps_bas = periode - temps_haut  # Temps bas
rapport_cyclique = (temps_haut / periode) * 100

# pwm.ChangeDutyCycle(rapport_cyclique)  # Positionner à environ 0 degré
# print(rapport_cyclique)

try:
    while True:
        GPIO.output(servo_pin, GPIO.HIGH)
        time.sleep(temps_haut)
        GPIO.output(servo_pin, GPIO.LOW)
        time.sleep(temps_bas)

except KeyboardInterrupt:
    print("Arrêt du programme")
finally:
    # Arrêter le PWM et nettoyer les GPIO
    # pwm.stop()
    GPIO.cleanup()
