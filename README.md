# 🎯 YOLO11 Intelligent Surveillance System

An AI-powered real-time surveillance system built for Raspberry Pi that detects suspicious objects (weapons, fire, smoking) using YOLO11 and provides intelligent alerts through voice announcements and a web dashboard.

## 📋 Overview

This Final Year Project implements a comprehensive security surveillance solution that:
- **Detects** dangerous objects in real-time using a custom-trained YOLO11 model
- **Analyzes** detections using OpenAI Vision API to reduce false positives
- **Alerts** users through natural voice announcements (Piper TTS)
- **Monitors** through a responsive web dashboard with event history and statistics

## 🚨 Detected Objects

The system is trained to detect:
- 🔥 **Fire** - Early fire detection
- 🔪 **Knife** - Weapon detection
- 🔫 **Gun** - Firearm detection  
- 🚬 **Cigarette** - Smoking detection
- 💨 **Vape** - Vaping detection

## 🏗️ System Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Raspberry Pi   │────▶│   YOLO11 Model   │────▶│ Vision Analyzer │
│     Camera      │     │   (Detection)    │     │  (OpenAI API)   │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                    ┌─────────────────────────────────────┼─────────────────────┐
                    │                                     │                     │
                    ▼                                     ▼                     ▼
           ┌───────────────┐                    ┌─────────────────┐    ┌───────────────┐
           │ Speech Engine │                    │  Event Storage  │    │ Web Dashboard │
           │  (Piper TTS)  │                    │     (JSON)      │    │    (Flask)    │
           └───────────────┘                    └─────────────────┘    └───────────────┘
```

## 📁 Project Structure

```
Project-yolo11/
├── main.py                 # Main detection application
├── src/
│   ├── camera.py           # Camera capture module
│   ├── detector.py         # YOLO11 inference engine
│   ├── visualizer.py       # Detection visualization
│   ├── recorder.py         # Video recording
│   ├── vision_analyzer.py  # OpenAI Vision analysis
│   └── speech_engine.py    # Text-to-speech alerts
├── web/
│   ├── app.py              # Flask web application
│   ├── config.py           # Web app configuration
│   ├── templates/          # HTML templates
│   ├── static/js/          # JavaScript files
│   └── utils/              # Utility modules
├── piper/                  # Piper TTS engine
└── best.pt                 # YOLO11 trained model
```

## 🚀 Features

### Real-time Detection
- Live camera feed processing
- Sub-second inference on Raspberry Pi
- Configurable confidence thresholds

### Intelligent Analysis
- OpenAI Vision API integration
- False positive reduction through AI verification
- Temporal verification (consistent detection over time)

### Voice Alerts
- Natural speech using Piper TTS
- Fallback to espeak for compatibility
- Cooldown system to prevent alert spam

### Web Dashboard
- 📊 Real-time statistics and charts
- 📋 Event history with filtering
- 🎛️ System controls (start/stop detection)
- 🔔 Live notifications via Server-Sent Events
- 📱 Responsive design

## ⚙️ Installation

### Prerequisites
- Raspberry Pi 4 (4GB+ recommended)
- Raspberry Pi Camera Module
- Python 3.9+

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Project-yolo11.git
   cd Project-yolo11
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Download/place model files**
   - Place your trained `best.pt` model in the project root

## 🎮 Usage

### Run Detection System
```bash
python main.py --model best.pt --resolution 1640x1232 --thresh 0.2
```

**Arguments:**
| Argument | Description | Default |
|----------|-------------|---------|
| `--model` | Path to YOLO model | Required |
| `--resolution` | Camera resolution (WxH) | 1640x1232 |
| `--thresh` | Confidence threshold | 0.2 |
| `--record` | Record output video | False |
| `--analyze-interval` | Seconds between analyses | 30 |
| `--webhook` | Webhook URL for notifications | None |

### Run Web Dashboard
```bash
cd web
python app.py
```
Access at `http://localhost:5000` or `http://<raspberry-pi-ip>:5000`

## 🔧 Configuration

### Detection Classes
Edit `src/vision_analyzer.py` to modify suspicious classes:
```python
self.SUSPICIOUS_CLASSES = ['Fire', 'cigarette', 'knife', 'gun', 'vape']
```

### Speech Engine
The system uses Piper TTS for natural voice. Falls back to espeak if unavailable.

## 📊 Web Dashboard Features

- **Dashboard**: Overview with recent events and live status
- **Events**: Browse and filter all detected events
- **Statistics**: Charts showing detection patterns over time
- **Controls**: Start/stop detection system remotely

## 🔗 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/events` | GET | Get all events (with optional filters) |
| `/api/events/<id>` | GET | Get single event details |
| `/api/status` | GET | Get system status |
| `/api/stats` | GET | Get comprehensive statistics |
| `/api/start` | POST | Start detection system |
| `/api/stop` | POST | Stop detection system |

## 🛠️ Tech Stack

- **Detection**: YOLO11 (Ultralytics)
- **AI Analysis**: OpenAI Vision API (GPT-4o)
- **Backend**: Python, Flask
- **Frontend**: HTML, JavaScript, Chart.js
- **TTS**: Piper TTS, espeak
- **Hardware**: Raspberry Pi 4, Pi Camera

## 📄 License

This project is developed as a Final Year Project (FYP) for educational purposes.

## 👤 Author

**Abdul Rehman**

---

⭐ Star this repository if you find it useful!
