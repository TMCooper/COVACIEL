import serial
import struct
import time

# Taille d'un paquet LD06 (en octets)
PACKET_SIZE = 45

def calculate_crc(data):
    """
    Calcule le CRC pour les données fournies.
    Cette fonction doit être adaptée selon le protocole du LD06.
    """
    # Exemple de calcul CRC-8 simple (à adapter)
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0x07
            else:
                crc <<= 1
            crc &= 0xFF
    return crc

def verify_crc(packet):
    """
    Vérifie le CRC du paquet.
    """
    crc_received = packet[44]
    crc_calculated = calculate_crc(packet[:44])
    return crc_received == crc_calculated

def process_packet(packet):
    """
    Décode un paquet LD06 de 45 octets.
    """
    if len(packet) != PACKET_SIZE:
        print("Erreur : paquet de taille invalide :", len(packet))
        return None

    if not verify_crc(packet):
        print("Erreur : CRC invalide.")
        return None

    start_angle = struct.unpack('<H', packet[2:4])[0] / 100.0

    readings = []
    num_readings = 12
    bytes_per_reading = 3
    for i in range(num_readings):
        idx = 4 + i * bytes_per_reading
        distance = struct.unpack('<H', packet[idx: idx + 2])[0]
        intensity = packet[idx + 2]
        readings.append((distance, intensity))

    end_angle = struct.unpack('<H', packet[40:42])[0] / 100.0

    if end_angle >= start_angle:
        angle_step = (end_angle - start_angle) / num_readings
    else:
        angle_step = ((end_angle + 360) - start_angle) / num_readings

    measurements = []
    for i, (distance, _) in enumerate(readings):
        angle = (start_angle + i * angle_step) % 360
        measurements.append((round(angle, 1), distance))

    return measurements

def save_results_to_txt(measurements, filename):
    with open(filename, 'a') as f:
        for angle, distance in measurements:
            distance_cm = distance / 10.0
            f.write(f"{angle:.1f}, {distance_cm:.2f}\n")

def main():
    SERIAL_PORT = '/dev/ttyS0'
    BAUDRATE = 230400
    OUTPUT_FILE = 'lidar_results.txt'

    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        print("Port série ouvert sur", SERIAL_PORT)
    except Exception as e:
        print("Erreur lors de l'ouverture du port série :", e)
        return

    try:
        while True:
            packet = ser.read(PACKET_SIZE)
            if len(packet) != PACKET_SIZE:
                print("Paquet incomplet reçu, taille :", len(packet))
                continue

            measurements = process_packet(packet)
            if measurements is None:
                continue

            print("Mesures :", measurements)
            save_results_to_txt(measurements, OUTPUT_FILE)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Arrêt du programme par l'utilisateur.")
    except Exception as e:
        print("Erreur lors de la lecture ou du traitement :", e)
    finally:
        ser.close()

if __name__ == '__main__':
    main()
