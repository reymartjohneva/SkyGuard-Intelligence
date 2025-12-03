// Detection App JavaScript
// Handles video upload, processing, and results display

const API_BASE = 'http://localhost:5000/api';

let currentJobId = null;
let currentFile = null;
let currentFileType = 'video'; // 'video' or 'image'
let statusCheckInterval = null;

// DOM Elements
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const fileType = document.getElementById('fileType');
const controlsSection = document.getElementById('controlsSection');
const videoOptions = document.getElementById('videoOptions');
const progressSection = document.getElementById('progressSection');
const resultsSection = document.getElementById('resultsSection');
const imagePreview = document.getElementById('imagePreview');
const previewSection = document.getElementById('previewSection');
const logContainer = document.getElementById('logContainer');
const serverStatusDot = document.getElementById('serverStatusDot');
const serverStatusText = document.getElementById('serverStatusText');

// Check server health
async function checkServerHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        
        if (data.status === 'running') {
            serverStatusDot.className = 'status-dot online';
            serverStatusText.textContent = `Server Online | Model: ${data.model_loaded ? 'Loaded' : 'Not Loaded'} | Device: ${data.device}`;
            addLog('✅ Connected to AI server successfully', 'success');
            return true;
        }
    } catch (error) {
        serverStatusDot.className = 'status-dot offline';
        serverStatusText.textContent = 'Server Offline - Please start the backend server';
        addLog('❌ Cannot connect to AI server. Please run: python backend/server.py', 'error');
        return false;
    }
}

// Add log entry
function addLog(message, type = 'info') {
    const logEntry = document.createElement('p');
    logEntry.className = `log-entry ${type}`;
    const timestamp = new Date().toLocaleTimeString();
    logEntry.textContent = `[${timestamp}] ${message}`;
    logContainer.appendChild(logEntry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Switch file type (video/image)
function switchFileType(type) {
    currentFileType = type;
    
    // Update toggle buttons
    document.getElementById('videoToggle').classList.toggle('active', type === 'video');
    document.getElementById('imageToggle').classList.toggle('active', type === 'image');
    
    // Update UI text
    if (type === 'video') {
        fileInput.accept = 'video/*';
        document.getElementById('uploadText').textContent = 'Drag & drop video file here or click to browse';
        document.getElementById('uploadHint').textContent = 'Supported formats: MP4, AVI, MOV, MKV, WebM';
        document.getElementById('selectBtnText').textContent = 'Select Video';
    } else {
        fileInput.accept = 'image/*';
        document.getElementById('uploadText').textContent = 'Drag & drop image file here or click to browse';
        document.getElementById('uploadHint').textContent = 'Supported formats: JPG, PNG, BMP, TIFF, WebP';
        document.getElementById('selectBtnText').textContent = 'Select Image';
    }
    
    // Reset current file
    currentFile = null;
    fileInfo.style.display = 'none';
    controlsSection.style.display = 'none';
    addLog(`Switched to ${type} mode`, 'info');
}

// Handle file selection
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        currentFile = file;
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        fileType.textContent = currentFileType.toUpperCase();
        fileInfo.style.display = 'block';
        controlsSection.style.display = 'block';
        
        // Show/hide frame skip option based on file type
        if (videoOptions) {
            videoOptions.style.display = currentFileType === 'video' ? 'block' : 'none';
        }
        
        addLog(`📄 ${currentFileType} selected: ${file.name}`, 'info');
    }
});

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#667eea';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = '#dee2e6';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#dee2e6';
    
    const file = e.dataTransfer.files[0];
    if (!file) return;
    
    // Check file type
    const isValidType = currentFileType === 'video' ? 
        file.type.startsWith('video/') : 
        file.type.startsWith('image/');
    
    if (file && isValidType) {
        currentFile = file;
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        fileType.textContent = currentFileType.toUpperCase();
        fileInfo.style.display = 'block';
        controlsSection.style.display = 'block';
        
        // Show/hide frame skip option
        if (videoOptions) {
            videoOptions.style.display = currentFileType === 'video' ? 'block' : 'none';
        }
        
        addLog(`📄 ${currentFileType} selected: ${file.name}`, 'info');
    } else {
        addLog(`❌ Please select a valid ${currentFileType} file`, 'error');
    }
});

// Upload file (video or image)
async function uploadFile() {
    if (!currentFile) {
        addLog('❌ No file selected', 'error');
        return null;
    }
    
    const formData = new FormData();
    formData.append(currentFileType, currentFile); // 'video' or 'image'
    
    try {
        addLog(`⬆️ Uploading ${currentFileType}...`, 'info');
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            addLog(`✅ ${currentFileType} uploaded successfully`, 'success');
            return data.filename;
        } else {
            addLog(`❌ Upload failed: ${data.error}`, 'error');
            return null;
        }
    } catch (error) {
        addLog(`❌ Upload error: ${error.message}`, 'error');
        return null;
    }
}

// Start processing
document.getElementById('startProcessing').addEventListener('click', async () => {
    const serverOnline = await checkServerHealth();
    if (!serverOnline) {
        alert('Backend server is not running. Please start it with: python backend/server.py');
        return;
    }
    
    const filename = await uploadFile();
    if (!filename) return;
    
    if (currentFileType === 'image') {
        // Process image
        await processImage(filename);
    } else {
        // Process video
        await processVideo(filename);
    }
});

// Process image
async function processImage(filename) {
    try {
        addLog('🚀 Starting object detection on image...', 'info');
        
        const response = await fetch(`${API_BASE}/detect/image`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ filename: filename })
        });
        
        const data = await response.json();
        
        if (data.frame_base64) {
            // Show results
            resultsSection.style.display = 'block';
            imagePreview.style.display = 'block';
            document.getElementById('detectedImage').src = `data:image/jpeg;base64,${data.frame_base64}`;
            
            // Update stats - count by class type
            let soldierCount = 0, civilianCount = 0, otherCount = 0;
            data.detections.forEach(det => {
                const className = det.class.toLowerCase();
                if (className === 'soldier') soldierCount++;
                else if (className === 'civilian') civilianCount++;
                else otherCount++;
            });
            
            const totalCount = soldierCount + civilianCount + otherCount;
            
            document.getElementById('totalDetections').textContent = totalCount;
            document.getElementById('soldierCount').textContent = soldierCount;
            document.getElementById('civilianCount').textContent = civilianCount;
            document.getElementById('otherCount').textContent = otherCount;
            
            // Show download button
            document.getElementById('downloadResult').style.display = 'inline-block';
            document.getElementById('downloadResult').onclick = () => {
                window.open(`${API_BASE}/download/${data.output_file}`, '_blank');
            };
            
            addLog(`✅ Image processed! Detected ${data.count} objects (${soldierCount} soldiers, ${civilianCount} civilians)`, 'success');
        } else {
            addLog(`❌ Failed to process image: ${data.error}`, 'error');
        }
    } catch (error) {
        addLog(`❌ Error: ${error.message}`, 'error');
    }
}

// Process video
async function processVideo(filename) {
    const frameSkip = document.getElementById('frameSkip').value;
    
    try {
        addLog('🚀 Starting object detection...', 'info');
        
        const response = await fetch(`${API_BASE}/detect/video`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename: filename,
                frame_skip: parseInt(frameSkip)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentJobId = data.job_id;
            addLog(`✅ Processing started (Job ID: ${currentJobId})`, 'success');
            
            // Show progress and results sections
            progressSection.style.display = 'block';
            resultsSection.style.display = 'block';
            
            // Disable start button
            document.getElementById('startProcessing').disabled = true;
            document.getElementById('cancelProcessing').disabled = false;
            
            // Start monitoring progress
            startProgressMonitoring();
        } else {
            addLog(`❌ Failed to start processing: ${data.error}`, 'error');
        }
    } catch (error) {
        addLog(`❌ Error: ${error.message}`, 'error');
    }
}

// Monitor processing progress
function startProgressMonitoring() {
    statusCheckInterval = setInterval(async () => {
        if (!currentJobId) return;
        
        try {
            const response = await fetch(`${API_BASE}/status/${currentJobId}`);
            const data = await response.json();
            
            // Update progress bar
            const progress = Math.round(data.progress || 0);
            document.getElementById('progressBar').style.width = `${progress}%`;
            document.getElementById('progressText').textContent = `${progress}%`;
            document.getElementById('processingStatus').textContent = data.status;
            
            // Update stats
            if (data.detections && data.detections.length > 0) {
                const latestDetections = data.detections;
                const totalDetections = latestDetections.reduce((sum, d) => sum + d.count, 0);
                
                document.getElementById('framesProcessed').textContent = latestDetections.length;
                
                // Count by class type
                let soldierCount = 0, civilianCount = 0, otherCount = 0;
                
                latestDetections.forEach(frame => {
                    frame.detections.forEach(det => {
                        const className = det.class.toLowerCase();
                        if (className === 'soldier') soldierCount++;
                        else if (className === 'civilian') civilianCount++;
                        else otherCount++;
                    });
                });
                
                const totalCount = soldierCount + civilianCount + otherCount;
                
                document.getElementById('totalDetections').textContent = totalCount;
                document.getElementById('soldierCount').textContent = soldierCount;
                document.getElementById('civilianCount').textContent = civilianCount;
                document.getElementById('otherCount').textContent = otherCount;
            }
            
            // Check if completed
            if (data.status === 'completed') {
                clearInterval(statusCheckInterval);
                addLog('✅ Processing completed successfully!', 'success');
                
                document.getElementById('startProcessing').disabled = false;
                document.getElementById('cancelProcessing').disabled = true;
                document.getElementById('downloadResult').style.display = 'inline-block';
                document.getElementById('viewDetails').style.display = 'inline-block';
                
                // Show completion message
                addLog(`🎉 Video processing complete! Detected ${document.getElementById('totalDetections').textContent} objects`, 'success');
            } else if (data.status === 'error') {
                clearInterval(statusCheckInterval);
                addLog(`❌ Processing error: ${data.error}`, 'error');
                document.getElementById('startProcessing').disabled = false;
            }
            
        } catch (error) {
            console.error('Status check error:', error);
        }
    }, 1000);
}

// Download processed video
document.getElementById('downloadResult').addEventListener('click', async () => {
    if (!currentJobId) return;
    
    try {
        const response = await fetch(`${API_BASE}/status/${currentJobId}`);
        const data = await response.json();
        
        if (data.output_file) {
            const downloadUrl = `${API_BASE}/download/${data.output_file}`;
            window.open(downloadUrl, '_blank');
            addLog(`⬇️ Downloading processed video: ${data.output_file}`, 'info');
        }
    } catch (error) {
        addLog(`❌ Download error: ${error.message}`, 'error');
    }
});

// View details
document.getElementById('viewDetails').addEventListener('click', () => {
    addLog('📊 Generating detailed report...', 'info');
    // This could open a new window or modal with detailed detection information
    alert('Detailed report feature - View frame-by-frame detection results');
});

// Cancel processing
document.getElementById('cancelProcessing').addEventListener('click', () => {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        statusCheckInterval = null;
    }
    addLog('⚠️ Processing cancelled by user', 'warning');
    document.getElementById('startProcessing').disabled = false;
    document.getElementById('cancelProcessing').disabled = true;
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    addLog('🚀 Application initialized', 'success');
    checkServerHealth();
    
    // Check server health every 30 seconds
    setInterval(checkServerHealth, 30000);
});

// Make switchFileType globally accessible for HTML onclick
window.switchFileType = switchFileType;
