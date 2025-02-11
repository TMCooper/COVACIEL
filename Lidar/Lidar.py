import serial
import struct
import math

class LidarLD06:
    def __init__(self, port, baudrate=230400):
        """
        Initialise la connexion série avec le LiDAR LD06.
        :param port: Port série (ex: '/dev/ttyUSB0' ou 'COM3')
        :param baudrate: Débit binaire (par défaut 230400 pour le LD06)
        """
        self.serial_port = serial.Serial(port, baudrate, timeout=1)
        self.serial_port.flushInput()

    def read_frame(self):
        """
        Lit une trame de données du LiDAR.
        Le LD06 envoie des trames de 47 octets.
        """
        while True:
            # Chercher le début de la trame (0x54)
            if self.serial_port.read() == b'\x54':
                # Lire les 46 octets restants de la trame
                frame = self.serial_port.read(46)
                if len(frame) == 46:
                    return frame

    def parse_frame(self, frame):
        """
        Analyse une trame de données pour extraire les distances et les angles.
        :param frame: Trame de 46 octets
        :return: Liste de tuples (distance, angle)
        """
        data = []
        start_angle = (frame[1] + (frame[2] << 8)) / 100.0  # Angle de départ en degrés
        for i in range(12):  # 12 points de données par trame
            dist = frame[3 + 3 * i] + ((frame[4 + 3 * i] & 0x3F) << 8)  # Distance en mm
            intensity = frame[5 + 3 * i]  # Intensité (non utilisé ici)
            angle = start_angle + (i * 4.0)  # Angle en degrés
            data.append((dist, angle))
        return data

    def find_closest_object(self, data):
        """
        Trouve l'objet le plus proche dans les données analysées.
        :param data: Liste de tuples (distance, angle)
        :return: Distance et angle de l'objet le plus proche
        """
        closest_distance = float('inf')
        closest_angle = 0.0
        for dist, angle in data:
            if dist < closest_distance and dist > 0:  # Ignorer les distances nulles ou invalides
                closest_distance = dist
                closest_angle = angle
        return closest_distance, closest_angle

    def run(self):
        """
        Boucle principale pour lire et afficher les données du LiDAR.
        """
        try:
            while True:
                frame = self.read_frame()
                data = self.parse_frame(frame)
                closest_distance, closest_angle = self.find_closest_object(data)
                print(f"Objet le plus proche : Distance = {closest_distance / 1000.0:.2f} m, Angle = {closest_angle:.2f}°")
        except KeyboardInterrupt:
            print("Arrêt du programme.")
        finally:
            self.serial_port.close()

if __name__ == '__main__':
    # Remplacez '/dev/ttyUSB0' par le port série approprié
    lidar = LidarLD06(port='/dev/ttyUSB0')
    lidar.run()


