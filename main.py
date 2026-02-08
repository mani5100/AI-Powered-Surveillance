import argparse
import time
import cv2
import json
import os
from src.camera import Camera
from src.detector import YOLODetector
from src.visualizer import Visualizer
from src.recorder import VideoRecorder
from src.vision_analyzer import VisionAnalyzer
from src.speech_engine import SpeechEngine

def parse_arguments():
    parser = argparse.ArgumentParser(description="YOLO Detection using Raspberry Pi Camera")
    parser.add_argument('--model', required=True, help='Path to YOLO model file (e.g., best.pt)')
    parser.add_argument('--resolution', default='1640x1232', help='Camera resolution WxH (default: 640x480)')
    parser.add_argument('--thresh', type=float, default=0.2, help='Confidence threshold (default: 0.5)')
    parser.add_argument('--record', action='store_true', help='Record output video (demo1.avi)')
    parser.add_argument('--analyze-interval', type=int, default=30, 
                      help='Minimum interval (in seconds) between vision analyses')
    parser.add_argument('--webhook', type=str, default=None,
                      help='Webhook URL to notify when new events are detected')
    return parser.parse_args()

def main():
    # Parse arguments
    args = parse_arguments()
    resW, resH = map(int, args.resolution.lower().split('x'))
    
    # Initialize components
    camera = Camera(resolution=(resW, resH))
    detector = YOLODetector(args.model, args.thresh)
    visualizer = Visualizer()
    recorder = VideoRecorder(resolution=(resW, resH)) if args.record else None
    vision_analyzer = VisionAnalyzer(webhook_url=args.webhook)
    speech_engine = SpeechEngine()
    last_analysis_time = 0
    
    try:
        # Setup
        camera.initialize()
        detector.load_model()
        if recorder:
            recorder.initialize()
            
        print("✅ YOLO detection started. Press 'q' to quit, 'p' to capture frame.")
        
        # Main loop
        while True:
            t_start = time.perf_counter()
            
            # Capture frame
            frame = camera.capture_frame()
            
            # Run YOLO inference
            detections = detector.detect(frame)
            
            # Get detected object labels with high confidence
            detected_objects = []
            for det in detections:
                if det.conf.item() >= detector.conf_thresh:
                    class_id = int(det.cls.item())
                    detected_objects.append(detector.labels[class_id])
            
            # Process detections and draw them
            frame, object_count = visualizer.draw_detections(
                frame, detections, detector.labels, detector.conf_thresh
            )
            
            # Analyze frame if time interval has passed
            current_time = time.time()
            if (current_time - last_analysis_time) >= args.analyze_interval:
                if detected_objects:
                    print(f"🔍 Detected objects: {detected_objects}")
                    suspicious_detected = any(vision_analyzer.is_suspicious_object(obj) for obj in detected_objects)
                    
                    if suspicious_detected:
                        print(f"⚠️ Suspicious objects detected, analyzing...")
                        result = vision_analyzer.analyze_frame(frame, detected_objects, current_time)
                        
                        if result:
                            if result.is_legitimate:
                                print(f"⚠️ ALERT! {result.alert_message}")
                                print(f"Confidence: {result.confidence:.2%}")
                                
                                # Speak the alert
                                speech_engine.speak_alert(result.alert_message)
                                
                                # Convert Pydantic model to JSON string
                                analysis_json = result.model_dump_json(indent=2)
                                success = vision_analyzer.save_analysis(frame, analysis_json)
                                if not success:
                                    print("❌ Failed to save analysis!")
                            else:
                                print(f"ℹ️ False detection (Confidence: {result.confidence:.2%})")
                        else:
                            print("❌ No analysis result returned")
                    else:
                        print("ℹ️ No suspicious objects detected in this frame")
                    
                last_analysis_time = current_time
            
            # Calculate and display FPS
            t_stop = time.perf_counter()
            fps = visualizer.update_fps(1 / (t_stop - t_start))
            frame = visualizer.draw_stats(frame, fps, object_count)
            
            # Display and record
            cv2.imshow('YOLO Pi Camera Detection', frame)
            if recorder:
                recorder.write_frame(frame)
            
            # Handle key events
            key = cv2.waitKey(5)
            if key == ord('q'):
                break
            elif key == ord('p'):
                cv2.imwrite('capture.png', frame)
                print("📸 Frame saved as capture.png")
                
    finally:
        # Cleanup
        print(f"✅ Average FPS: {visualizer.update_fps(0):.2f}")
        speech_engine.stop()
        if recorder:
            recorder.release()
        camera.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()