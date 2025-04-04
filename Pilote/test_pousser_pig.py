import pigpio
import time

# Paramètres
periode = 20e-3  # 20 ms (50 Hz)
temps_haut = 1.5e-3  # 2 ms HIGH
rapport_cyclique = (temps_haut / periode) * 100  # Duty cycle en %

# print(f"Fréquence calculée : {frequence:.2f} Hz")

# Broche GPIO utilisée pour le signal PWM
broche_pwm = 17  # Utiliser la broche GPIO correspondant au numéro BCM (ici GPIO17)

# Initialisation de pigpio
pi = pigpio.pi()  # Se connecter au démon pigpio

if not pi.connected:
    exit()

# Configurer la broche PWM en mode sortie
pi.set_mode(broche_pwm, pigpio.OUTPUT)

# Fréquence PWM (28 Hz)
pi.set_PWM_frequency(broche_pwm, 28)

# Résolution PWM (8 bits par défaut, ici on peut l'ajuster à la plage de 0 à 255)
pi.set_PWM_range(broche_pwm, 255)

# Démarrer avec le bon duty cycle
pi.set_PWM_dutycycle(broche_pwm, (rapport_cyclique / 100) * 255)  # Duty cycle en fonction de la plage 0-255

print(f"Démarrage du moteur à {rapport_cyclique:.2f}% de PWM")

try:
    while True:
        time.sleep(1)  # Garder le signal stable sans surcharge CPU

except KeyboardInterrupt:
    print("\nArrêt du programme")

finally:
    pi.set_PWM_dutycycle(broche_pwm, 0)  # Arrêter le PWM proprement
    pi.stop()  # Fermer la connexion avec pigpio
