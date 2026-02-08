import subprocess
import threading
from queue import Queue
import time
import os

class SpeechEngine:
    def __init__(self, engine='piper'):
        """
        Initialize the speech engine with optimized settings
        Args:
            engine: 'piper' (natural) or 'espeak' (fast/robotic)
        """
        self.engine_type = engine
        self.speech_queue = Queue()
        self.is_speaking = False
        self.last_spoken_time = 0
        self.cooldown_period = 3  # Minimum seconds between alerts
        
        # Piper paths
        self.piper_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'piper', 'piper')
        self.voice_model = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'en_US-amy-medium.onnx')
        
        # Check if Piper is available
        if engine == 'piper' and not os.path.exists(self.piper_path):
            print("⚠️ Piper not found, falling back to espeak")
            self.engine_type = 'espeak'
        
        # Start background thread for speech
        self.speech_thread = threading.Thread(target=self._process_speech_queue, daemon=True)
        self.speech_thread.start()
        
        print(f"🔊 Speech engine initialized (engine: {self.engine_type})")
    
    def _speak_piper(self, message):
        """Use Piper TTS for natural speech"""
        try:
            # Piper command with wave output piped to aplay
            cmd = f'echo "{message}" | {self.piper_path} --model {self.voice_model} --output_raw | aplay -r 22050 -f S16_LE -t raw -'
            subprocess.run(cmd, shell=True, check=True, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"❌ Piper speech error: {str(e)}")
    
    def _speak_espeak(self, message):
        """Use espeak directly via subprocess"""
        try:
            cmd = [
                'espeak',
                '-s', '130',      # Speed: 130 words per minute
                '-a', '200',      # Amplitude (volume): 200 (0-200)
                '-p', '50',       # Pitch: 50 (0-99)
                '-g', '10',       # Gap between words: 10ms
                message
            ]
            subprocess.run(cmd, check=True, capture_output=True)
        except Exception as e:
            print(f"❌ Espeak speech error: {str(e)}")
    
    def _process_speech_queue(self):
        """Background thread to process speech queue"""
        while True:
            try:
                if not self.speech_queue.empty():
                    message, priority = self.speech_queue.get()
                    
                    # Check cooldown for normal priority
                    current_time = time.time()
                    if not priority and (current_time - self.last_spoken_time) < self.cooldown_period:
                        continue
                    
                    self.is_speaking = True
                    
                    if self.engine_type == 'piper':
                        self._speak_piper(message)
                    else:
                        self._speak_espeak(message)
                    
                    self.is_speaking = False
                    self.last_spoken_time = time.time()
                    
                time.sleep(0.1)
            except Exception as e:
                print(f"❌ Speech queue error: {str(e)}")
                self.is_speaking = False
                time.sleep(0.5)
    
    def speak(self, message, priority=False):
        """
        Add message to speech queue
        Args:
            message: Text to speak
            priority: If True, bypass cooldown period
        """
        if message and len(message.strip()) > 0:
            self.speech_queue.put((message, priority))
            print(f"🔊 Queued for speech: {message[:50]}...")
    
    def speak_alert(self, alert_message):
        """Speak a security alert with priority"""
        # Add emphasis to alert
        full_message = f"Security Alert! {alert_message}"
        self.speak(full_message, priority=True)
    
    def is_busy(self):
        """Check if currently speaking"""
        return self.is_speaking
    
    def clear_queue(self):
        """Clear pending speech messages"""
        while not self.speech_queue.empty():
            self.speech_queue.get()
    
    def stop(self):
        """Stop the speech engine"""
        self.clear_queue()
        if self.is_speaking:
            self.engine.stop()
