import serial
import struct
import time

class LD06Reader:
    def __init__(self, port='/dev/ttyS0', baudrate=230400):
        self.port = port
        self.baudrate = baudrate
        self.serial = serial.Serial(port, baudrate)
        self.distances = [None] * 360  

    def read_packet(self):
        while True:
            byte = self.serial.read(1)
            if byte == b'\x54':
                packet = byte + self.serial.read(46)
                if len(packet) == 47:
                    return packet
                else:
                    continue  

    def parse_packet(self, packet):
        print("Taille du paquet :", len(packet))
        format_str = 'BBHH' + ('HB'*12) + 'HHB'
        print("Taille requise par struct.unpack :", struct.calcsize(format_str))
        if len(packet) != struct.calcsize(format_str):
            print("Taille incorrecte :", len(packet), "au lieu de", struct.calcsize(format_str))
            return None, None, []
        unpacked = struct.unpack(format_str, packet)
        header, ver_len, speed, start_angle_001deg, *points_data, end_angle_001deg, timestamp, crc = unpacked
        start_angle_deg = start_angle_001deg / 100.0
        end_angle_deg = end_angle_001deg / 100.0
        distances_mm = points_data[::2]
        distances_cm = [dist / 10.0 for dist in distances_mm]
        return start_angle_deg, end_angle_deg, distances_cm

    def update(self):
        packet = self.read_packet()
        if packet:
            start_angle_deg, end_angle_deg, points = self.parse_packet(packet)
            if start_angle_deg is not None:
                num_points = len(points)
                if num_points > 1:
                    increment = (end_angle_deg - start_angle_deg) / (num_points - 1)
                else:
                    increment = 0
                for i, dist_cm in enumerate(points):
                    angle_deg = start_angle_deg + i * increment
                    int_angle = round(angle_deg) % 360
                    self.distances[int_angle] = dist_cm

    def get_distance(self, angle):
        if angle < 0 or angle >= 360:
            return None
        return self.distances[angle]

    def get_all_distances(self):
        return self.distances.copy()