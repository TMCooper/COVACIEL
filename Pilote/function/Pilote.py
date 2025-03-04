import time

class Pilote():
    speed = float
    direction = float

    branch_moteur = int #Branche moteur 27
    branch_direction = int #Branche pour la direction 28

    periode = 20000 # Periode de 50 ms en microsecondes

    # start_time = time.time()

    # def micros():
        # return int((time.time() - Pilote.start_time) * 1_000_000)

    def __init__(self, speed, direction, branch_moteur, branch_direction): #Ajout de speed, direction, branch_moteur et branch_direction au "tableau" de self
        self.speed = speed
        self.direction = direction
        self.branch_moteur = branch_moteur
        self.branch_direction = branch_direction

    def adjustSpeed(self):
        #faire un system de com entre le raspi et le resultat de notre decision
        
        self.speed = Pilote.verificationEntrer() #Ajuste la valeur de la vitesses entre -1.0 et 1.0
        rapportCyclique = Pilote.calculerRapportCyclique(self)
        signalPWM = Pilote.genererSignalPWM(self, rapportCyclique)
        print(f"Ajustement de speed a : {self.speed} \n Signal PWM = {signalPWM}\n Rapport cyclique : {rapportCyclique}%") #print la vitesse après actualisation
        
        return signalPWM #retourne la nouvelle valeur de vitesse 

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
    
    def verificationEntrer():
        new_speed = input("A quel vitesses voulez vous ajuter le moteur (-1.0 / 1.0) : ") # Demande a l'utilisateur la nouvelle valeur de new_speed convenue entre -1.0 et 1.0 
        new_speed = float(new_speed) # Convertie la valeur choisit en float pour la conparaison
        if new_speed <= 1.0 and new_speed >= -1.0: # Compare la variable new_speed pour quel sois obligatoirement entre -1.0 et 1.0 
            return new_speed #si c'est oui alors on envoie directement la valeur
        else: 
            while new_speed > 1.0 or new_speed < -1.0: # Si la valeur n'est pas bonne nous rentrons dans un while et t'en que la variable new_speed n'est pas entre -1.0 et 1.0 alors on demande a l'utilisateur de nouveau
                new_speed = input("Erreur : La consigne doit être entre -1.0 et 1.0 : ") #redemande a l'utilisateur la valeur qu'il souhaite
                new_speed = float(new_speed) # Convertie la valeur choisit en float pour la conparaison
            return new_speed

    def calculerRapportCyclique(self):
        speed = self.speed
        if speed == 0.0:
            dureeEtatHaut = 1.5
        elif speed > 0.0:
            dureeEtatHaut = 1.5 + speed * (2.0 - 1.5) # Interpolation vers 2 ms
        else:
            dureeEtatHaut = 1.5 + speed * (1.3 - 1.5) # Interpolation vers 1.3 ms
        
        return (dureeEtatHaut / 20.0) * 100.0 # Convertion en %

    def genererSignalPWM(branch_moteur, rapportCyclique):
        #avoir une periode de 50 ms
        # print(Pilote.micros())
        debutCycle = time.time()
        dureeEtatHaut = ((rapportCyclique / 100.0) * Pilote.periode)
        actuel = time.time()

        if (actuel - debutCycle < dureeEtatHaut):
            PWM = 1
        else:
            PWM = 0
        
        if (actuel - debutCycle >= Pilote.periode):
            debutCycle = actuel
        
        return PWM