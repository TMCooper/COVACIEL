from rplidar import RPLidar

lidar = RPLidar('/dev/ttyS0')

for scan in lidar.iter_scans():
    for (_, angle, distance) in scan:
        print(f"Angle: {angle}, Distance: {distance}")

lidar.stop()
lidar.disconnect()

