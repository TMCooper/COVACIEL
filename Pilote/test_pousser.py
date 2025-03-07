import RPi.GPIO as gpio
import time

branch_moteur = 12

target_time = 0.0184  # 18.4 ms
short_time = 0.0016    # Temps court pour envoyer un HIGH (1.6 ms, par exemple)

gpio.setmode(gpio.BOARD)
gpio.setup(branch_moteur, gpio.OUT)

pilote = gpio.PWM(branch_moteur, 1000)

pilote.start(8)  # Commence le PWM avec un rapport cyclique de 8%

try:
    while True:
        # Maintenir le moteur à LOW pendant 18.4 ms
        gpio.output(branch_moteur, gpio.LOW)
        time.sleep(target_time)  # Attendre 18.4 ms
        
        # Passer à HIGH pendant 1.6 ms
        gpio.output(branch_moteur, gpio.HIGH)
        time.sleep(short_time)  # Attendre 1.6 ms pour marquer l'événement

except KeyboardInterrupt:
    print("\nZeub")

finally:
    print("\nExit...")