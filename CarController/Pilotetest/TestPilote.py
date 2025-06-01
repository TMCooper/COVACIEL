import RPi.GPIO as gpio

class Pilote:
    def __init__(self, speed, direction, branch_moteur, branch_direction):
        self.speed = speed
        self.direction = direction
        self.branch_moteur = branch_moteur
        self.branch_direction = branch_direction

        gpio.setmode(gpio.BOARD)
        gpio.setwarnings(False)

        gpio.setup(self.branch_moteur, gpio.OUT)
        gpio.setup(self.branch_direction, gpio.OUT)

        # Fréquence différente selon moteur ou servo
        self.pwm = gpio.PWM(self.branch_moteur, 100)  # 100 Hz pour propulsion
        self.pwm.start(0)

        self.dir = gpio.PWM(self.branch_direction, 50)  # 50 Hz pour servo
        self.dir.start(7.5)  # Centre

    def adjustSpeed(self, Control_car_input):
        self.speed = self.verificationEntrer(Control_car_input)
        rapportCyclique = self.calculerRapportCyclique(0)
        self.genererSignalPWM(0, rapportCyclique)

    def changeDirection(self, Control_direction_input):
        self.direction = self.verificationEntrer(Control_direction_input)
        rapportCyclique = self.calculerRapportCyclique(1)
        self.genererSignalPWM(1, rapportCyclique)

    def getCurrentSpeed(self):
        return self.speed

    def getCurrentDirection(self):
        return self.direction

    @staticmethod
    def verificationEntrer(valeur):
        try:
            new_val = float(valeur)
        except ValueError:
            print("❌ Entrée invalide. Valeur forcée à 0.")
            return 0.0
        if new_val > 1.0:
            return 1.0
        elif new_val < -1.0:
            return -1.0
        return new_val

    def calculerRapportCyclique(self, ID):
        periode = 20e-3  # 20 ms

        if ID == 0:  # Moteur
            speed = self.speed
            # Simule signal PWM proportionnel (pas vraiment pour servo ici)
            duty = abs(speed) * 100
            return duty

        elif ID == 1:  # Direction (servo)
            direction = self.direction
            # Convertit -1.0 à 1.0 vers 5% à 10% duty cycle
            rapport_cyclique = 7.5 + (direction * 2.5)
            return rapport_cyclique

    def genererSignalPWM(self, ID, rapportCyclique):
        if ID == 0:
            self.pwm.ChangeDutyCycle(rapportCyclique)
        elif ID == 1:
            self.dir.ChangeDutyCycle(rapportCyclique)

    def applyBrakes(self, etat):
        if etat:
            self.pwm.ChangeDutyCycle(0)
            return True
        else:
            return False

    def stop(self):
        self.pwm.ChangeDutyCycle(0)
        self.dir.ChangeDutyCycle(7.5)
        self.pwm.stop()
        self.dir.stop()
        gpio.cleanup()
        print("🛑 PWM arrêté et GPIO nettoyé.")
