import os
from ultralytics import YOLO

class YOLODetector:
    def __init__(self, model_path, conf_thresh=0.2):
        self.model_path = model_path
        self.conf_thresh = conf_thresh
        self.model = None
        self.labels = None
        
    def load_model(self):
        """Load the YOLO model"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError("❌ ERROR: Model path invalid or not found.")
            
        print("🚀 Loading YOLO model...")
        self.model = YOLO(self.model_path)
        self.labels = self.model.names
        print(f"📋 Available classes in model: {list(self.labels.values())}")
        
    def detect(self, frame):
        """Run detection on a frame"""
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
            
        results = self.model(frame, verbose=False)
        return results[0].boxes