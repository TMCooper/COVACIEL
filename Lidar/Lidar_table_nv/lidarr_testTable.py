import serial
import threading
import time
import math
import os
import RPi.GPIO as GPIO

NUM_POINTS = 12
PACKET_LEN = 47
CONFIDENCE_THRESHOLD = 15
PWM_PIN = 12  # GPIO12 = pin physique 32

class LidarPoint:
    def __init__(self, angle, distance, confidence, timestamp):
        self.angle = angle
        self.distance = distance
        self.confidence = confidence
        self.timestamp = timestamp

class LidarKit:
    def __init__(self, port="/dev/ttyS0", debug=False):
        self.ser = serial.Serial(port, 230400, timeout=0.1)
        self.running = False
        self.lock = threading.Lock()
        self.angle_distance_table = [None] * 361
        self.debug = debug

        # Setup GPIO PWM
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PWM_PIN, GPIO.OUT)
        self.pwm = GPIO.PWM(PWM_PIN, 1000)  # 1 kHz
        self.pwm.start(0)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.read_loop)
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()
        self.ser.close()
        self.pwm.stop()
        GPIO.cleanup()

    def get_angle_distance_table(self):
        with self.lock:
            return self.angle_distance_table.copy()

    def set_pwm_duty_cycle(self, duty_cycle):
        if 0 <= duty_cycle <= 100:
            self.pwm.ChangeDutyCycle(duty_cycle)
        else:
            raise ValueError("Duty cycle doit être entre 0 et 100")

    def read_loop(self):
        while self.running:
            packet = self.ser.read(PACKET_LEN)
            if len(packet) != PACKET_LEN or packet[0] != 0x54:
                continue

            data = list(packet)
            if self.calc_crc8(data[:46]) != data[46]:
                if self.debug:
                    print("CRC invalide")
                continue

            start_angle = (data[4] + (data[5] << 8)) / 100.0
            end_angle = (data[42] + (data[43] << 8)) / 100.0
            timestamp = data[44] + (data[45] << 8)
            step = (end_angle - start_angle + 360.0) % 360.0 / (NUM_POINTS - 1)

            with self.lock:
                for i in range(NUM_POINTS):
                    offset = 6 + i * 3
                    dist = (data[offset] + (data[offset+1] << 8)) / 1000.0
                    conf = data[offset + 2]
                    angle = (start_angle + i * step) % 360.0

                    if conf >= CONFIDENCE_THRESHOLD:
                        angle_int = int(round(angle)) % 361
                        self.angle_distance_table[angle_int] = dist

    @staticmethod
    def calc_crc8(data):
        crc = 0
        for byte in data:
            crc ^= byte
            for _ in range(8):
                crc = (crc << 1) ^ 0x07 if crc & 0x80 else crc << 1
                crc &= 0xFF
        return crc

def display_table(angle_distance_table):
    os.system('clear')  # pour terminal Linux/macOS
    print("="*35)
    print(f"{'Angle (°)':<10} | {'Distance (cm)':<15}")
    print("-"*35)
    for angle in range(361):
        dist = angle_distance_table[angle]
        if dist is not None:
            print(f"{angle:<10} | {dist * 100:<15.2f}")
    print("="*35) 

if __name__ == "__main__":
    lidar = LidarKit(port="/dev/ttyS0", debug=False)
    lidar.start()

    try:
        while True:
            table = lidar.get_angle_distance_table()
            display_table(table)

            # PWM test dynamique
            lidar.set_pwm_duty_cycle(30)
            time.sleep(0.5)
            lidar.set_pwm_duty_cycle(70)
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Fin du programme.")
        lidar.stop()
