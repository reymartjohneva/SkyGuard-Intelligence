"""
Flask API Server for YOLO Object Detection
Provides REST API endpoints for video processing and real-time detection
Supports YOLOv8s, YOLO11s, and hot model switching
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


def init_detector(model_path='models/yolov8s.pt'):
    """Initialize the object detector"""
    global detector
    try:
        if os.path.exists(model_path):
            detector = ObjectDetector(model_path=model_path)
            return True
        else:
            print(f"Warning: Model file not found at {model_path}")
            print("Please place your model.pt or yolov8s.pt in the models/ directory")
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
    
    # Create frame stream queue with larger buffer
    frame_streams[job_id] = queue.Queue(maxsize=30)
    
    def process_video_thread():
        try:
            all_detections = []
            frame_skip = data.get('frame_skip', 1)
            
            # Frame rate limiting for smooth streaming
            last_frame_time = time.time()
            min_frame_interval = 1.0 / 30  # Limit to ~30 FPS max
            
            for result in detector.process_video(video_path, output_path, frame_skip):
                # Update progress
                processing_status[job_id]['progress'] = result['progress']
                
                # Convert frame to base64 with compression for faster transmission
                frame_base64 = detector.frame_to_base64(result['frame'], quality=70)
                
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
                
                # Stream frame to client with rate limiting
                current_time = time.time()
                time_since_last = current_time - last_frame_time
                
                # Only send frame if enough time has passed (prevents overwhelming client)
                if time_since_last >= min_frame_interval:
                    try:
                        stream_data = {
                            'type': 'frame',
                            'frame': frame_base64,
                            'frame_number': result['frame_number'],
                            'progress': result['progress'],
                            'detections': result['detections'],
                            'count': result['count']
                        }
                        frame_streams[job_id].put(stream_data, block=False)
                        last_frame_time = current_time
                    except queue.Full:
                        # Skip frame if queue is full
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


@app.route('/api/models', methods=['GET'])
def list_models():
    """List available models"""
    models = []
    model_dir = Path(MODEL_FOLDER)
    
    for model_file in model_dir.glob('*.pt'):
        models.append({
            'name': model_file.name,
            'path': str(model_file),
            'size': model_file.stat().st_size
        })
    
    return jsonify({'models': models})


@app.route('/api/model/load', methods=['POST'])
def load_model():
    """Load/switch to a specific model (hot model switching)"""
    global detector
    data = request.get_json()
    model_name = data.get('model_name', 'yolov8s.pt')
    model_path = os.path.join(MODEL_FOLDER, model_name)
    
    if not os.path.exists(model_path):
        return jsonify({'error': f'Model {model_name} not found'}), 404
    
    try:
        if detector is None:
            # Initialize new detector
            if init_detector(model_path):
                return jsonify({
                    'success': True, 
                    'message': f'Model {model_name} loaded successfully',
                    'current_model': detector.model_name
                })
            else:
                return jsonify({'error': 'Failed to load model'}), 500
        else:
            # Hot swap to new model
            if detector.switch_model(model_path):
                return jsonify({
                    'success': True, 
                    'message': f'Switched to model {model_name} successfully',
                    'current_model': detector.model_name
                })
            else:
                return jsonify({'error': 'Failed to switch model'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/model/current', methods=['GET'])
def get_current_model():
    """Get currently loaded model info"""
    if detector is None:
        return jsonify({'error': 'No model loaded'}), 404
    
    return jsonify({
        'model_name': detector.model_name,
        'model_path': detector.model_path,
        'device': detector.device,
        'conf_threshold': detector.conf_threshold
    })


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
    print("Supports: YOLOv8s, YOLO11s, Hot Model Switching")
    print("=" * 60)
    
    # Clean up old files on startup
    print("\n🧹 Cleaning up old files...")
    cleanup_old_files()
    
    # Try to load default model (prefer YOLO11s if available)
    model_files = ['models/yolo11s.pt', 'models/yolov8s.pt', 'models/model.pt']
    model_loaded = False
    
    for model_file in model_files:
        if os.path.exists(model_file):
            print(f"\nFound model: {model_file}")
            if init_detector(model_file):
                model_loaded = True
                break
    
    if not model_loaded:
        print("\n⚠️  WARNING: No model file found!")
        print("Please place your model files in the models/ directory:")
        print("  - yolo11s.pt (YOLO11)")
        print("  - yolov8s.pt (YOLOv8)")
        print("The server will start but detection will not work until a model is loaded.")
    
    print("\n" + "=" * 60)
    print("Server starting on http://localhost:5000")
    print(f"Auto-cleanup enabled: Files older than {MAX_FILE_AGE_HOURS}h will be deleted")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
