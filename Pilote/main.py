from function.Pilote import *

def main():
    try :
        entrer = False
        
        pilote = Pilote(0.0, 0.0, 27, 28) #defini les valeur par defaut a speed 0 et direction 0 les deux en type float
        
        pilote.changeDirection()
        
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