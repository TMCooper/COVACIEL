import serial
import threading
import time
from collections import namedtuple

# Structure pour stocker un point LIDAR
LidarPoint = namedtuple("LidarPoint", ["angle", "distance", "confidence", "timestamp"])

# Constantes de protocole LD06
PACKET_LEN           = 47
NUM_POINTS           = 12
CONFIDENCE_THRESHOLD = 50  # Seuil minimal de confiance

# Table CRC8
CRC_TABLE = [
    0x00, 0x4d, 0x9a, 0xd7, 0x79, 0x34, 0xe3, 0xae, 0xf2, 0xbf, 0x68, 0x25, 0x8b, 0xc6, 0x11, 0x5c,
    0xa9, 0xe4, 0x33, 0x7e, 0xd0, 0x9d, 0x4a, 0x07, 0x5b, 0x16, 0xc1, 0x8c, 0x22, 0x6f, 0xb8, 0xf5,
    0x1f, 0x52, 0x85, 0xc8, 0x66, 0x2b, 0xfc, 0xb1, 0xed, 0xa0, 0x77, 0x3a, 0x94, 0xd9, 0x0e, 0x43,
    0xb6, 0xfb, 0x2c, 0x61, 0xcf, 0x82, 0x55, 0x18, 0x44, 0x09, 0xde, 0x93, 0x3d, 0x70, 0xa7, 0xea,
    0x3e, 0x73, 0xa4, 0xe9, 0x47, 0x0a, 0xdd, 0x90, 0xcc, 0x81, 0x56, 0x1b, 0xb5, 0xf8, 0x2f, 0x62,
    0x97, 0xda, 0x0d, 0x40, 0xee, 0xa3, 0x74, 0x39, 0x65, 0x28, 0xff, 0xb2, 0x1c, 0x51, 0x86, 0xcb,
    0x21, 0x6c, 0xbb, 0xf6, 0x58, 0x15, 0xc2, 0x8f, 0xd3, 0x9e, 0x49, 0x04, 0xaa, 0xe7, 0x30, 0x7d,
    0x88, 0xc5, 0x12, 0x5f, 0xf1, 0xbc, 0x6b, 0x26, 0x7a, 0x37, 0xe0, 0xad, 0x03, 0x4e, 0x99, 0xd4,
    0x7c, 0x31, 0xe6, 0xab, 0x05, 0x48, 0x9f, 0xd2, 0x8e, 0xc3, 0x14, 0x59, 0xf7, 0xba, 0x6d, 0x20,
    0xd5, 0x98, 0x4f, 0x02, 0xac, 0xe1, 0x36, 0x7b, 0x27, 0x6a, 0xbd, 0xf0, 0x5e, 0x13, 0xc4, 0x89,
    0x63, 0x2e, 0xf9, 0xb4, 0x1a, 0x57, 0x80, 0xcd, 0x91, 0xdc, 0x0b, 0x46, 0xe8, 0xa5, 0x72, 0x3f,
    0xca, 0x87, 0x50, 0x1d, 0xb3, 0xfe, 0x29, 0x64, 0x38, 0x75, 0xa2, 0xef, 0x41, 0x0c, 0xdb, 0x96,
    0x42, 0x0f, 0xd8, 0x95, 0x3b, 0x76, 0xa1, 0xec, 0xb0, 0xfd, 0x2a, 0x67, 0xc9, 0x84, 0x53, 0x1e,
    0xeb, 0xa6, 0x71, 0x3c, 0x92, 0xdf, 0x08, 0x45, 0x19, 0x54, 0x83, 0xce, 0x60, 0x2d, 0xfa, 0xb7,
    0x5d, 0x10, 0xc7, 0x8a, 0x24, 0x69, 0xbe, 0xf3, 0xaf, 0xe2, 0x35, 0x78, 0xd6, 0x9b, 0x4c, 0x01,
    0xf4, 0xb9, 0x6e, 0x23, 0x8d, 0xc0, 0x17, 0x5a, 0x06, 0x4b, 0x9c, 0xd1, 0x7f, 0x32, 0xe5, 0xa8
] + [0] * (256 - 32)


class LidarKit:
    """
    Gestionnaire LIDAR LD06 thread-safe avec pyserial.
    Ouvre le port en __init__, ferme dans __del__, lit en thread daemon.
    """
    def __init__(self, port="/dev/ttyS0", baudrate=230400, timeout=0.01, debug=False):
        self.port     = port
        self.baudrate = baudrate
        self.timeout  = timeout
        self.debug    = debug

        # Initialisation du port série
        self.ser = serial.Serial(port, baudrate, timeout=timeout)

        # Données partagées
        self._angle_map = [-1.0] * 360
        self._points    = []
        self._lock      = threading.Lock()

        self._running = False
        self._thread  = None

    def __del__(self):
        # Arrêt et fermeture automatiques
        self.stop()
        if self.ser and self.ser.is_open:
            self.ser.close()

    @staticmethod
    def _crc8(buf: bytes) -> int:
        crc = 0
        for b in buf[:46]:
            crc = CRC_TABLE[(crc ^ b) & 0xFF]
        return crc

    def start(self) -> bool:
        """Démarre la lecture continue en thread daemon."""
        if self._running:
            return False
        self._running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()
        return True

    def stop(self):
        """Arrête le thread de lecture."""
        self._running = False
        if self._thread:
            self._thread.join()
            self._thread = None

    def get_points(self):
        """Renvoie et vide la liste des points fraîchement lus."""
        with self._lock:
            pts = self._points[:]
            self._points.clear()
        return pts

    def get_angle_map(self):
        """Renvoie une copie du tableau angle→distance (mm)."""
        with self._lock:
            return self._angle_map[:]

    def _read_loop(self):
        """Boucle interne : synchronisation, lecture et parsing des paquets."""
        while self._running:
            header = self.ser.read(1)
            if not header or header[0] != 0x54:
                continue

            pkt = bytearray(header) + self.ser.read(PACKET_LEN - 1)
            if len(pkt) != PACKET_LEN:
                if self.debug:
                    print("Trame incomplète, taille", len(pkt))
                continue

            if self._crc8(pkt) != pkt[46]:
                if self.debug:
                    print("CRC invalide, ignore")
                continue

            start_angle = int.from_bytes(pkt[4:6],  "little") / 100.0
            end_angle   = int.from_bytes(pkt[42:44], "little") / 100.0
            timestamp   = int.from_bytes(pkt[44:46], "little")
            diff  = (end_angle - start_angle + 360.0) % 360.0
            step  = diff / (NUM_POINTS - 1)

            with self._lock:
                for i in range(NUM_POINTS):
                    j = 6 + 3 * i
                    dist_m = int.from_bytes(pkt[j:j+2], "little") / 1000.0
                    conf   = pkt[j+2]
                    angle  = (start_angle + i * step) % 360.0
                    if conf >= CONFIDENCE_THRESHOLD:
                        idx = int(angle)
                        self._angle_map[idx] = dist_m * 1000.0
                        self._points.append(
                            LidarPoint(angle, dist_m, conf, timestamp)
                        )

            # Légère pause pour éviter le 100% CPU
            time.sleep(0.001)
