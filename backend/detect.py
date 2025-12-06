"""
YOLO11 Object Detection Backend
Handles video processing and real-time object detection
"""

import cv2
import torch
from ultralytics import YOLO
import numpy as np
from pathlib import Path
import json
import base64
from datetime import datetime

class ObjectDetector:
    def __init__(self, model_path='models/yolo11s.pt', conf_threshold=0.25):
        """
        Initialize the object detector
        
        Args:
            model_path: Path to YOLO11 model file
            conf_threshold: Confidence threshold for detections (lowered for better recall)
        """
        self.model_path = model_path
        self.model_name = Path(model_path).stem  # Get model name without extension
        self.conf_threshold = conf_threshold
        self.iou_threshold = 0.45  # IOU threshold for NMS (lower = allow more overlapping detections)
        self.imgsz = 640  # Image size for inference
        self.max_det = 300  # Maximum detections per image
        self.model = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.half = False  # Half precision mode
        
        # ONLY 2 classes from trained model: civilian and soldier
        self.class_names = {
            0: 'civilian',
            1: 'soldier'
        }
        
        # Allowed classes - only detect these 2 classes
        self.allowed_classes = {'civilian', 'soldier'}
        
        # Class-specific colors (BGR format)
        self.colors = {
            'soldier': (0, 0, 255),      # Red
            'civilian': (0, 255, 0)      # Green
        }
        
        # Augmentation settings for better detection
        self.augment = True  # Enable test-time augmentation
        
        self.load_model()
    
    def load_model(self):
        """Load the YOLO11 model with optimizations"""
        try:
            print(f"Loading model: {self.model_name} from {self.model_path}")
            print(f"Using device: {self.device}")
            
            self.model = YOLO(self.model_path)
            self.model.to(self.device)
            
            # Enable half precision for GPU to improve speed
            if self.device == 'cuda':
                self.half = True
                print("Half precision (FP16) enabled for faster inference")
            
            # Print the actual class names from the model
            if hasattr(self.model, 'names'):
                print(f"\n{'='*60}")
                print("Model class names detected:")
                for idx, name in self.model.names.items():
                    print(f"  Class {idx}: {name}")
                print(f"{'='*60}\n")
                
                # Update our class names based on model
                self.class_names = {int(idx): name.lower() for idx, name in self.model.names.items()}
                self.allowed_classes = {name.lower() for name in self.model.names.values()}
                
                # Verify only civilian and soldier classes exist
                if set(self.class_names.values()) != {'civilian', 'soldier'}:
                    print("⚠️  WARNING: Model has unexpected classes!")
                    print(f"   Expected: civilian, soldier")
                    print(f"   Found: {', '.join(self.class_names.values())}")
                    print("   Detection may not work correctly.\n")
            
            # Warm up the model with a dummy image to reduce first inference latency
            print("Warming up model...")
            dummy_img = np.zeros((self.imgsz, self.imgsz, 3), dtype=np.uint8)
            _ = self.model(dummy_img, conf=self.conf_threshold, iou=self.iou_threshold, 
                          imgsz=self.imgsz, half=self.half, max_det=self.max_det, 
                          agnostic_nms=False, verbose=False)
            
            print(f"✅ Model {self.model_name} loaded and warmed up successfully!")
            print(f"Detection settings: conf={self.conf_threshold}, iou={self.iou_threshold}, imgsz={self.imgsz}, max_det={self.max_det}")
            print(f"Augmentation: {'Enabled' if self.augment else 'Disabled'}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def draw_detections(self, frame, detections):
        """
        Draw bounding boxes and labels on frame
        
        Args:
            frame: Input frame
            detections: Detection results
            
        Returns:
            Annotated frame
        """
        annotated_frame = frame.copy()
        
        for det in detections:
            x1, y1, x2, y2 = map(int, det['bbox'])
            class_name = det['class']
            confidence = det['confidence']
            
            # Get color based on class name
            color = self.colors.get(class_name, (128, 128, 128))
            
            # Draw bounding box with higher thickness for better visibility
            thickness = 3
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, thickness)
            
            # Prepare label text with detailed confidence percentage
            label = f"{class_name.upper()} {confidence:.1%}"
            
            # Get text size for background
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            font_thickness = 2
            (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, font_thickness)
            
            # Calculate label position (above the box)
            label_y = y1 - 10 if y1 - 10 > text_height else y1 + text_height + 10
            
            # Draw semi-transparent background for label
            overlay = annotated_frame.copy()
            cv2.rectangle(overlay, 
                         (x1, label_y - text_height - 8),
                         (x1 + text_width + 10, label_y + baseline + 2),
                         color, -1)
            
            # Blend the overlay with the original frame for transparency
            alpha = 0.8
            cv2.addWeighted(overlay, alpha, annotated_frame, 1 - alpha, 0, annotated_frame)
            
            # Draw black outline for text (for better visibility)
            cv2.putText(annotated_frame, label,
                       (x1 + 5, label_y),
                       font, font_scale, (0, 0, 0), font_thickness + 2, cv2.LINE_AA)
            
            # Draw white text on top
            cv2.putText(annotated_frame, label,
                       (x1 + 5, label_y),
                       font, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)
            
            # Add class-specific indicator
            if class_name == 'soldier':
                # Draw small circle in top-right corner of box
                cv2.circle(annotated_frame, (x2 - 10, y1 + 10), 6, color, -1)
                cv2.circle(annotated_frame, (x2 - 10, y1 + 10), 6, (255, 255, 255), 1)
            elif class_name == 'civilian':
                # Draw small square in top-right corner of box
                cv2.rectangle(annotated_frame, (x2 - 16, y1 + 4), (x2 - 4, y1 + 16), color, -1)
                cv2.rectangle(annotated_frame, (x2 - 16, y1 + 4), (x2 - 4, y1 + 16), (255, 255, 255), 1)
        
        return annotated_frame
    
    def detect_frame(self, frame, use_enhancement=False):
        """
        Perform detection on a single frame with optimized settings
        
        Args:
            frame: Input frame (numpy array)
            use_enhancement: Apply CLAHE enhancement (slower but better for low-light)
            
        Returns:
            dict: Detection results and annotated frame
        """
        if self.model is None:
            return None
        
        # Preprocess frame for better detection accuracy
        # Ensure RGB color space (YOLO11 expects RGB)
        if len(frame.shape) == 2:  # Grayscale
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        elif frame.shape[2] == 4:  # RGBA
            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
        
        # Optional: Apply CLAHE for better detection in varying lighting
        # Disabled by default for better performance during real-time streaming
        if use_enhancement:
            lab = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8,8))
            l = clahe.apply(l)
            enhanced_frame = cv2.merge([l, a, b])
            enhanced_frame = cv2.cvtColor(enhanced_frame, cv2.COLOR_LAB2RGB)
        else:
            enhanced_frame = frame
        
        # Perform inference with optimized parameters
        # Custom model trained with class 0 = civilian, class 1 = soldier
        results = self.model(
            enhanced_frame, 
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            imgsz=self.imgsz,
            half=self.half,
            augment=self.augment,  # Enable test-time augmentation for better accuracy
            agnostic_nms=False,  # Class-specific NMS for better class distinction
            max_det=self.max_det,  # Maximum detections per image
            classes=[0, 1],  # Detect class 0 (civilian) and class 1 (soldier)
            verbose=False
        )
        
        detections = []
        
        # Process results
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                # Extract box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                
                # Get class and confidence
                cls = int(box.cls[0].cpu().numpy())
                conf = float(box.conf[0].cpu().numpy())
                
                # Get class name from the model
                if hasattr(result, 'names'):
                    detected_class = result.names[cls].lower()
                else:
                    detected_class = self.class_names.get(cls, 'unknown')
                
                # Only accept civilian and soldier classes
                if detected_class not in self.allowed_classes:
                    print(f"Skipped detection: Class '{detected_class}' not in allowed classes")
                    continue
                
                detection = {
                    'bbox': [float(x1), float(y1), float(x2), float(y2)],
                    'class': detected_class,
                    'class_id': cls,
                    'confidence': conf
                }
                
                detections.append(detection)
        
        # Draw detections on frame
        annotated_frame = self.draw_detections(frame, detections)
        
        return {
            'detections': detections,
            'frame': annotated_frame,
            'count': len(detections),
            'timestamp': datetime.now().isoformat()
        }
    
    def process_video(self, video_path, output_path=None, frame_skip=1):
        """
        Process entire video file
        
        Args:
            video_path: Path to input video
            output_path: Path to save output video (optional)
            frame_skip: Process every nth frame for speed
            
        Yields:
            Detection results for each processed frame
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Initialize video writer if output path provided
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            # Keep original FPS for output video to maintain timing
            # Frame skip only affects processing, not output playback speed
            output_fps = fps
            writer = cv2.VideoWriter(output_path, fourcc, output_fps, (width, height))
            print(f"Output video FPS: {output_fps:.2f} (original: {fps}, frame_skip: {frame_skip})")
        
        frame_count = 0
        processed_count = 0
        
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                frame_count += 1
                
                # Skip frames for performance
                if frame_count % frame_skip != 0:
                    continue
                
                # Detect objects
                result = self.detect_frame(frame)
                
                if result:
                    processed_count += 1
                    result['frame_number'] = frame_count
                    result['total_frames'] = total_frames
                    result['progress'] = (frame_count / total_frames) * 100
                    
                    # Write annotated frame
                    if writer:
                        writer.write(result['frame'])
                    
                    yield result
        
        finally:
            cap.release()
            if writer:
                writer.release()
    
    def frame_to_base64(self, frame, quality=70):
        """Convert frame to base64 for transmission with compression"""
        # Reduce JPEG quality for faster encoding and smaller size
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
        _, buffer = cv2.imencode('.jpg', frame, encode_params)
        return base64.b64encode(buffer).decode('utf-8')


if __name__ == '__main__':
    # Test the detector
    detector = ObjectDetector()
    
    print("\nObject Detector initialized successfully!")
    print(f"Device: {detector.device}")
    print(f"Model: {detector.model_path}")
    print(f"Ready for detection...")
