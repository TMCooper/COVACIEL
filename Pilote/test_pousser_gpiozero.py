from gpiozero import PWMOutputDevice

# Paramètres
periode = 20e-3  # 20 ms (50 Hz)
temps_haut = 1.7e-3  # 2 ms HIGH
rapport_cyclique = (temps_haut / periode) * 100  # Duty cycle en %

# print(f"Fréquence calculée : {frequence:.2f} Hz")

# Broche GPIO utilisée pour le signal PWM
broche_pwm = 17  # Utiliser la broche GPIO correspondant au numéro BCM (ici GPIO17)

# Initialisation de la broche en mode PWM
pwm = PWMOutputDevice(broche_pwm)

# Fréquence PWM (50 Hz)
pwm.frequency = 28.03

# Démarrer avec le bon duty cycle
pwm.value = rapport_cyclique / 100  # Duty cycle entre 0 (off) et 1 (maximum)

# print(f"Démarrage du moteur à {rapport_cyclique:.2f}% de PWM")

try:
    while True:
        continue
except KeyboardInterrupt:
    pwm.off()  # Arrêter le PWM proprement
