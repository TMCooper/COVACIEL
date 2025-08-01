from function.Pilote import *

def main():
    try :        
        pilote = Pilote(0.0, 0.0, 32, 33, 35) #defini les valeur par defaut a speed 0 et direction 0 les deux en type float ainsi que les pin utiliser donc 32 pour le moteur et 33 pour la direction

        # print(threading.enumerate())

        while True:

            Control_car_input = input("A quelle vitesse voulez-vous ajuster le moteur (-1.0 / 1.0) : ")
            id_car = 0
            Control_direction_input = input("Dans quel dirrection voulez vous allez (-1.0 / 1.0) ? : ")
            id_dir = 1
            
            pilote.UpdateCar(id_car, Control_car_input)
            pilote.UpdateCar(id_dir, Control_direction_input)
            # pilote.GetFourche()
            # print(f"Direction actuelle :{pilote.getCurrentDirection()}")
            # print(f"Vitesse actuelle :{pilote.getCurrentSpeed()}")
            # pilote.applyBrakes(True)

    except KeyboardInterrupt or RuntimeError or ValueError:
        pilote.stop()
        # gpio.cleanup()  # Nettoyer les GPIO
        print("\nArret du programme...\n")

if __name__ == '__main__':
    main()