import serial
import threading
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import namedtuple

LidarPoint = namedtuple("LidarPoint", ["angle", "distance", "confidence", "timestamp"])

PACKET_LEN = 47
NUM_POINTS = 12
CONFIDENCE_THRESHOLD = 50
PWM_GPIO = 12  # GPIO18 / Broche 12  # Minimum de confiance pour accepter un point

CRC_TABLE = [
    0x00, 0x4d, 0x9a, 0xd7, 0x79, 0x34, 0xe3,
    0xae, 0xf2, 0xbf, 0x68, 0x25, 0x8b, 0xc6, 0x11, 0x5c, 0xa9, 0xe4, 0x33,
    0x7e, 0xd0, 0x9d, 0x4a, 0x07, 0x5b, 0x16, 0xc1, 0x8c, 0x22, 0x6f, 0xb8,
    0xf5, 0x1f, 0x52, 0x85, 0xc8, 0x66, 0x2b, 0xfc, 0xb1, 0xed, 0xa0, 0x77,
    0x3a, 0x94, 0xd9, 0x0e, 0x43, 0xb6, 0xfb, 0x2c, 0x61, 0xcf, 0x82, 0x55,
    0x18, 0x44, 0x09, 0xde, 0x93, 0x3d, 0x70, 0xa7, 0xea, 0x3e, 0x73, 0xa4,
    0xe9, 0x47, 0x0a, 0xdd, 0x90, 0xcc, 0x81, 0x56, 0x1b, 0xb5, 0xf8, 0x2f,
    0x62, 0x97, 0xda, 0x0d, 0x40, 0xee, 0xa3, 0x74, 0x39, 0x65, 0x28, 0xff,
    0xb2, 0x1c, 0x51, 0x86, 0xcb, 0x21, 0x6c, 0xbb, 0xf6, 0x58, 0x15, 0xc2,
    0x8f, 0xd3, 0x9e, 0x49, 0x04, 0xaa, 0xe7, 0x30, 0x7d, 0x88, 0xc5, 0x12,
    0x5f, 0xf1, 0xbc, 0x6b, 0x26, 0x7a, 0x37, 0xe0, 0xad, 0x03, 0x4e, 0x99,
    0xd4, 0x7c, 0x31, 0xe6, 0xab, 0x05, 0x48, 0x9f, 0xd2, 0x8e, 0xc3, 0x14,
    0x59, 0xf7, 0xba, 0x6d, 0x20, 0xd5, 0x98, 0x4f, 0x02, 0xac, 0xe1, 0x36,
    0x7b, 0x27, 0x6a, 0xbd, 0xf0, 0x5e, 0x13, 0xc4, 0x89, 0x63, 0x2e, 0xf9,
    0xb4, 0x1a, 0x57, 0x80, 0xcd, 0x91, 0xdc, 0x0b, 0x46, 0xe8, 0xa5, 0x72,
    0x3f, 0xca, 0x87, 0x50, 0x1d, 0xb3, 0xfe, 0x29, 0x64, 0x38, 0x75, 0xa2,
    0xef, 0x41, 0x0c, 0xdb, 0x96, 0x42, 0x0f, 0xd8, 0x95, 0x3b, 0x76, 0xa1,
    0xec, 0xb0, 0xfd, 0x2a, 0x67, 0xc9, 0x84, 0x53, 0x1e, 0xeb, 0xa6, 0x71,
    0x3c, 0x92, 0xdf, 0x08, 0x45, 0x19, 0x54, 0x83, 0xce, 0x60, 0x2d, 0xfa,
    0xb7, 0x5d, 0x10, 0xc7, 0x8a, 0x24, 0x69, 0xbe, 0xf3, 0xaf, 0xe2, 0x35,
    0x78, 0xd6, 0x9b, 0x4c, 0x01, 0xf4, 0xb9, 0x6e, 0x23, 0x8d, 0xc0, 0x17,
    0x5a, 0x06, 0x4b, 0x9c, 0xd1, 0x7f, 0x32, 0xe5, 0xa8
] 

class LidarKit:
    def __init__(self, port="/dev/ttyS0", baudrate=230400, debug=False):
        self.port = port
        self.baudrate = baudrate
        self.debug = debug
        self.ser = None
        self.running = False
        self.thread = None
        self.points = []
        self.lock = threading.Lock()
        self.pwm_pin = PWM_GPIO

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pwm_pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pwm_pin, 1000)  # 1 kHz
        self.pwm.start(0)

    def _set_pwm_max(self):
        self.pwm.ChangeDutyCycle(100)
        if self.debug:
            print("PWM à 100 %")

    def open(self):
        self.ser = serial.Serial(self.port, self.baudrate, timeout=0.1)

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()

    def calc_crc8(self, data):
        crc = 0
        for b in data[:46]:
            crc = CRC_TABLE[(crc ^ b) & 0xFF]
        return crc

    def start(self):
        if self.running:
            return False
        self.running = True
        self.open()
        self.thread = threading.Thread(target=self.read_loop)
        self.thread.start()
        return True

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self.close()

    def get_points(self):
        with self.lock:
            pts = self.points.copy()
            self.points.clear()
        return pts

    def read_loop(self):
        while self.running:
            while self.running:
                byte = self.ser.read(1)
                if byte and byte[0] == 0x54:
                    break

            packet = bytearray()
            packet.append(0x54)
            while self.running and len(packet) < PACKET_LEN:
                more = self.ser.read(PACKET_LEN - len(packet))
                packet.extend(more)

            if len(packet) < PACKET_LEN:
                continue

            if self.calc_crc8(packet) != packet[46]:
                if self.debug:
                    print("Bad checksum, skipping...")
                continue

            start_angle = int.from_bytes(packet[4:6], "little") / 100.0
            end_angle = int.from_bytes(packet[42:44], "little") / 100.0
            timestamp = int.from_bytes(packet[44:46], "little")

            step = (end_angle - start_angle + 360.0 if end_angle < start_angle else end_angle - start_angle) / (NUM_POINTS - 1)
            new_points = []

            for i in range(NUM_POINTS):
                j = 6 + 3 * i
                dist = int.from_bytes(packet[j:j+2], "little") / 1000.0
                conf = packet[j+2]
                angle = (start_angle + i * step) % 360

                if conf >= CONFIDENCE_THRESHOLD:
                    new_points.append(LidarPoint(angle, dist, conf, timestamp))

            with self.lock:
                self.points.extend(new_points)


class LidarMap:
    def __init__(self, lidar: LidarKit, max_range=5.0):
        self.lidar = lidar
        self.max_range = max_range
        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.sc = self.ax.scatter([], [], s=10, c='blue', alpha=0.7)

        self.ax.set_xlim(-max_range, max_range)
        self.ax.set_ylim(-max_range, max_range)
        self.ax.set_xlabel("X (m)")
        self.ax.set_ylabel("Y (m)")
        self.ax.set_title("Carte LIDAR LD06 - Vue cartésienne")
        self.ax.grid(True)
        self.ax.set_aspect('equal')

    def update(self, frame):
        points = self.lidar.get_points()
        if not points:
            return self.sc,

        xs = [p.distance * np.cos(np.radians(p.angle)) for p in points]
        ys = [p.distance * np.sin(np.radians(p.angle)) for p in points]
        self.sc.set_offsets(np.c_[xs, ys])
        return self.sc,

    def run(self):
        ani = animation.FuncAnimation(self.fig, self.update, interval=100, blit=True)
        plt.show()


if __name__ == "__main__":
    lidar = LidarKit("/dev/ttyS0", debug=False)
    lidar.start()

    try:
        map_display = LidarMap(lidar)
        map_display.run()
    except KeyboardInterrupt:
        print("Fermeture par l'utilisateur...")
    finally:
        lidar.stop()
