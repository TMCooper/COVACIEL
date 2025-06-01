from TestPilote import Pilote
from time import sleep

def main():
    pilote = Pilote(0.0, 0.0, 11, 15)  # Exemple : vitesse 0, direction 0, moteur sur pin 11, servo sur pin 15

    try:
        while True:
            cmd = input("Commande (g=gauche, d=droite, t=tout droit, q=quitter) : ").lower()

            if cmd == 'g':
                pilote.changeDirection(-1)
            elif cmd == 'd':
                pilote.changeDirection(1)
            elif cmd == 't':
                pilote.changeDirection(0)
            elif cmd == 'q':
                break
            else:
                print("Commande inconnue.")

    except KeyboardInterrupt:
        print("Arrêt du test.")
    finally:
        pilote.stop()

if __name__ == "__main__":
    main()
