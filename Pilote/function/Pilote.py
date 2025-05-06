import RPi.GPIO as gpio
import threading

class Pilote():
    speed = float
    direction = float

    branch_moteur = int # Branche moteur
    branch_direction = int # Branche pour la direction

    def __init__(self,speed, direction, branch_moteur, branch_direction): #Ajout de speed, direction, branch_moteur et branch_direction au "tableau" de self
        # Initialisation des differente variable essentiel
        self.speed = speed
        self.direction = direction
        self.branch_moteur = branch_moteur
        self.branch_direction = branch_direction
        

        # Définir le mode de numérotation des broches
        gpio.setmode(gpio.BOARD)

        # Definition des broche utiliser pour le moteur et la direction
        gpio.setup(self.branch_moteur, gpio.OUT)  # Configuration de la branche moteur en sortie
        gpio.setup(self.branch_direction, gpio.OUT) #Configuration de la branche dirrection en sortie

        # Initialisation de la broche moteur
        pwm = gpio.PWM(self.branch_moteur, 50)  # Fréquence de 50 Hz sur la branch moteur
        pwm.start(0)
        self.pwm = pwm

        # Initialisation de la broche direction 
        dir = gpio.PWM(self.branch_direction, 50) # Fréquence de 50 Hz sur la branch direction
        dir.start(0)
        self.dir = dir

        # print(type(self.lock))

    def adjustSpeed(self, Control_car_input):

        self.speed = Pilote.verificationEntrer(Control_car_input) #Ajuste la valeur de la vitesses entre -1.0 et 1.0
        rapportCyclique = Pilote.calculerRapportCyclique(self, 0)
        Pilote.genererSignalPWM(self, 0, rapportCyclique)

        return 

    def changeDirection(self, Control_direction_input):

        self.direction = Pilote.verificationEntrer(Control_direction_input) # Ajuste la direction
        rapportCyclique = Pilote.calculerRapportCyclique(self, 1) # Converti la direction entre -1.0 et 1.0
        Pilote.genererSignalPWM(self, 1, rapportCyclique) # Ecriture de l'angle sur le servo moteur
        
        return
    
    def applyBrakes(self, entrer):
        if entrer == True:
            self.pwm.ChangeDutyCycle(0)
            return True #True pour oui le frein est déclancher
        elif entrer == False:
            return False
    
    def getCurrentSpeed(self):
        return self.speed #retourne la valeur de speed 
    
    def getCurrentDirection(self):
        return self.direction # retourne la valeur de la dirrection
    
    def verificationEntrer(Control_car_input):
        new_speed = float(Control_car_input) # Convertie la valeur choisit en float pour la conparaison
        if new_speed <= 1.0 and new_speed >= -1.0: # Compare la variable new_speed pour quel sois obligatoirement entre -1.0 et 1.0 
            return new_speed #si c'est oui alors on envoie directement la valeur
        else: 
            while new_speed > 1.0 or new_speed < -1.0: # Si la valeur n'est pas bonne nous rentrons dans un while et t'en que la variable new_speed n'est pas entre -1.0 et 1.0 alors on demande a l'utilisateur de nouveau
                new_speed = input("Erreur : La consigne doit être entre -1.0 et 1.0 : ") #redemande a l'utilisateur la valeur qu'il souhaite
                new_speed = float(new_speed) # Convertie la valeur choisit en float pour la comparaison
            return new_speed

    def calculerRapportCyclique(self, ID):
        periode = 20e-3  # Période de 20 ms (0.020 s)

        if ID == 0:
            speed = self.speed

            # Calcul du rapport cyclique basé sur la vitesse
            if speed >= 0:
                temps_haut = 1.5e-3 + speed * (2.0e-3 - 1.5e-3)  # Jusqu’à 2.0 ms
            else:
                temps_haut = 1.5e-3 + speed * (1.5e-3 - 1.3e-3)  # Jusqu’à 1.3 ms
            
            rapport_cyclique = (temps_haut / periode) * 100
            return rapport_cyclique
        
        elif ID == 1:
            direction = self.direction

            # Calcul du rapport cyclique basé sur la direction
            if direction == 0: 
                temps_haut_direction = 1.38e-3  # Temps haut de 1.38 ms
            elif direction == 1:
                temps_haut_direction = 1.54e-3  # Temps haut de 1.54 ms
            elif direction == -1:
                temps_haut_direction = 1.22e-3  # Temps haut de 1.22 ms
            
            rapport_cyclique = (temps_haut_direction / periode) * 100
            return rapport_cyclique
        
    def genererSignalPWM(self, ID, rapportCyclique):
        if ID == 0:
            self.pwm.ChangeDutyCycle(rapportCyclique)
        elif ID == 1:
            self.dir.ChangeDutyCycle(rapportCyclique)
        return
    
    def stop(self):
        gpio.cleanup
        self.dir.stop()
        self.pwm.stop()