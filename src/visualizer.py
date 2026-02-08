import cv2
import numpy as np

class Visualizer:
    def __init__(self):
        self.bbox_colors = [
            (164,120,87), (68,148,228), (93,97,209), (178,182,133),
            (88,159,106), (96,202,231), (159,124,168), (169,162,241),
            (98,118,150), (172,176,184)
        ]
        self.frame_rate_buffer = []
        self.fps_avg_len = 100
        
    def draw_detections(self, frame, detections, labels, conf_thresh):
        """Draw bounding boxes and labels on frame"""
        object_count = 0
        
        for i in range(len(detections)):
            xyxy = detections[i].xyxy.cpu().numpy().squeeze().astype(int)
            xmin, ymin, xmax, ymax = xyxy
            classidx = int(detections[i].cls.item())
            conf = detections[i].conf.item()
            
            if conf >= conf_thresh:
                color = self.bbox_colors[classidx % len(self.bbox_colors)]
                label = f"{labels[classidx]}: {int(conf*100)}%"
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
                cv2.putText(frame, label, (xmin, ymin - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                object_count += 1
        
        return frame, object_count
    
    def update_fps(self, frame_rate):
        """Update FPS calculation"""
        self.frame_rate_buffer.append(frame_rate)
        if len(self.frame_rate_buffer) > self.fps_avg_len:
            self.frame_rate_buffer.pop(0)
        return np.mean(self.frame_rate_buffer)
    
    def draw_stats(self, frame, fps, object_count):
        """Draw FPS and object count on frame"""
        cv2.putText(frame, f'FPS: {fps:.2f}', (10, 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
        cv2.putText(frame, f'Objects: {object_count}', (10, 45), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
        return frame