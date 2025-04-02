import matplotlib.pyplot as plt
import numpy as np
import serial
from enum import Enum
import struct
import time
import argparse
import RPi.GPIO as GPIO

# ----------------------------------------------------------------------
# System Constants
# ----------------------------------------------------------------------
SERIAL_PORT = "/dev/ttyS0"
MEASUREMENTS_PER_PLOT = 1200
PLOT_MAX_RANGE = 4  # in meters
PLOT_AUTO_RANGE = False
PLOT_CONFIDENCE = True
PLOT_CONFIDENCE_COLOUR_MAP = "bwr_r"
PRINT_DEBUG = False

# Set the GPIO mode
GPIO.setmode(GPIO.BOARD)

# ----------------------------------------------------------------------
# Main Packet Format
# ----------------------------------------------------------------------
PACKET_LENGTH = 47
MEASUREMENT_LENGTH = 12
MESSAGE_FORMAT = "<xBHH" + "HB" * MEASUREMENT_LENGTH + "HHB"

class State(Enum):
    SYNC0 = 1
    SYNC1 = 2
    SYNC2 = 3
    LOCKED = 4
    UPDATE_PLOT = 5

# ----------------------------------------------------------------------
# PWM Controller
# ----------------------------------------------------------------------
class PWMController:
    def __init__(self, pin, pwm_frequency=2500):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)  # Ensure the pin is set up as an output
        self.pwm = GPIO.PWM(self.pin, pwm_frequency)  # Initialize PWM on the specified pin
        self.pwm_frequency = pwm_frequency

    def set_speed(self, duty_cycle):
        """Set the motor speed using PWM duty cycle (0-100%)."""
        if self.pwm is not None:
            self.pwm.start(duty_cycle)

    def stop(self):
        """Stop the PWM signal."""
        if self.pwm is not None:
            self.pwm.stop()
# ----------------------------------------------------------------------
# Lidar Controller
# ----------------------------------------------------------------------
class LidarController:
    def __init__(self, port=SERIAL_PORT, pwm_pin=12, pwm_frequency=3200, duty_cycle=100):
        self.lidar_serial = serial.Serial(port, 230400, timeout=0.05)
        self.measurements = []
        self.data = b''
        self.state = State.SYNC0
        self.pwm_controller = PWMController(pwm_pin, pwm_frequency)
        self.pwm_controller.set_speed(duty_cycle)  # Set initial speed
        self.running = True

    def run(self):
        try:
            while self.running:
                if self.state == State.SYNC0:
                    self.data = b''
                    self.measurements = []
                    if self.lidar_serial.read() == b'\x54':
                        self.data = b'\x54'
                        self.state = State.SYNC1
                elif self.state == State.SYNC1:
                    if self.lidar_serial.read() == b'\x2C':
                        self.state = State.SYNC2
                        self.data += b'\x2C'
                    else:
                        self.state = State.SYNC0
                elif self.state == State.SYNC2:
                    self.data += self.lidar_serial.read(PACKET_LENGTH - 2)
                    if len(self.data) != PACKET_LENGTH:
                        self.state = State.SYNC0
                        continue
                    self.measurements += LidarDataParser.parse_lidar_data(self.data)
                    self.state = State.LOCKED
                elif self.state == State.LOCKED:
                    self.data = self.lidar_serial.read(PACKET_LENGTH)
                    if self.data[0] != 0x54 or len(self.data) != PACKET_LENGTH:
                        print("WARNING: Serial sync lost")
                        self.state = State.SYNC0
                        continue
                    self.measurements += LidarDataParser.parse_lidar_data(self.data)
                    if len(self.measurements) > MEASUREMENTS_PER_PLOT:
                        self.state = State.UPDATE_PLOT
                elif self.state == State.UPDATE_PLOT:
                    self.plotter.update_plot(self.measurements)
                    self.state = State.LOCKED
                    self.measurements = []
        except KeyboardInterrupt:
            print("Program interrupted by user")
            self.running = False

    def get_measurements(self):
        """Retourne les mesures actuelles du LiDAR."""
        return self.measurements
# ----------------------------------------------------------------------
# Lidar Data Parser
# ----------------------------------------------------------------------
class LidarDataParser:
    @staticmethod
    def parse_lidar_data(data):
        length, speed, start_angle, *pos_data, stop_angle, timestamp, crc = \
            struct.unpack(MESSAGE_FORMAT, data)
        start_angle = float(start_angle) / 100.0
        stop_angle = float(stop_angle) / 100.0
        if stop_angle < start_angle:
            stop_angle += 360.0
        step_size = (stop_angle - start_angle) / (MEASUREMENT_LENGTH - 1)
        angle = [start_angle + step_size * i for i in range(0, MEASUREMENT_LENGTH)]
        distance = pos_data[0::2]
        confidence = pos_data[1::2]
        if PRINT_DEBUG:
            print(length, speed, start_angle, *pos_data, stop_angle, timestamp, crc)
        return list(zip(angle, distance, confidence))

# ----------------------------------------------------------------------
# Lidar AngleData Droite et gauche
# ----------------------------------------------------------------------
class LidarAngleDistance:
    """
    Classe permettant d'extraire la distance aux angles 0° et 180° depuis les données du LiDAR.
    """
    @staticmethod
    def get_distances(measurements):
        """
        Extrait la distance aux angles 0° et 180° à partir des mesures du LiDAR.
        :param measurements: Liste de tuples (angle, distance, confiance)
        :return: Dictionnaire contenant les distances pour les angles 0° et 180°
        """
        distances = {90: None, 270: None}
        
        for angle, distance, _ in measurements:
            if round(angle) == 90:
                distances[90] = distance
            elif round(angle) == 270:
                distances[270] = distance
        
        return distances


# ----------------------------------------------------------------------
# Lidar Plotter
# ----------------------------------------------------------------------
class LidarPlotter:
    def __init__(self):
        plt.ion()
        plt.rcParams['figure.figsize'] = [10, 10]
        plt.rcParams['lines.markersize'] = 2.0
        if PLOT_CONFIDENCE:
            self.graph = plt.scatter([], [], c=[], marker=".", vmin=0, vmax=255, cmap=PLOT_CONFIDENCE_COLOUR_MAP)
        else:
            self.graph = plt.plot([], [], ".")[0]
        self.graph.figure.canvas.mpl_connect('close_event', self.on_plot_close)
        plt.xlim(-PLOT_MAX_RANGE, PLOT_MAX_RANGE)
        plt.ylim(-PLOT_MAX_RANGE, PLOT_MAX_RANGE)
        self.key_points = None  # Stocke les points verts pour 0° et 180°

    def on_plot_close(self, event):
        self.running = False

    def update_plot(self, measurements):
        x, y, c = self.get_xyc_data(measurements)
        if PLOT_AUTO_RANGE:
            max_val = max([max(abs(x)), max(abs(y))]) * 1.2
            plt.xlim(-max_val, max_val)
            plt.ylim(-max_val, max_val)
        self.graph.remove()
        if PLOT_CONFIDENCE:
            self.graph = plt.scatter(x, y, c=c, marker=".", vmin=0, vmax=255, cmap=PLOT_CONFIDENCE_COLOUR_MAP)
        else:
            self.graph = plt.plot(x, y, 'b.')[0]
        
        self.highlight_key_angles(measurements)  # Ajout des points verts pour 0° et 180°
        plt.pause(0.00001)

    def highlight_key_angles(self, measurements):
        distances = LidarAngleDistance.get_distances(measurements)
        
        key_x, key_y = [], []
        for angle, distance in distances.items():
            if distance is not None:
                x = np.sin(np.radians(angle)) * (distance / 1000.0)
                y = np.cos(np.radians(angle)) * (distance / 1000.0)
                key_x.append(x)
                key_y.append(y)
        
        if self.key_points:
            self.key_points.remove()  # Supprime les anciens points verts
        self.key_points = plt.scatter(key_x, key_y, color='green', marker='o', s=100, label='Angles 0° & 180°')


    @staticmethod
    def get_xyc_data(measurements):
        angle = np.array([measurement[0] for measurement in measurements])
        distance = np.array([measurement[1] for measurement in measurements])
        confidence = np.array([measurement[2] for measurement in measurements])
        x = np.sin(np.radians(angle)) * (distance / 1000.0)
        y = np.cos(np.radians(angle)) * (distance / 1000.0)
        return x, y, confidence

# ----------------------------------------------------------------------
# Main Execution
# ----------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Lidar Controller with PWM pin selection.")
    parser.add_argument('--pwm_pin', type=int, default=12, help='GPIO pin for PWM output (default: 12)')
    parser.add_argument('--pwm_frequency', type=int, default=3200, help='PWM frequency in Hz (default: 3200)')
    parser.add_argument('--duty_cycle', type=float, default=100.0, help='PWM duty cycle in percentage (default: 100.0)')
    args = parser.parse_args()

    try:
        controller = LidarController(pwm_pin=args.pwm_pin, pwm_frequency=args.pwm_frequency, duty_cycle=args.duty_cycle)
        controller.plotter = LidarPlotter()  # Initialize the plotter after controller
        controller.run()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup completed")