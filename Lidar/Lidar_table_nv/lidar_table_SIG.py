import serial
import threading
import RPi.GPIO as GPIO
import time

# Constantes pour le décodage des trames et contrôle
PACKET_LEN = 47          # Longueur d'une trame de données Lidar
NUM_POINTS = 12          # Nombre de points de distance par trame
CONFIDENCE_THRESHOLD = 50  # Seuil de confiance minimum pour une mesure valide
PWM_GPIO = 12  # GPIO18 / Broche 12

# Table CRC8 pour vérifier l'intégrité des trames
CRC_TABLE = [
    0x00, 0x4d, 0x9a, 0xd7, 0x79, 0x34, 0xe3, 0xae, 0xf2, 0xbf, 0x68, 0x25,
    0x8b, 0xc6, 0x11, 0x5c, 0xa9, 0xe4, 0x33, 0x7e, 0xd0, 0x9d, 0x4a, 0x07,
    0x5b, 0x16, 0xc1, 0x8c, 0x22, 0x6f, 0xb8, 0xf5, 0x1f, 0x52, 0x85, 0xc8,
    0x66, 0x2b, 0xfc, 0xb1, 0xed, 0xa0, 0x77, 0x3a, 0x94, 0xd9, 0x0e, 0x43,
    0xb6, 0xfb, 0x2c, 0x61, 0xcf, 0x82, 0x55, 0x18, 0x44, 0x09, 0xde, 0x93,
    0x3d, 0x70, 0xa7, 0xea, 0x3e, 0x73, 0xa4, 0xe9, 0x47, 0x0a, 0xdd, 0x90,
    0xcc, 0x81, 0x56, 0x1b, 0xb5, 0xf8, 0x2f, 0x62, 0x97, 0xda, 0x0d, 0x40,
    0xee, 0xa3, 0x74, 0x39, 0x65, 0x28, 0xff, 0xb2, 0x1c, 0x51, 0x86, 0xcb,
    0x21, 0x6c, 0xbb, 0xf6, 0x58, 0x15, 0xc2, 0x8f, 0xd3, 0x9e, 0x49, 0x04,
    0xaa, 0xe7, 0x30, 0x7d, 0x88, 0xc5, 0x12, 0x5f, 0xf1, 0xbc, 0x6b, 0x26,
    0x7a, 0x37, 0xe0, 0xad, 0x03, 0x4e, 0x99, 0xd4, 0x7c, 0x31, 0xe6, 0xab,
    0x05, 0x48, 0x9f, 0xd2, 0x8e, 0xc3, 0x14, 0x59, 0xf7, 0xba, 0x6d, 0x20,
    0xd5, 0x98, 0x4f, 0x02, 0xac, 0xe1, 0x36, 0x7b, 0x27, 0x6a, 0xbd, 0xf0,
    0x5e, 0x13, 0xc4, 0x89, 0x63, 0x2e, 0xf9, 0xb4, 0x1a, 0x57, 0x80, 0xcd,
    0x91, 0xdc, 0x0b, 0x46, 0xe8, 0xa5, 0x72, 0x3f, 0xca, 0x87, 0x50, 0x1d,
    0xb3, 0xfe, 0x29, 0x64, 0x38, 0x75, 0xa2, 0xef, 0x41, 0x0c, 0xdb, 0x96,
    0x42, 0x0f, 0xd8, 0x95, 0x3b, 0x76, 0xa1, 0xec, 0xb0, 0xfd, 0x2a, 0x67,
    0xc9, 0x84, 0x53, 0x1e, 0xeb, 0xa6, 0x71, 0x3c, 0x92, 0xdf, 0x08, 0x45,
    0x19, 0x54, 0x83, 0xce, 0x60, 0x2d, 0xfa, 0xb7, 0x5d, 0x10, 0xc7, 0x8a,
    0x24, 0x69, 0xbe, 0xf3, 0xaf, 0xe2, 0x35, 0x78, 0xd6, 0x9b, 0x4c, 0x01,
    0xf4, 0xb9, 0x6e, 0x23, 0x8d, 0xc0, 0x17, 0x5a, 0x06, 0x4b, 0x9c, 0xd1,
    0x7f, 0x32, 0xe5, 0xa8
]

class LidarKit:
    def __init__(self, port="/dev/ttyS0", baudrate=230400, debug=False):
        self.port = port
        self.baudrate = baudrate
        self.debug = debug
        self.ser = None             # Port série
        self.running = False        # État du thread de lecture
        self.thread = None          # Thread de lecture des données
        self.angle_distance_map = [-1.0] * 360  # Tableau des distances indexées par angle (0 à 359)
        self.lock = threading.Lock()           # Verrou pour accès concurrent
        self.pwm_pin = PWM_GPIO                # Broche PWM

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pwm_pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pwm_pin, 1000)  # 1 kHz
        self.pwm.start(0)                        # PWM à 0% au départ

        # Liste de points récents 
        self.points = []

    def _calc_crc(self, data):
        crc = 0
        for b in data[:46]:                   # CRC calculé sur les 46 premiers octets
            crc = CRC_TABLE[(crc ^ b) & 0xFF]
        return crc

    def open(self):
        self.ser = serial.Serial(self.port, self.baudrate, timeout=0.01)   # Ouverture du port série


    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()               # Fermeture propre du port série

    def start(self):
        if self.running:
            return False
        self.running = True
        self.open()                        # Active la liaison série
        self._set_pwm_max()                # Lance le moteur lidar
        self.thread = threading.Thread(target=self._read_loop, daemon=True)   # Lancement du thread de lecture
        self.thread.start()
        return True

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()      # Attend la fin du thread
        self.close()
        self.pwm.stop()             # Coupe le signal PWM (arrêt moteur)


    def get_angle_map(self):
        with self.lock:
            return self.angle_distance_map.copy()    # Retourne une copie des distances par angle


    def get_distance_at_angles(self, angles):
        with self.lock:
            return [self.angle_distance_map[a % 360] if 0 <= a < 360 else -1.0 for a in angles]

    def _read_loop(self):
        while self.running:
            header = self.ser.read(1)    # Lecture d'un octet
            if not header or header[0] != 0x54:
                continue                 # Attend un octet de début valide
            raw = bytearray(header + self.ser.read(PACKET_LEN - 1))       # Lit le reste de la trame
            if len(raw) != PACKET_LEN or self._calc_crc(raw) != raw[46]:
                continue                 # Vérifie longueur et validité CRC
             # Calcul des angles de début et de fin de trame
            start_angle = int.from_bytes(raw[4:6], "little") / 100.0
            end_angle = int.from_bytes(raw[42:44], "little") / 100.0
            step = ((end_angle - start_angle + 360.0) % 360.0) / (NUM_POINTS - 1)
            # Extraction des 12 mesures dans la trame
            for i in range(NUM_POINTS):
                offset = 6 + i * 3
                dist = int.from_bytes(raw[offset:offset+2], "little") / 1000.0
                conf = raw[offset + 2]
                if conf < CONFIDENCE_THRESHOLD or dist <= 0:
                    continue
                angle_index = int((start_angle + i * step) % 360)
                with self.lock:
                    self.angle_distance_map[angle_index] = dist
