import serial

def read_lidar_frames(port="/dev/ttyS0", baudrate=230400):
    ser = serial.Serial(port, baudrate, timeout=1)
    buffer = bytearray()

    try:
        print("Lecture des trames LiDAR... (CTRL+C pour arrêter)")
        while True:
            data = ser.read(1024)
            buffer += data

            while True:
                # Cherche le caractère de début 0x54
                start = buffer.find(b'\x54')
                if start == -1:
                    break

                if len(buffer[start:]) < 47:
                    break  # Attend plus de données si trame incomplète

                # La trame commence par 0x54 et fait 47 octets (typique pour ce type de LiDAR)
                frame = buffer[start:start+47]
                buffer = buffer[start+47:]  # Retire la trame du buffer

                # Affiche la trame en hexadécimal formaté
                hex_frame = ' '.join(f"{byte:02X}" for byte in frame)
                print(f"Trame reçue : {hex_frame}")

    except KeyboardInterrupt:
        print("\nArrêt de la lecture.")
    finally:
        ser.close()

if __name__ == "__main__":
    read_lidar_frames()
