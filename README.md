# Aerial Threat Detection System

> AI-powered desktop application for detecting and classifying objects in aerial footage using YOLOv8

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Node](https://img.shields.io/badge/node-14%2B-green)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-orange)

## 🎯 Features

- 🎨 **Modern Landing Page** - Engaging welcome interface with smooth transitions
- 🤖 **YOLOv8 Detection** - State-of-the-art AI object detection
- 🎥 **Video & Image Support** - Process MP4, AVI, MOV, MKV, WebM, JPG, PNG
- 🎨 **Color-Coded Results** - Red (soldiers), Green (civilians), Yellow (other)
- 📊 **Real-time Progress** - Live monitoring and statistics
- 💾 **Export Results** - Download annotated videos/images
- ⚡ **GPU Acceleration** - CUDA support for faster processing
- 🖥️ **Cross-platform** - Windows, macOS, Linux

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

**Quick Start:**
```bash
start.bat      # Windows
./start.sh     # Linux/Mac
```

**Manual Start:**
```bash
# Terminal 1 - Backend
python backend/server.py

# Terminal 2 - Frontend
npm start
```

## 📖 How to Use

1. Launch the app → Landing page appears
2. Click **"Start Detection"**
3. Upload video or image file
4. Configure frame skip (optional)
5. Click **"Start Detection"**
6. View real-time progress and results
7. Download processed file with annotations

## 🏗️ Project Structure

```
Aerial-Threat-Detection/
├── backend/
│   ├── detect.py           # YOLOv8 detection engine
│   └── server.py           # Flask API server
├── models/
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
