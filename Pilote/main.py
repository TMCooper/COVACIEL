from function.Pilote import *

def main():
    try :
        entrer = False
        
        pilote = Pilote(0.0, 0.0, 11, 13) #defini les valeur par defaut a speed 0 et direction 0 les deux en type float ainsi que les pin utiliser donc 11 pour le moteur et 13 pour la direction
        
        # pilote.changeDirection()
        
        # currentDirection = pilote.changeDirection()
        # print(f"Direction actuelle : {currentDirection}")
        
        pilote.adjustSpeed()
        
        # currentSpeed = pilote.adjustSpeed()
        # print(f"Speed actuelle : {currentSpeed}")
        
        pilote.getCurrentDirection()
        pilote.getCurrentSpeed()
        
        pilote.applyBrakes(entrer)

    except KeyboardInterrupt:
        print("\nArret du programme...\n")

if __name__ == '__main__':
    main()