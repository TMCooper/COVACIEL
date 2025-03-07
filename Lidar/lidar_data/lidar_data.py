import serial
import time
from CalcLidarData import CalcLidarData

# Configuration du port série
ser = serial.Serial(port='/dev/ttyS0',
                    baudrate=230400,
                    timeout=5.0,
                    bytesize=8,
                    parity='N',
                    stopbits=1)

# Fichier de sortie
filename = "lidar_data.txt"

with open(filename, "w") as file:
    while True:
        tmpString = ""
        flag2c = False
        b = ser.read()
        tmpInt = int.from_bytes(b, 'big')

        if tmpInt == 0x54:
            tmpString += b.hex() + " "
            flag2c = True
            continue

        elif tmpInt == 0x2c and flag2c:
            tmpString += b.hex()

            if len(tmpString[0:-5].replace(' ', '')) != 90:
                tmpString = ""
                continue

            lidarData = CalcLidarData(tmpString[0:-5])

            # Enregistrement des angles et distances
            for angle, distance in zip(lidarData.Angle_i, lidarData.Distance_i):
                file.write(f"{angle} {distance}\n")

            tmpString = ""

        flag2c = False

        # Arrêter l'enregistrement après 10 secondes (modifiable)
        if time.time() - start_time > 10:
            break

ser.close()
print(f"✅ Données enregistrées dans {lidar_data.txt}")
