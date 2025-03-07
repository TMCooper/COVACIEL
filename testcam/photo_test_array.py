from picamera2 import Picamera2
picam2 = Picamera2()
picam2.start()
frame = picam2.capture_array()
print("Capture réussie")
picam2.stop()