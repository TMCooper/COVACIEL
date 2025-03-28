from function.Pilote import *
from time import sleep

def main():
    try :        
        pilote = Pilote(0.0, 0.0, 11, 13) #defini les valeur par defaut a speed 0 et direction 0 les deux en type float ainsi que les pin utiliser donc 11 pour le moteur et 13 pour la direction
        
        # pilote.changeDirection()
        
        # currentDirection = pilote.changeDirection()
        # print(f"Direction actuelle : {currentDirection}")
        while True:
            # Control_car_input = 0.3
            Control_car_input = input("A quel vitesses voulez vous ajuter le moteur (-1.0 / 1.0) : ")
            pilote.adjustSpeed(Control_car_input)
            sleep(1)
        # currentSpeed = pilote.adjustSpeed()
        # print(f"Speed actuelle : {currentSpeed}")
        
        # pilote.getCurrentDirection()
        # pilote.getCurrentSpeed()
        
        # pilote.applyBrakes(entrer)

    except KeyboardInterrupt:
        print("\nArret du programme...\n")
    
    except ValueError:
        print("Mauvaise input..")
        pass

if __name__ == '__main__':
    main()