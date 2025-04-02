import serial

SERIAL_PORT = "/dev/ttyS0"
PACKET_LENGTH = 47  # Longueur attendue d'un paquet de données
TIMEOUT = 5  # Augmentez le timeout pour permettre plus de temps pour la réception des données

def test_lidar():
    try:
        with serial.Serial(SERIAL_PORT, 230400, timeout=TIMEOUT) as ser:
            buffer = b''
            while True:
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)
                    buffer += data

                    # Vérifiez si le buffer contient un paquet complet
                    while len(buffer) >= PACKET_LENGTH:
                        packet = buffer[:PACKET_LENGTH]
                        buffer = buffer[PACKET_LENGTH:]
                        print("Paquet reçu :", packet)
                        # Traitez le paquet ici
                else:
                    print("Aucune donnée reçue.")
    except serial.SerialException as e:
        print(f"Erreur de connexion série : {e}")

if __name__ == "__main__":
    test_lidar()
