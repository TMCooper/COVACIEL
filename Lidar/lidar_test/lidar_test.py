import matplotlib.pyplot as plt
import numpy as np
import serial
import struct
import time
import argparse
import RPi.GPIO as GPIO
from enum import Enum

SERIAL_PORT = "/dev/ttyS0"
MEASUREMENTS_PER_PLOT = 1200
PLOT_MAX_RANGE = 4
PLOT_AUTO_RANGE = False
PLOT_CONFIDENCE = True
PLOT_CONFIDENCE_COLOUR_MAP = "bwr_r"
PRINT_DEBUG = False

GPIO.setmode(GPIO.BOARD)
PACKET_LENGTH = 47
MEASUREMENT_LENGTH = 12
MESSAGE_FORMAT = "<xBHH" + "HB" * MEASUREMENT_LENGTH + "HHB"

class LidarSystem:
    class State(Enum):
        SYNC0 = 1
        SYNC1 = 2
        SYNC2 = 3
        LOCKED = 4
        UPDATE_PLOT = 5

    def __init__(self, port=SERIAL_PORT, pwm_pin=12, pwm_frequency=4700, duty_cycle=100):
        self.lidar_serial = serial.Serial(port, 230400, timeout=0.05)
        self.measurements = []
        self.data = b''
        self.state = self.State.SYNC0
        self.running = True

        self.pwm_pin = pwm_pin
        self.pwm_frequency = pwm_frequency
        self.pwm = self._setup_pwm(pwm_pin, pwm_frequency)
        self.pwm.start(duty_cycle)

        self._init_plot()

    def _setup_pwm(self, pin, frequency):
        GPIO.setup(pin, GPIO.OUT)
        return GPIO.PWM(pin, frequency)

    def _init_plot(self):
        plt.ion()
        plt.rcParams['figure.figsize'] = [10, 10]
        plt.rcParams['lines.markersize'] = 2.0
        self.graph = None
        if PLOT_CONFIDENCE:
            self.graph = plt.scatter([], [], c=[], marker=".", vmin=0, vmax=255, cmap=PLOT_CONFIDENCE_COLOUR_MAP)
        else:
            self.graph = plt.plot([], [], ".")[0]
        self.graph.figure.canvas.mpl_connect('close_event', self._on_plot_close)
        plt.xlim(-PLOT_MAX_RANGE, PLOT_MAX_RANGE)
        plt.ylim(-PLOT_MAX_RANGE, PLOT_MAX_RANGE)
        self.key_points = None

    def _on_plot_close(self, event):
        self.running = False

    def _parse_lidar_data(self, data): # décode les données brutes
        length, speed, start_angle, *pos_data, stop_angle, timestamp, crc = struct.unpack(MESSAGE_FORMAT, data)
        start_angle /= 100.0
        stop_angle /= 100.0
        if stop_angle < start_angle:
            stop_angle += 360.0
        step_size = (stop_angle - start_angle) / (MEASUREMENT_LENGTH - 1)
        angles = [start_angle + step_size * i for i in range(MEASUREMENT_LENGTH)]
        distances = pos_data[0::2]
        confidences = pos_data[1::2]
        if PRINT_DEBUG:
            print(length, speed, start_angle, *pos_data, stop_angle, timestamp, crc)
        return list(zip(angles, distances, confidences))

    def _get_distances_90_270(self, measurements):
        distances = {90: None, 270: None}
        for angle, dist, _ in measurements:
            if round(angle) == 90:
                distances[90] = dist
            elif round(angle) == 270:
                distances[270] = dist
        return distances

    def _get_xyc_data(self, measurements): # convertit les mesures polaires (angle et distance )en données cartésiennes (x et y ) 
        angle = np.array([m[0] for m in measurements])
        distance = np.array([m[1] for m in measurements])
        confidence = np.array([m[2] for m in measurements])
        x = np.sin(np.radians(angle)) * (distance / 1000.0)
        y = np.cos(np.radians(angle)) * (distance / 1000.0)
        return x, y, confidence

    def _highlight_key_angles(self, measurements): # afficher les point vert gauche droite
        distances = self._get_distances_90_270(measurements)
        key_x, key_y = [], []
        for angle, distance in distances.items():
            if distance is not None:
                x = np.sin(np.radians(angle)) * (distance / 1000.0)
                y = np.cos(np.radians(angle)) * (distance / 1000.0)
                key_x.append(x)
                key_y.append(y)
        if self.key_points:
            self.key_points.remove()
        self.key_points = plt.scatter(key_x, key_y, color='green', marker='o', s=100)

    def _update_plot(self, measurements):
        x, y, c = self._get_xyc_data(measurements)
        if PLOT_AUTO_RANGE:
            max_val = max([max(abs(x)), max(abs(y))]) * 1.2
            plt.xlim(-max_val, max_val)
            plt.ylim(-max_val, max_val)
        self.graph.remove()
        if PLOT_CONFIDENCE:
            self.graph = plt.scatter(x, y, c=c, marker=".", vmin=0, vmax=255, cmap=PLOT_CONFIDENCE_COLOUR_MAP)
        else:
            self.graph = plt.plot(x, y, 'b.')[0]
        self._highlight_key_angles(measurements)
        plt.pause(0.00001)

    def run(self):
        try:
            while self.running:
                if self.state == self.State.SYNC0:
                    self.data = b''
                    self.measurements = []
                    if self.lidar_serial.read() == b'\x54':
                        self.data = b'\x54'
                        self.state = self.State.SYNC1

                elif self.state == self.State.SYNC1:
                    if self.lidar_serial.read() == b'\x2C':
                        self.state = self.State.SYNC2
                        self.data += b'\x2C'
                    else:
                        self.state = self.State.SYNC0

                elif self.state == self.State.SYNC2:
                    self.data += self.lidar_serial.read(PACKET_LENGTH - 2)
                    if len(self.data) != PACKET_LENGTH:
                        self.state = self.State.SYNC0
                        continue
                    self.measurements += self._parse_lidar_data(self.data)
                    self.state = self.State.LOCKED

                elif self.state == self.State.LOCKED:
                    self.data = self.lidar_serial.read(PACKET_LENGTH)
                    if self.data[0] != 0x54 or len(self.data) != PACKET_LENGTH:
                        print("WARNING: Serial sync lost")
                        self.state = self.State.SYNC0
                        continue
                    self.measurements += self._parse_lidar_data(self.data)
                    if len(self.measurements) > MEASUREMENTS_PER_PLOT:
                        self.state = self.State.UPDATE_PLOT

                elif self.state == self.State.UPDATE_PLOT:
                    self._update_plot(self.measurements)
                    self.state = self.State.LOCKED
                    self.measurements = []

        except KeyboardInterrupt:
            print("Program interrupted by user")
            self.running = False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Lidar Controller with PWM pin selection.")
    parser.add_argument('--pwm_pin', type=int, default=12)
    parser.add_argument('--pwm_frequency', type=int, default=3200)
    parser.add_argument('--duty_cycle', type=float, default=100.0)
    args = parser.parse_args()

    try:
        lidar_system = LidarSystem(pwm_pin=args.pwm_pin, pwm_frequency=args.pwm_frequency, duty_cycle=args.duty_cycle)
        lidar_system.run()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup completed")
