import numpy as np
import matplotlib.pyplot as plt
import serial
from enum import Enum
import struct
import csv

# ----------------------------------------------------------------------
# System Constants
# ----------------------------------------------------------------------
SERIAL_PORT = "/dev/ttyS0"
MEASUREMENTS_PER_PLOT = 1100
PLOT_MAX_RANGE = 4  # in meters
PLOT_AUTO_RANGE = False
PLOT_CONFIDENCE = True
PLOT_CONFIDENCE_COLOUR_MAP = "bwr_r"
PRINT_DEBUG = False

# ----------------------------------------------------------------------
# Main Packet Format
# ----------------------------------------------------------------------
PACKET_LENGTH = 47
MEASUREMENT_LENGTH = 12
MESSAGE_FORMAT = "<xBHH" + "HB" * MEASUREMENT_LENGTH + "HHB"

State = Enum("State", ["SYNC0", "SYNC1", "SYNC2", "LOCKED", "UPDATE_PLOT"])

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

def get_xyc_data(measurements):
    angle = np.array([measurement[0] for measurement in measurements])
    distance = np.array([measurement[1] for measurement in measurements])
    confidence = np.array([measurement[2] for measurement in measurements])
    x = np.sin(np.radians(angle)) * (distance / 1000.0)
    y = np.cos(np.radians(angle)) * (distance / 1000.0)
    return x, y, confidence

def save_to_csv(measurements, filename="lidar_data.csv"):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Angle", "Distance (mm)", "Confidence"])
        for measurement in measurements:
            writer.writerow(measurement)

running = True

def on_plot_close(event):
    global running
    running = False

if __name__ == "__main__":
    lidar_serial = serial.Serial(SERIAL_PORT, 230400, timeout=0.5)
    measurements = []
    data = b''
    state = State.SYNC0

    plt.ion()
    plt.rcParams['figure.figsize'] = [10, 10]
    plt.rcParams['lines.markersize'] = 2.0
    if PLOT_CONFIDENCE:
        graph = plt.scatter([], [], c=[], marker=".", vmin=0, vmax=255, cmap=PLOT_CONFIDENCE_COLOUR_MAP)
    else:
        graph = plt.plot([], [], ".")[0]
    graph.figure.canvas.mpl_connect('close_event', on_plot_close)
    plt.xlim(-PLOT_MAX_RANGE, PLOT_MAX_RANGE)
    plt.ylim(-PLOT_MAX_RANGE, PLOT_MAX_RANGE)

    while running:
        if state == State.SYNC0:
            data = b''
            measurements = []
            if lidar_serial.read() == b'\x54':
                data = b'\x54'
                state = State.SYNC1
        elif state == State.SYNC1:
            if lidar_serial.read() == b'\x2C':
                state = State.SYNC2
                data += b'\x2C'
            else:
                state = State.SYNC0
        elif state == State.SYNC2:
            data += lidar_serial.read(PACKET_LENGTH - 2)
            if len(data) != PACKET_LENGTH:
                state = State.SYNC0
                continue
            measurements += parse_lidar_data(data)
            state = State.LOCKED
        elif state == State.LOCKED:
            data = lidar_serial.read(PACKET_LENGTH)
            if data[0] != 0x54 or len(data) != PACKET_LENGTH:
                print("WARNING: Serial sync lost")
                state = State.SYNC0
                continue
            measurements += parse_lidar_data(data)
            if len(measurements) > MEASUREMENTS_PER_PLOT:
                state = State.UPDATE_PLOT
        elif state == State.UPDATE_PLOT:
            x, y, c = get_xyc_data(measurements)
            if PLOT_AUTO_RANGE:
                max_val = max([max(abs(x)), max(abs(y))]) * 1.2
                plt.xlim(-max_val, max_val)
                plt.ylim(-max_val, max_val)
            graph.remove()
            if PLOT_CONFIDENCE:
                graph = plt.scatter(x, y, c=c, marker=".", vmin=0, vmax=255, cmap=PLOT_CONFIDENCE_COLOUR_MAP)
            else:
                graph = plt.plot(x, y, 'b.')[0]
            plt.pause(0.00001)
            save_to_csv(measurements)  # Save data to CSV
            state = State.LOCKED
            measurements = []
