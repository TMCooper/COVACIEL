from function.Pilote import *
from threading import Thread

def main():
    try :        
        pilote = Pilote(0.0, 0.0, 32, 33) #defini les valeur par defaut a speed 0 et direction 0 les deux en type float ainsi que les pin utiliser donc 32 pour le moteur et 33 pour la direction
        
        vit = Thread(target=pilote.adjustSpeed)
        dir = Thread(target=pilote.changeDirection)

        vit.start()
        dir.start()

        print(threading.enumerate())

        while True:

            Control_car_input = input("A quelle vitesse voulez-vous ajuster le moteur (-1.0 / 1.0) : ")
            Control_direction_input = input("Dans quel dirrection voulez vous allez (-1.0 / 1.0) ? : ")
            
            pilote.UpdateControlCar(Control_car_input)
            pilote.UpdateDirectionCar(Control_direction_input)

    except KeyboardInterrupt or RuntimeError:
        pilote.stop()
        vit.join()
        dir.join()
        gpio.cleanup()  # Nettoyer les GPIO
        print("\nArret du programme...\n")

    except ValueError:
        pilote.stop()
        vit.join()
        dir.join()
        gpio.cleanup()
        print("Mauvaise input..")

if __name__ == '__main__':
    main()