from function.Pilote import *
from threading import Thread

def main():
    try :
        Control_car_input = 0
        Control_direction_input = 0

        pilote = Pilote(0.0, 0.0, 32, 33) #defini les valeur par defaut a speed 0 et direction 0 les deux en type float ainsi que les pin utiliser donc 11 pour le moteur et 13 pour la direction

        dir = Thread(target=pilote.changeDirection, args=(Control_direction_input,))
        vit = Thread(target=pilote.adjustSpeed, args=(Control_car_input,))

        vit.start()
        dir.start()


        while True:
            # Control_car_input = 0.3
            Control_car_input = input("A quelle vitesse voulez-vous ajuster le moteur (-1.0 / 1.0) : ")
            Control_direction_input = input("Dans quel dirrection voulez vous allez (-1.0 / 1.0) ? : ")
            
            # pilote.adjustSpeed(Control_car_input)
            # pilote.changeDirection(Control_direction_input)


            # print(f"Speed actuelle : {pilote.getCurrentSpeed()}")
            # print(f"Direction actuelle : {pilote.getCurrentDirection()}")        
        
            # pilote.applyBrakes(True)

    except KeyboardInterrupt or RuntimeError:
        # vit.join()
        # dir.join()
        pilote.stop()
        gpio.cleanup()  # Nettoyer les GPIO
        print("\nArret du programme...\n")

    except ValueError:
        # vit.join()
        # dir.join()
        pilote.stop()
        gpio.cleanup()
        print("Mauvaise input..")
        pass

if __name__ == '__main__':
    # t = Thread(target=main)
    main()
    # t.start()