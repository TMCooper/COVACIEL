import RPi.GPIO as GPIO
import time

# Initialisation GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)  # Remplace 15 par la broche que tu utilises

# Créer un objet PWM pour piloter le servo
pwm = GPIO.PWM(11, 50)  # Fréquence de 50 Hz pour un servo classique
pwm.start(0)  # Démarrer avec un duty cycle de 0%

# Fonction pour la marche arrière
def marche_arriere(vitesse):
    """
    Fonction pour effectuer la marche arrière avec le freinage, le passage au point mort, 
    et la marche arrière à vitesse réglable.
    La vitesse est entre 0.0 et 1.0, où 0.0 correspond à la vitesse minimale (1.2 ms) et 
    1.0 à la vitesse maximale (1.4 ms).
    """
    # Etape 1 : Freinage pendant 0.3s
    print("Freinage...")
    pwm.ChangeDutyCycle(5)  # 5% pour la durée à l'état haut de 1 ms (freinage)
    time.sleep(0.3)  # Durée de freinage

    # Etape 2 : Passage au point mort pendant 0.3s
    print("Passage au point mort...")
    pwm.ChangeDutyCycle(5)  # Même rapport cyclique pour le point mort
    time.sleep(0.3)  # Durée du passage au point mort

    # Etape 3 : Marche arrière à vitesse réglable
    print("Marche arrière à vitesse réglable...")
    # Calcul du temps haut pour la marche arrière
    temps_haut_ms = 1.2 + (vitesse * 0.2)  # 1.2 ms à 1.4 ms en fonction de la vitesse (entre 0 et 1)
    rapport_cyclique = (temps_haut_ms / 20) * 100  # Calcul du rapport cyclique en fonction du temps haut

    pwm.ChangeDutyCycle(rapport_cyclique)  # Appliquer le rapport cyclique
    print(f"Vitesse de marche arrière réglée à : {vitesse * 100}%")
    print(f"Temps haut : {temps_haut_ms} ms, Rapport cyclique : {rapport_cyclique}%")
    time.sleep(1)  # Durée de la marche arrière

# Exemple d'utilisation :
try:
    while True:
        # Demander à l'utilisateur de choisir la vitesse de la marche arrière entre 0 et 1
        vitesse = float(input("Entrez une vitesse de marche arrière entre 0.0 et 1.0 : "))
        if 0.0 <= vitesse <= 1.0:
            marche_arriere(vitesse)
        else:
            print("Erreur : La vitesse doit être entre 0.0 et 1.0.")
        time.sleep(2)  # Attendre avant de refaire un tour

except KeyboardInterrupt:
    pwm.stop()  # Arrêter le PWM
    GPIO.cleanup()  # Nettoyer les GPIO
