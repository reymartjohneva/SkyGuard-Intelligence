# Aerial Threat Detection System

> AI-powered desktop application for detecting and classifying objects in aerial footage using YOLO11s & YOLOv8s

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Node](https://img.shields.io/badge/node-14%2B-green)
![YOLO](https://img.shields.io/badge/YOLO-v11s%20%7C%20v8s-orange)

## ✨ Features

- 🎨 **Modern Landing Page** - Engaging welcome interface with smooth transitions
- 🤖 **Dual Model Support** - YOLO11s (Latest) & YOLOv8s (Legacy)
- 🔥 **Hot Model Switching** - Swap between models instantly without restart
- 🎥 **Multi-Source Input** - Video files, Images, and YouTube URLs
- 🌐 **YouTube Integration** - Direct video download and processing from YouTube
- 🎯 **Color-Coded Detection** - Red (soldiers), Green (civilians)
- 📊 **Real-time Progress** - Live monitoring and statistics
- 💾 **Export Results** - Download annotated videos/images
- ⚡ **GPU Acceleration** - CUDA support for faster processing
- 🖥️ **Cross-platform** - Windows, macOS, Linux
- 🚀 **Auto-Start Server** - Python backend starts automatically with `npm start`

## 🆕 New in v2.0

- ✅ **YOLO11s Support** - Latest YOLO model with improved accuracy
- ✅ **Hot Model Switching** - Change models on-the-fly
- ✅ **YouTube URL Support** - Process videos directly from YouTube
- ✅ **Multiple Input Types** - Video, Image, and YouTube URL support
- ✅ **Auto-Server Start** - Backend starts automatically when running `npm start`
- ✅ **Enhanced UI** - Model selector and input type toggles

## 📋 Prerequisites

- **Node.js** v14+
- **Python** 3.8-3.11
- **pip** package manager
- **CUDA GPU** (optional, for acceleration)

## 🚀 Quick Start

**Windows:**
```bash
git clone https://github.com/reymartjohneva/Aerial-Threat-Detection.git
cd Aerial-Threat-Detection
setup.bat
start.bat
```

**Linux/Mac:**
```bash
git clone https://github.com/reymartjohneva/Aerial-Threat-Detection.git
cd Aerial-Threat-Detection
chmod +x setup.sh start.sh
./setup.sh
./start.sh
```

## 📦 Manual Installation

```bash
# Clone repository
git clone https://github.com/reymartjohneva/Aerial-Threat-Detection.git
cd Aerial-Threat-Detection

# Install dependencies
npm install
pip install -r requirements.txt
```

## 🎮 Running the App

**Quick Start (Auto-starts backend server):**
```bash
npm start      # Both frontend and backend start automatically
```

**Development Mode:**
```bash
npm run dev    # Starts with DevTools enabled
```

**Manual Start (if needed):**
```bash
# Terminal 1 - Backend
python backend/server.py

# Terminal 2 - Frontend
npm start
```

## 📖 How to Use

### Video/Image Processing
1. Launch the app → Landing page appears
2. Click **"Start Detection"**
3. Select input type: **Video**, **Image**, or **YouTube**
4. Upload file or enter YouTube URL
5. Select model: **YOLO11s** or **YOLOv8s**
6. Configure frame skip (for videos)
7. Click **"Start Detection"**
8. View real-time progress and results
9. Download processed file with annotations

### Hot Model Switching
- Use the model selector dropdown at the top
- Switch between **YOLO11s** and **YOLOv8s** anytime
- Model changes instantly without restarting

### YouTube Video Processing
1. Click **YouTube** tab
2. Paste YouTube video URL
3. Click **"Load YouTube Video"**
4. Wait for download to complete
5. Process as normal video

## 🏗️ Project Structure

```
Aerial-Threat-Detection/
├── backend/
│   ├── detect.py           # YOLO detection engine (v11s & v8s)
│   └── server.py           # Flask API server with hot swap
├── models/
│   ├── yolo11s.pt         # YOLO11s model (latest)
│   └── yolov8s.pt         # YOLOv8s model (legacy)
│   └── yolov8s.pt          # Model (auto-downloads)
├── uploads/                # Uploaded files
├── outputs/                # Processed results
├── landing.html            # Landing page
├── detection.html          # Detection interface
├── detection.js            # Frontend logic
├── main.js                 # Electron main process
├── styles.css              # Styling
├── package.json            # Node dependencies
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## 🛠️ Technology Stack

**Backend:** Python, YOLOv8, PyTorch, OpenCV, Flask  
**Frontend:** Electron, HTML5/CSS3, JavaScript

## 🔧 API Endpoints

### Health Check
```
GET /api/health
```

### Upload File
```
POST /api/upload
```

### Detect Objects
```
POST /api/detect/video
POST /api/detect/image
```

### Check Status
```
GET /api/status/:jobId
```

### Download Result
```
GET /api/download/:filename
```

## 🐛 Troubleshooting

**Server won't start?**
```bash
pip install -r requirements.txt --upgrade
```

**Model not found?**
- YOLOv8s will auto-download on first run
- Or place your model in `models/` directory

**GPU not detected?**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/name`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature/name`)
5. Open Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 👨‍💻 Author

**Reymart John Eva**  
GitHub: [@reymartjohneva](https://github.com/reymartjohneva)

## 🙏 Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [PyTorch](https://pytorch.org/)
- [Electron](https://www.electronjs.org/)
- [Flask](https://flask.palletsprojects.com/)
- [OpenCV](https://opencv.org/)

## ⚠️ Disclaimer

**Educational purposes only.** Ensure proper authorization before analyzing footage. AI predictions should not be used for critical decisions without human verification. Users are responsible for legal compliance.

---

**Made with ❤️ by Reymart John Eva**  
*Star ⭐ this repository if you find it helpful!*
>>>>>>> development
