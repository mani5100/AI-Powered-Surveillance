from picamera2 import Picamera2
import cv2

class Camera:
    def __init__(self, resolution=(640, 480)):
        self.resolution = resolution
        self.picam = None
        
    def initialize(self):
        """Initialize and configure the Pi Camera"""
        print("📷 Initializing Raspberry Pi Camera...")
        self.picam = Picamera2()
        self.picam.configure(self.picam.create_video_configuration(
            main={"format": 'XRGB8888', "size": self.resolution}
        ))
        self.picam.start()
        
    def capture_frame(self):
        """Capture a frame from the camera"""
        frame_bgra = self.picam.capture_array()
        return cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2BGR)
    
    def stop(self):
        """Stop the camera"""
        if self.picam:
            self.picam.stop()