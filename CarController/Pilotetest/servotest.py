import RPi.GPIO as GPIO
import time

servo_pin = 15  # Assurez-vous que c'est la bonne broche
GPIO.setmode(GPIO.BOARD)
GPIO.setup(servo_pin, GPIO.OUT)

pwm = GPIO.PWM(servo_pin, 50)  # Fréquence de 50 Hz
pwm.start(7.5)  # Duty cycle pour la position centrale (environ 90 degrés)

try:
    while True:
        pwm.ChangeDutyCycle(5)  # Positionner à environ 0 degré
        time.sleep(1)
        pwm.ChangeDutyCycle(7.5)  # Positionner à environ 90 degrés
        time.sleep(1)
        pwm.ChangeDutyCycle(10)  # Positionner à environ 180 degrés
        time.sleep(1)
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
