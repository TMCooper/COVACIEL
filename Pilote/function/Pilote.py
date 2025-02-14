class Pilote:
    speed = float
    direction = float

    def __init__(self, speed, direction): #Ajout de speed et direction au "tableau" de self
        self.speed = speed
        self.direction = direction

    def adjustSpeed(self):
        self.speed = 1.2 #ajuste la valeur de la vitesses
        print(f"Ajustement de speed a : {self.speed}") #print la vitesse après actualisation
        return self.speed #retourne la nouvelle valeur de vitesse 

    def changeDirection(self):
        self.direction = 2.1 #ajuste la direction
        print(f"Ajustement de direction a : {self.direction}") #print la direction après ajustement
        return self.direction #retourne la direction actualiser
    
    def applyBrakes(self, entrer):
        if entrer == True:
            print("Déclanchement des frein") #affiche le bon déclanchement des frein
            return True #True pour oui le frein est déclancher
        elif entrer == False:
            print("Frein non enclanché") #affiche le non déclanchement des frein
            return False
    
    def getCurrentSpeed(self):
        print(f"Valeur actuelle de speed : {self.speed}") #affiche directement la valeur de speed
        return self.speed #retourne la valeur de speed au besoins
    
    def getCurrentDirection(self):
        print(f"Valeur actuelle de la direction prise : {self.direction}") # affiche directement la valeur de la direction
        return self.direction # retourne la valeur de speed