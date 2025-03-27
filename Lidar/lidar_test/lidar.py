import numpy as np
import matplotlib.pyplot as plt
import serial
from enum import Enum
import struct
import time

# ----------------------------------------------------------------------
# System Constants
# ----------------------------------------------------------------------
SERIAL_PORT = "/dev/ttyS0"
BAUD_RATE = 115200  # Augmenté à 115200 pour tester les performances
MEASUREMENTS_PER_PLOT = 240  # Réduit à 240 pour tester les performances
PLOT_MAX_RANGE = 4.0
PLOT_AUTO_RANGE = False
PLOT_CONFIDENCE = True
PLOT_CONFIDENCE_COLOUR_MAP = "bwr_r"
PRINT_DEBUG = False
UPDATE_INTERVAL = 0.1  # Intervalle de mise à jour du graphique en secondes

# ----------------------------------------------------------------------
# Packet format constants
# ----------------------------------------------------------------------
PACKET_LENGTH = 47
MEASUREMENT_LENGTH = 12
MESSAGE_FORMAT = "<xBHH" + "HB" * MEASUREMENT_LENGTH + "HHB"

State = Enum("State", ["SYNC0", "SYNC1", "SYNC2", "LOCKED", "UPDATE_PLOT"])

def parse_lidar_data(data):
    length, speed, start_angle, *pos_data, stop_angle, timestamp, crc = struct.unpack(MESSAGE_FORMAT, data)
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

running = True

def on_plot_close(event):
    global running
    running = False

if __name__ == "__main__":
    lidar_serial = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.5)
    measurements = []
    data = b''
    state = State.SYNC0

    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 10))
    plt.rcParams['lines.markersize'] = 2.0
    if PLOT_CONFIDENCE:
        graph = ax.scatter([], [], c=[], marker=".", vmin=0, vmax=255, cmap=PLOT_CONFIDENCE_COLOUR_MAP)
    else:
        graph, = ax.plot([], [], ".")
    graph.figure.canvas.mpl_connect('close_event', on_plot_close)
    plt.xlim(-PLOT_MAX_RANGE, PLOT_MAX_RANGE)
    plt.ylim(-PLOT_MAX_RANGE, PLOT_MAX_RANGE)

    last_update_time = time.time()
    background = fig.canvas.copy_from_bbox(ax.bbox)

    while running:
        current_time = time.time()
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
            if current_time - last_update_time >= UPDATE_INTERVAL:
                x, y, c = get_xyc_data(measurements)
                if PLOT_AUTO_RANGE:
                    mav_val = max([max(abs(x)), max(abs(y))]) * 1.2
                    ax.set_xlim(-mav_val, mav_val)
                    ax.set_ylim(-mav_val, mav_val)
                if PLOT_CONFIDENCE:
                    graph.set_offsets(np.c_[x, y])
                    graph.set_array(c)
                else:
                    graph.set_data(x, y)
                fig.canvas.restore_region(background)
                ax.draw_artist(graph)
                fig.canvas.blit(ax.bbox)
                fig.canvas.flush_events()
                last_update_time = current_time
                state = State.LOCKED
                measurements = []
