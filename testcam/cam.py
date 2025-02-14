from picamera2.outputs import FileOutput
import socket
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    
sock.connect(("REMOTEIP", 10001))
stream = sock.makefile("wb")
output = FileOutput(stream)
