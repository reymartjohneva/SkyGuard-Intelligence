"""
Flask API Server for YOLO11 Object Detection
Provides REST API endpoints for video processing and real-time detection
"""

from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import cv2
import json
from pathlib import Path
import threading
import queue
import base64
import time
import subprocess
import re
import yt_dlp
from detect import ObjectDetector

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
MODEL_FOLDER = 'models'
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp'}
MAX_FILE_AGE_HOURS = 24  # Auto-delete files older than 24 hours

# Create necessary folders
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, MODEL_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Initialize detector
detector = None
processing_status = {}
results_queue = queue.Queue()
frame_streams = {}  # Store frame streams for real-time viewing


def cleanup_old_files():
    """Remove uploaded and output files older than MAX_FILE_AGE_HOURS"""
    import time
    current_time = time.time()
    max_age_seconds = MAX_FILE_AGE_HOURS * 3600
    
    for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
        if not os.path.exists(folder):
            continue
            
        for filename in os.listdir(folder):
            # Skip README and .gitkeep files
            if filename in ['README.md', '.gitkeep']:
                continue
                
            filepath = os.path.join(folder, filename)
            
            # Skip if not a file
            if not os.path.isfile(filepath):
                continue
            
            # Check file age
            file_age = current_time - os.path.getmtime(filepath)
            
            if file_age > max_age_seconds:
                try:
                    os.remove(filepath)
                    print(f"🗑️  Cleaned up old file: {filename} (age: {file_age/3600:.1f} hours)")
                except Exception as e:
                    print(f"❌ Failed to delete {filename}: {e}")


def allowed_file(filename, file_type='video'):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    if file_type == 'video':
        return ext in ALLOWED_VIDEO_EXTENSIONS
    elif file_type == 'image':
        return ext in ALLOWED_IMAGE_EXTENSIONS
    else:
        return ext in ALLOWED_VIDEO_EXTENSIONS or ext in ALLOWED_IMAGE_EXTENSIONS


def init_detector(model_path='models/yolo11s.pt'):
    """Initialize the object detector"""
    global detector
    try:
        if os.path.exists(model_path):
            detector = ObjectDetector(model_path=model_path)
            return True
        else:
            print(f"Warning: Model file not found at {model_path}")
            print("Please place your yolo11s.pt in the models/ directory")
            return False
    except Exception as e:
        print(f"Error initializing detector: {e}")
        return False


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'model_loaded': detector is not None,
        'current_model': detector.model_name if detector else 'N/A',
        'device': detector.device if detector else 'N/A'
    })


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload video or image file for processing"""
    # Check for either 'video' or 'image' in request
    file = None
    file_type = None
    
    if 'video' in request.files:
        file = request.files['video']
        file_type = 'video'
    elif 'image' in request.files:
        file = request.files['image']
        file_type = 'image'
    else:
        return jsonify({'error': 'No file provided'}), 400
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename, file_type):
        if file_type == 'video':
            return jsonify({'error': 'Invalid video file type. Allowed: mp4, avi, mov, mkv, webm'}), 400
        else:
            return jsonify({'error': 'Invalid image file type. Allowed: jpg, jpeg, png, bmp, tiff, webp'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    return jsonify({
        'success': True,
        'filename': filename,
        'filepath': filepath,
        'file_type': file_type,
        'message': f'{file_type.capitalize()} uploaded successfully'
    })


@app.route('/api/detect/video', methods=['POST'])
def detect_video():
    """Process video and detect objects"""
    if detector is None:
        return jsonify({'error': 'Model not loaded. Please check model file.'}), 500
    
    data = request.get_json()
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    
    video_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if not os.path.exists(video_path):
        return jsonify({'error': 'Video file not found'}), 404
    
    # Generate output filename
    output_filename = f"detected_{filename}"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    
    # Start processing in background thread
    job_id = filename.replace('.', '_')
    processing_status[job_id] = {
        'status': 'processing',
        'progress': 0,
        'detections': [],
        'output_file': output_filename
    }
    
    # Create frame stream queue with larger buffer to prevent dropping frames
    frame_streams[job_id] = queue.Queue(maxsize=60)
    
    # Get video FPS for proper playback timing
    import cv2
    cap = cv2.VideoCapture(video_path)
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    
    def process_video_thread():
        try:
            all_detections = []
            frame_skip = data.get('frame_skip', 1)
            
            for result in detector.process_video(video_path, output_path, frame_skip):
                # Update progress
                processing_status[job_id]['progress'] = result['progress']
                
                # Convert frame to base64 with lower quality for faster transmission
                frame_base64 = detector.frame_to_base64(result['frame'], quality=60)
                
                # Store detections
                detection_summary = {
                    'frame': result['frame_number'],
                    'count': result['count'],
                    'detections': result['detections'],
                    'timestamp': result['timestamp']
                }
                all_detections.append(detection_summary)
                
                # Keep only last 100 frames in memory
                if len(all_detections) > 100:
                    all_detections.pop(0)
                
                processing_status[job_id]['detections'] = all_detections
                
                # Stream frame to client without rate limiting
                try:
                    stream_data = {
                        'type': 'frame',
                        'frame': frame_base64,
                        'frame_number': result['frame_number'],
                        'progress': result['progress'],
                        'detections': result['detections'],
                        'count': result['count'],
                        'fps': video_fps
                    }
                    # Use put with timeout to avoid blocking
                    frame_streams[job_id].put(stream_data, block=True, timeout=0.1)
                except queue.Full:
                    # Skip frame if queue is full (client is lagging)
                    pass
            
            # Mark as complete
            processing_status[job_id]['status'] = 'completed'
            processing_status[job_id]['progress'] = 100
            
            # Send completion signal
            if job_id in frame_streams:
                frame_streams[job_id].put(None)
            
            # Save summary
            summary_path = os.path.join(OUTPUT_FOLDER, f"summary_{job_id}.json")
            with open(summary_path, 'w') as f:
                json.dump({
                    'total_detections': sum(d['count'] for d in all_detections),
                    'frames_processed': len(all_detections),
                    'detections': all_detections
                }, f, indent=2)
            
        except Exception as e:
            processing_status[job_id]['status'] = 'error'
            processing_status[job_id]['error'] = str(e)
            # Send error signal
            if job_id in frame_streams:
                frame_streams[job_id].put(None)
    
    # Start processing thread
    thread = threading.Thread(target=process_video_thread)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'job_id': job_id,
        'message': 'Video processing started'
    })


@app.route('/api/detect/youtube', methods=['POST'])
def detect_youtube():
    """Download and process YouTube video"""
    if detector is None:
        return jsonify({'error': 'Model not loaded. Please check model file.'}), 500
    
    data = request.get_json()
    youtube_url = data.get('url')
    
    if not youtube_url:
        return jsonify({'error': 'No YouTube URL provided'}), 400
    
    # Validate YouTube URL
    youtube_regex = r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+'
    if not re.match(youtube_regex, youtube_url):
        return jsonify({'error': 'Invalid YouTube URL'}), 400
    
    # Generate unique filename
    import hashlib
    url_hash = hashlib.md5(youtube_url.encode()).hexdigest()[:10]
    timestamp = int(time.time())
    video_filename = f'youtube_{url_hash}_{timestamp}.mp4'
    
    # Ensure upload folder exists and get absolute path
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Use absolute paths for reliability
    video_path = os.path.abspath(os.path.join(UPLOAD_FOLDER, video_filename))
    output_filename = f'detected_youtube_{url_hash}_{timestamp}.mp4'
    output_path = os.path.abspath(os.path.join(OUTPUT_FOLDER, output_filename))
    
    # Create job ID
    job_id = video_filename.replace('.', '_')
    processing_status[job_id] = {
        'status': 'downloading',
        'progress': 0,
        'detections': [],
        'output_file': output_filename
    }
    
    # Create frame stream queue
    frame_streams[job_id] = queue.Queue(maxsize=60)
    
    def download_and_process():
        try:
            # Download YouTube video using yt-dlp Python module
            print(f"Downloading YouTube video: {youtube_url}")
            print(f"Saving to: {video_path}")
            
            ydl_opts = {
                'format': 'best[height<=720][ext=mp4]/best[height<=720]/best',
                'outtmpl': video_path,
                'quiet': False,
                'no_warnings': False,
                'noplaylist': True,
                'nocheckcertificate': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                print(f"Downloaded: {info.get('title', 'Unknown')}")
            
            if not os.path.exists(video_path):
                raise Exception(f"Downloaded video file not found at {video_path}")
            
            print(f"Download complete. File size: {os.path.getsize(video_path)} bytes")
            print(f"Processing video...")
            processing_status[job_id]['status'] = 'processing'
            
            # Get video FPS for proper playback timing
            cap = cv2.VideoCapture(video_path)
            video_fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            
            # Process the downloaded video
            all_detections = []
            frame_skip = 1  # Process every frame for YouTube videos
            
            for result in detector.process_video(video_path, output_path, frame_skip):
                processing_status[job_id]['progress'] = result['progress']
                
                frame_base64 = detector.frame_to_base64(result['frame'], quality=60)
                
                detection_summary = {
                    'frame': result['frame_number'],
                    'count': result['count'],
                    'detections': result['detections'],
                    'timestamp': result['timestamp']
                }
                all_detections.append(detection_summary)
                
                if len(all_detections) > 100:
                    all_detections.pop(0)
                
                processing_status[job_id]['detections'] = all_detections
                
                try:
                    stream_data = {
                        'type': 'frame',
                        'frame': frame_base64,
                        'frame_number': result['frame_number'],
                        'progress': result['progress'],
                        'detections': result['detections'],
                        'count': result['count'],
                        'fps': video_fps
                    }
                    frame_streams[job_id].put(stream_data, block=True, timeout=0.1)
                except queue.Full:
                    pass
            
            processing_status[job_id]['status'] = 'completed'
            processing_status[job_id]['progress'] = 100
            
            if job_id in frame_streams:
                frame_streams[job_id].put(None)
            
            print(f"YouTube video processing complete: {output_filename}")
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error processing YouTube video: {e}")
            print(f"Full traceback:\n{error_details}")
            processing_status[job_id]['status'] = 'error'
            processing_status[job_id]['error'] = f"{type(e).__name__}: {str(e)}"
            
            if job_id in frame_streams:
                frame_streams[job_id].put(None)
    
    # Start download and processing thread
    thread = threading.Thread(target=download_and_process)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'job_id': job_id,
        'message': 'YouTube video download and processing started'
    })


@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get processing status for a job"""
    if job_id not in processing_status:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(processing_status[job_id])


@app.route('/api/detect/image', methods=['POST'])
def detect_image():
    """Detect objects in an uploaded image file"""
    if detector is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    data = request.get_json()
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if not os.path.exists(image_path):
        return jsonify({'error': 'Image file not found'}), 404
    
    # Read image
    frame = cv2.imread(image_path)
    
    if frame is None:
        return jsonify({'error': 'Failed to read image'}), 400
    
    # Detect
    result = detector.detect_frame(frame)
    
    if result:
        # Generate output filename
        output_filename = f"detected_{filename}"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # Save annotated image
        cv2.imwrite(output_path, result['frame'])
        
        # Convert frame to base64 for preview
        result['frame_base64'] = detector.frame_to_base64(result['frame'])
        result['output_file'] = output_filename
        del result['frame']  # Remove numpy array
        
        return jsonify(result)
    else:
        return jsonify({'error': 'Detection failed'}), 500


@app.route('/api/detect/frame', methods=['POST'])
def detect_frame():
    """Detect objects in a single frame (for real-time detection)"""
    if detector is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    if 'frame' not in request.files:
        return jsonify({'error': 'No frame provided'}), 400
    
    file = request.files['frame']
    
    # Read image
    import numpy as np
    from PIL import Image
    
    image = Image.open(file.stream)
    frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Detect
    result = detector.detect_frame(frame)
    
    if result:
        # Convert frame to base64
        result['frame_base64'] = detector.frame_to_base64(result['frame'])
        del result['frame']  # Remove numpy array
        
        return jsonify(result)
    else:
        return jsonify({'error': 'Detection failed'}), 500


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download processed video"""
    # Use absolute path for send_file
    filepath = os.path.abspath(os.path.join(OUTPUT_FOLDER, filename))
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return jsonify({'error': f'File not found: {filename}'}), 404
    
    print(f"Sending file: {filepath}")
    return send_file(filepath, as_attachment=True, download_name=filename)


@app.route('/api/stream/<job_id>')
def stream_frames(job_id):
    """Stream processed frames in real-time using Server-Sent Events"""
    def generate():
        if job_id not in frame_streams:
            frame_streams[job_id] = queue.Queue(maxsize=30)
        
        stream_queue = frame_streams[job_id]
        
        while True:
            try:
                # Wait for frame data with timeout
                frame_data = stream_queue.get(timeout=30)
                
                if frame_data is None:  # End signal
                    yield f"data: {json.dumps({'type': 'complete'})}\n\n"
                    break
                
                # Send frame data as SSE
                yield f"data: {json.dumps(frame_data)}\n\n"
                
            except queue.Empty:
                # Send keepalive
                yield f"data: {json.dumps({'type': 'keepalive'})}\n\n"
            except Exception as e:
                print(f"Stream error: {e}")
                break
        
        # Cleanup
        if job_id in frame_streams:
            del frame_streams[job_id]
    
    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    print("=" * 60)
    print("Aerial Object Detection API Server")
    print("Powered by YOLO11s")
    print("=" * 60)
    
    # Clean up old files on startup
    print("\n🧹 Cleaning up old files...")
    cleanup_old_files()
    
    # Try to load default model (YOLO11s)
    model_files = ['models/yolo11s.pt', 'models/model.pt']
    model_loaded = False
    
    for model_file in model_files:
        if os.path.exists(model_file):
            print(f"\nFound model: {model_file}")
            if init_detector(model_file):
                model_loaded = True
                break
    
    if not model_loaded:
        print("\n⚠️  WARNING: No model file found!")
        print("Please place your model file in the models/ directory:")
        print("  - yolo11s.pt (YOLO11)")
        print("The server will start but detection will not work until a model is loaded.")
    
    print("\n" + "=" * 60)
    print("Server starting on http://localhost:5000")
    print(f"Auto-cleanup enabled: Files older than {MAX_FILE_AGE_HOURS}h will be deleted")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
