from function.Pilote import *
from threading import Thread

def main():
    try :        
        pilote = Pilote(0.0, 0.0, 11, 15) #defini les valeur par defaut a speed 0 et direction 0 les deux en type float ainsi que les pin utiliser donc 11 pour le moteur et 13 pour la direction
        
        # pilote.changeDirection()
        
        # currentDirection = pilote.changeDirection()
        # print(f"Direction actuelle : {currentDirection}")
        while True:
            # Control_car_input = 0.3
            Control_car_input = input("A quel vitesses voulez vous ajuter le moteur (-1.0 / 1.0) : ")
            Control_direction_input = input("Dans quel dirrection voulez vous allez (-1.0 / 1.0) ? : ")
            
            Thread(target=pilote.adjustSpeed, args=(Control_car_input,)).start()
            Thread(target=pilote.changeDirection, args=(Control_direction_input,)).start()
            # pilote.adjustSpeed(Control_car_input)
            # pilote.changeDirection(Control_direction_input)
            # sleep(1)
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
    # t = Thread(target=main)
    main()
    # t.start()