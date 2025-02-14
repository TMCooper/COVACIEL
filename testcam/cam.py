from picamera2.outputs import FfmpegOutput

output = FfmpegOutput("cam.mp4", audio=True)
