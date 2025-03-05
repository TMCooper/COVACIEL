import time
import RPi.GPIO as gpio

class Pilote():
    speed = float
    direction = float

    branch_moteur = int #Branche moteur 27
    branch_direction = int #Branche pour la direction 28

    periode = 20000 # Periode de 50 ms en microsecondes

    gpio.setup(branch_direction, gpio.OUT) #Configuration de la branche moteur en sortie
    servoDirection = gpio.PWM(branch_direction, 50) #creation d'un PWM sur la branche 28 pour le moteur
    servoDirection(0) #Arret du PWM

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
        self.direction = Pilote.verificationEntrer() #ajuste la direction
        angleServo = map(self.direction * 100, -100, 100, 0, 180) #converti la direction entre -1.0 et 1.0 en angle
        Pilote.servoDirection.ChangeDutyCycle(angleServo) #ecriture de l'angle sur le servo moteur
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
                new_speed = float(new_speed) # Convertie la valeur choisit en float pour la comparaison
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
        # gpio.setup(branch_moteur, gpio.OUT)
        # print(Pilote.micros())
        debutCycle = time.time()
        dureeEtatHaut = ((rapportCyclique / 100.0) * Pilote.periode)
        actuel = time.time()

        # Gpio peut être a ecrire ailleur 

        if (actuel - debutCycle < dureeEtatHaut):
            PWM = 1
            gpio.output(branch_moteur, gpio.HIGH)
        else:
            PWM = 0
            gpio.output(branch_moteur, gpio.LOW)
        
        if (actuel - debutCycle >= Pilote.periode):
            debutCycle = actuel
        
        return PWM