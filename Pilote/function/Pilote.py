import RPi.GPIO as gpio
import threading 
from threading import Thread

Control_car_input = 0
Control_direction_input = 0
running = True

class Pilote():
    """
    Classe représentant un véhicule ou un système motorisé avec les attributs suivants :
    - speed (float) : vitesse actuelle du véhicule
    - direction (float) : direction actuelle (en degrés ou radians, selon le contexte)
    - branch_moteur (int) : identifiant ou numéro de la branche moteur
    - branch_direction (int) : identifiant ou numéro de la branche direction
    """

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
        self.lock = threading.Lock()

        # Création des thread de la class pilotte
        self.vit = Thread(target=Pilote.adjustSpeed, args=(self,))
        self.dir_t = Thread(target=Pilote.changeDirection, args=(self,))

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

        # Démarage des thread de la class
        self.vit.start()
        self.dir_t.start()

    def adjustSpeed(self):
        global Control_car_input

        while running:
            self.speed = Pilote.verificationEntrer(Control_car_input) # Ajuste la valeur de la vitesses entre -1.0 et 1.0
            rapportCyclique = Pilote.calculerRapportCyclique(self, 0) # Génère un rapport cyclique en fonction de self.speed
            Pilote.genererSignalPWM(self, 0, rapportCyclique) # Envoie le resultat du rapport cyclique a genererSignalPWM pour ajustement

        return
    
    def UpdateControlCar(self, new_value):
        """Méthode Pour effectuer la mise a jour de la vitesse de la voiture entre -1 et 1"""
        # Methode intermediaire pour ajuster la valeur de control_car_input 
        global Control_car_input
    
        with self.lock:
            Control_car_input = new_value

    def changeDirection(self):
        global Control_direction_input

        while running:
            self.direction = Pilote.verificationEntrer(Control_direction_input) # Ajuste de la vitesses pour la tenir entre -1 et 1
            rapportCyclique = Pilote.calculerRapportCyclique(self, 1) # Génère un rapport cyclique en fonction de self.direction
            Pilote.genererSignalPWM(self, 1, rapportCyclique) # Envoie le resultat du rapport cyclique a genererSinalPWM pour ajustement
        
        return

    def UpdateDirectionCar(self, new_value):
        """Méthode Pour effectuer la mise a jour de la direction de la voiture entre -1, 0 et 1"""
        # Methode intermediaire pour ajuster la valeur de control_direction_input 
        global Control_direction_input

        with self.lock:
            Control_direction_input = new_value
    
    def applyBrakes(self, entrer):
        """
        Méthode permettant d'activer rapidement les freins.

        Paramètre :
        - a (bool) : active les freins si True.
        """
        global Control_car_input
        if entrer == True:
            Control_car_input = 0 # True pour oui le frein est déclancher
        else:
            return None
    
    def getCurrentSpeed(self):
        """Affiche la valeur actuelle de speed"""
        return self.speed #retourne la valeur de speed (avec le thread un petit temps pour actialiser serait idéal) 
    
    def getCurrentDirection(self):
        """Affiche la valeur actuelle de direction"""
        return self.direction # retourne la valeur de la dirrection (avec le thread un petit temps pour actialiser serait idéal)
    
    def verificationEntrer(Control_car_input):
        """Verifie l'entrer de l'utilisateur pour qu'il sois obligatoirement entre -1 et 1"""
        new_speed = float(Control_car_input) # Convertie la valeur choisit en float pour la conparaison
        if new_speed <= 1.0 and new_speed >= -1.0: # Compare la variable new_speed pour quel sois obligatoirement entre -1.0 et 1.0 
            return new_speed #si c'est oui alors on envoie directement la valeur
        else: 
            while new_speed > 1.0 or new_speed < -1.0: # Si la valeur n'est pas bonne nous rentrons dans un while et t'en que la variable new_speed n'est pas entre -1.0 et 1.0 alors on demande a l'utilisateur de nouveau
                new_speed = input("Erreur : La consigne doit être entre -1.0 et 1.0 : ") #redemande a l'utilisateur la valeur qu'il souhaite
                new_speed = float(new_speed) # Convertie la valeur choisit en float pour la comparaison
            return new_speed

    def calculerRapportCyclique(self, ID):
        """Effectue le calcule pour le rapport cyclique moteur et direction"""
        periode = 20e-3  # Période de 20 ms (0.020 s)

        if ID == 0:
            speed = self.speed

            # Calcul du rapport cyclique pour la vitesse
            if speed >= 0:
                temps_haut = 1.5e-3 + speed * (2.0e-3 - 1.5e-3)  # Jusqu’à 2.0 ms
            else:
                temps_haut = 1.5e-3 + speed * (1.5e-3 - 1.3e-3)  # Jusqu’à 1.3 ms
            
            rapport_cyclique = (temps_haut / periode) * 100
            return rapport_cyclique
        
        elif ID == 1:
            direction = self.direction

            # Calcul du rapport cyclique pour la direction
            if direction == 0: 
                temps_haut_direction = 1.38e-3  # Temps haut de 1.38 ms
            elif direction == 1:
                temps_haut_direction = 1.54e-3  # Temps haut de 1.54 ms
            elif direction == -1:
                temps_haut_direction = 1.22e-3  # Temps haut de 1.22 ms
            
            rapport_cyclique = (temps_haut_direction / periode) * 100
            return rapport_cyclique
        
    def genererSignalPWM(self, ID, rapportCyclique):
        """
        Utilise un signal PWM pour l'injecter soit dans :
        - le moteur (ID = 0)
        - la direction (ID = 1)
        """
        # Génère un signial pwm pour le moteur si l'ID est 0
        if ID == 0:
            self.pwm.ChangeDutyCycle(rapportCyclique)
        # Génère un signial pwm pour le la direction si l'ID est 1
        elif ID == 1:
            self.dir.ChangeDutyCycle(rapportCyclique)
    
    def stop(self):
        """Effectue un arret propre des thread ainsi qu'un nettoyage du gpio"""
        # Arrete les threads ainsi que tous se qui est lier au gpio 
        global running ; running = False
        gpio.cleanup 
        self.dir.stop()
        self.pwm.stop()
        self.vit.join()
        self.dir_t.join()