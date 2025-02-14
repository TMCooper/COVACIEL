from picamera2 import Picamera2
from picamera2.outputs import FfmpegOutput

# Créer une instance de la caméra
picam2 = Picamera2()


output = FfmpegOutput("-f mpegts udp://192.168.20.165:5000")  


picam2.start_recording(output)


picam2.wait_recording(3600)  


picam2.stop_recording()
