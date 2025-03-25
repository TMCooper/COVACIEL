import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.cleanup()  # Réinitialise les GPIO
GPIO.setup(2, GPIO.OUT)
