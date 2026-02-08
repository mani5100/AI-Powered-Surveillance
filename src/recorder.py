import cv2

class VideoRecorder:
    def __init__(self, filename='demo1.avi', fps=30, resolution=(640, 480)):
        self.filename = filename
        self.fps = fps
        self.resolution = resolution
        self.recorder = None
        
    def initialize(self):
        """Initialize video recorder"""
        self.recorder = cv2.VideoWriter(
            self.filename,
            cv2.VideoWriter_fourcc(*'MJPG'),
            self.fps,
            self.resolution
        )
        print(f"💾 Recording enabled: saving to {self.filename}")
        
    def write_frame(self, frame):
        """Write a frame to the video"""
        if self.recorder:
            self.recorder.write(frame)
            
    def release(self):
        """Release the video recorder"""
        if self.recorder:
            self.recorder.release()
            self.recorder = None