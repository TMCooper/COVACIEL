import serial

def lire_trames_lidar(port="/dev/ttyS0", baudrate=230400):
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            print(f"Lecture des trames LiDAR sur {port} à {baudrate} baud...\n")

            while True:
                # Lecture de 47 octets (taille d'une trame LiDAR)
                trame = ser.read(47)

                if len(trame) == 47:
                    hex_str = ' '.join(f"{byte:02X}" for byte in trame)
                    print(hex_str)
                else:
                    print("Trame incomplète ou absente.")
    except KeyboardInterrupt:
        print("\nArrêt de la lecture.")
    except serial.SerialException as e:
        print(f"Erreur de port série : {e}")

if __name__ == "__main__":
    lire_trames_lidar()
