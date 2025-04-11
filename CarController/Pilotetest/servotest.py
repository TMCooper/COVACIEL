import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)  # Utilise le numéro GPIO (ex : 22)
GPIO.setup(22, GPIO.OUT)  # GPIO 22 = pin physique 15

pwm = GPIO.PWM(22, 50)  # 50 Hz
pwm.start(0)

def set_angle(angle):
    duty = 2.5 + (angle / 18)
    pwm.ChangeDutyCycle(duty)

try:
    while True:
        print("Centre")
        set_angle(90)
        time.sleep(1)

        print("Droite")
        set_angle(140)
        time.sleep(1)

        print("Gauche")
        set_angle(40)
        time.sleep(1)

except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
