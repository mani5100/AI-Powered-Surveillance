import os
import base64
import json
from datetime import datetime
import cv2
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional
import requests

class SecurityAnalysis(BaseModel):
    """Pydantic model for structured security analysis response"""
    is_legitimate: bool = Field(
        description="True if suspicious object is real, false if false detection"
    )
    alert_message: Optional[str] = Field(
        default=None,
        description="Detailed alert message if legitimate, null if false detection"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence in the assessment (0-1)"
    )

class VisionAnalyzer:
    def __init__(self, webhook_url=None):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.webhook_url = webhook_url
        # Suspicious classes matching the exact names from the model
        self.SUSPICIOUS_CLASSES = ['Fire', 'cigarette', 'knife', 'gun', 'vape']
        self.detection_history = {}  # Track detections over time
        print(f"🚨 Monitoring for suspicious objects: {self.SUSPICIOUS_CLASSES}")
        if self.webhook_url:
            print(f"🔔 Webhook notifications enabled: {self.webhook_url}")
        
    def is_suspicious_object(self, object_name):
        """Check if detected object is in suspicious classes list"""
        return object_name.lower() in [cls.lower() for cls in self.SUSPICIOUS_CLASSES]
    
    def update_detection_history(self, frame_time, detected_objects):
        """Update detection history and check for persistent detections"""
        # Clean old detections (older than 10 seconds - long enough to span multiple analysis intervals)
        self.detection_history = {
            t: objs for t, objs in self.detection_history.items()
            if frame_time - t < 10
        }
        
        # Add new detection
        self.detection_history[frame_time] = detected_objects
        
        print(f"   Detection history: {len(self.detection_history)} entries")
        
        # Check if objects have been consistently detected
        # Reduced requirement to 2 detections for faster response
        if len(self.detection_history) >= 2:
            consistent_objects = set.intersection(
                *[set(objs) for objs in self.detection_history.values()]
            )
            if consistent_objects:
                print(f"✓ Temporal verification passed for: {consistent_objects}")
                return True
        return False
        
    def analyze_frame(self, frame, detected_objects, frame_time):
        """
        Analyze frame using OpenAI Vision API with structured output
        """
        # Filter suspicious objects
        suspicious_objects = [
            obj for obj in detected_objects 
            if self.is_suspicious_object(obj)
        ]
        
        if not suspicious_objects:
            print("   No suspicious objects in filter")
            return None
            
        print(f"   Suspicious objects found: {suspicious_objects}")
        
        # Check temporal persistence
        is_persistent = self.update_detection_history(frame_time, suspicious_objects)
        if not is_persistent:
            print(f"   Temporal check failed. History count: {len(self.detection_history)}")
            return None
            
        try:
            # Convert frame to jpg format
            _, buffer = cv2.imencode('.jpg', frame)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Create structured prompt
            objects_str = ", ".join(suspicious_objects)
            user_prompt = f"""You are a security verification system. Analyze this image for detected suspicious object(s): {objects_str}.

Verify if the detected suspicious object is legitimate or a false detection.
If legitimate, provide a clear alert message describing the threat.
Provide your confidence level in the assessment."""
            
            # Call OpenAI Vision API with Pydantic structured output
            print("📡 Sending request to OpenAI Vision API with structured output...")
            completion = self.client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",  # Use the model that supports structured outputs
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                response_format=SecurityAnalysis,
            )
            
            # Get the parsed response
            analysis = completion.choices[0].message.parsed
            
            if analysis:
                print(f"✓ Received structured response from OpenAI")
                print(f"   Legitimate: {analysis.is_legitimate}")
                print(f"   Confidence: {analysis.confidence:.2%}")
                return analysis
            else:
                print("❌ No parsed response received")
                return None
            
        except Exception as e:
            print(f"❌ Error analyzing frame: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def send_webhook_notification(self, event_id, analysis_data):
        """
        Send HTTP POST notification to webhook URL when new event is saved
        
        Args:
            event_id: Unique identifier for the event (timestamp)
            analysis_data: Dictionary containing analysis information
        """
        if not self.webhook_url:
            return
        
        try:
            # Prepare webhook payload
            payload = {
                'event_id': event_id,
                'timestamp': datetime.now().isoformat(),
                'analysis': analysis_data
            }
            
            # Send POST request to webhook
            print(f"🔔 Sending webhook notification to {self.webhook_url}...")
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=5  # 5 second timeout to avoid blocking
            )
            
            if response.status_code == 200:
                print(f"✓ Webhook notification sent successfully")
            else:
                print(f"⚠️ Webhook returned status {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⚠️ Webhook request timed out")
        except requests.exceptions.ConnectionError:
            print(f"⚠️ Failed to connect to webhook URL")
        except Exception as e:
            print(f"⚠️ Error sending webhook notification: {str(e)}")
    
    def save_analysis(self, frame, analysis_json, base_path=None):
        """
        Save the frame and its analysis
        """
        try:
            # Use absolute path for base_path
            if base_path is None:
                base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "suspicious_events")
            
            # Create directory if it doesn't exist
            os.makedirs(base_path, exist_ok=True)
            print(f"📁 Using directory: {base_path}")
            
            # Generate timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save image
            image_path = os.path.join(base_path, f"event_{timestamp}.jpg")
            success = cv2.imwrite(image_path, frame)
            if not success:
                raise Exception(f"Failed to save image to {image_path}")
            print(f"📸 Saved image to: {image_path}")
            
            # Save analysis as JSON
            json_path = os.path.join(base_path, f"event_{timestamp}.json")
            with open(json_path, 'w') as f:
                f.write(analysis_json)
            print(f"📝 Saved analysis to: {json_path}")
            
            # Send webhook notification if configured
            if self.webhook_url:
                try:
                    analysis_dict = json.loads(analysis_json)
                    self.send_webhook_notification(f"event_{timestamp}", analysis_dict)
                except json.JSONDecodeError:
                    print("⚠️ Failed to parse analysis JSON for webhook")
            
            print(f"✅ Successfully saved event analysis to {base_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving analysis: {str(e)}")
            print(f"   Attempted to save to: {base_path}")
            return False