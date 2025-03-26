import RPi.GPIO as gpio

gpio.setmode(gpio.BOARD)  # Utilisation des numéros physiques des broches

# Liste des broches GPIO disponibles sur le Raspberry Pi
broches_a_tester = [11, 12, 13, 15, 16, 18, 22, 29, 31, 32, 33, 35, 36, 37, 38, 40]

broches_utilisees = []

for broche in broches_a_tester:
    try:
        gpio.setup(broche, gpio.IN)  # Définir la broche en entrée pour voir son état
        etat = gpio.input(broche)
        print(f"Broche {broche} -> État: {'HIGH' if etat else 'LOW'}")
        broches_utilisees.append((broche, etat))
    except RuntimeError:
        print(f"⚠️ Impossible de lire la broche {broche} (peut-être en sortie)")

gpio.cleanup()  # Nettoyage des GPIO après le test

