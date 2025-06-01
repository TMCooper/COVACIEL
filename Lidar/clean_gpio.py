import RPi.GPIO as GPIO
import time

# Définir le mode de numérotation des broches GPIO
GPIO.setmode(GPIO.BOARD)  # Utilise la numérotation BOARD



# Configurer la broche GPIO 12 en sortie
# Notez que GPIO 12 en mode BOARD correspond à GPIO 18 en mode BCM
GPIO.setup(12, GPIO.OUT)

try:
    print("Starting test on GPIO 12 (BOARD mode)")
    GPIO.output(12, GPIO.HIGH)  # Met la broche à l'état haut
    time.sleep(2)  # Attend 2 secondes
    GPIO.output(12, GPIO.LOW)  # Met la broche à l'état bas
    print("Test completed on GPIO 12 (BOARD mode)")

except KeyboardInterrupt:
    print("Test interrupted")

finally:
    GPIO.cleanup()
    print("GPIO cleanup completed")
