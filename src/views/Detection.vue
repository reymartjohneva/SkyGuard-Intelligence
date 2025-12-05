<template>
  <div class="detection-page">
    <div class="detection-grid">
      <!-- Left Sidebar: Upload and Options -->
      <div class="sidebar">
        <!-- Header -->
        <div class="header-section">
          <button class="btn-back" @click="goBack">← Back</button>
          <h1>🛡️ Detection</h1>
          <div class="server-status">
            <span :class="['status-dot', serverOnline ? 'online' : 'offline']"></span>
            <span>{{ serverStatusText }}</span>
          </div>
        </div>

        <!-- Upload Section -->
        <div class="upload-card">
          <h2>📁 Upload File</h2>
          
          <div class="file-type-toggle">
            <button 
              :class="['toggle-btn', { active: currentFileType === 'video' }]" 
              @click="switchFileType('video')"
            >
              📹 Video
            </button>
            <button 
              :class="['toggle-btn', { active: currentFileType === 'image' }]" 
              @click="switchFileType('image')"
            >
              🖼️ Image
            </button>
          </div>
          
          <div 
            class="upload-area" 
            :class="{ 'processing': isProcessing }"
            @dragover.prevent="onDragOver"
            @dragleave.prevent="onDragLeave"
            @drop.prevent="onDrop"
            @click="!isProcessing && $refs.fileInput.click()"
          >
            <div class="upload-icon">📁</div>
            <p>{{ uploadText }}</p>
            <p class="upload-hint">{{ isProcessing ? '⏳ Processing current file...' : '⚡ Auto-processing enabled' }}</p>
            <input 
              type="file" 
              ref="fileInput"
              :accept="fileAccept"
              @change="onFileSelect"
              hidden
            >
            <button class="btn-upload" @click.stop="!isProcessing && $refs.fileInput.click()" :disabled="isProcessing">
              {{ isProcessing ? '⏳ Processing...' : 'Select File' }}
            </button>
          </div>
          
          <div v-if="currentFile" class="file-info">
            <p><strong>{{ currentFile.name }}</strong></p>
            <p>{{ formatFileSize(currentFile.size) }}</p>
          </div>
        </div>

        <!-- Options Section -->
        <div class="options-card">
          <h2>⚙️ Options</h2>
          
          <div class="option-group">
            <label>🤖 Model:</label>
            <select v-model="selectedModel" @change="switchModel">
              <option value="yolo11s.pt">YOLO11s</option>
              <option value="yolov8s.pt">YOLOv8s</option>
            </select>
          </div>
          
          <div v-if="currentFileType === 'video'" class="option-group">
            <label>Frame Skip:</label>
            <select v-model="frameSkip">
              <option value="1">Every Frame</option>
              <option value="2">Every 2nd</option>
              <option value="3">Every 3rd</option>
              <option value="5">Every 5th</option>
            </select>
          </div>

          <button 
            v-if="isProcessing" 
            class="btn-cancel" 
            @click="cancelProcessing"
          >
            ❌ Stop
          </button>
        </div>

        <!-- Processing Progress -->
        <div v-if="isProcessing" class="progress-card">
          <h2>📊 Progress</h2>
          <div class="progress-bar-container">
            <div class="progress-bar" :style="{ width: progress + '%' }"></div>
            <span class="progress-text">{{ progress }}%</span>
          </div>
          <div class="stats">
            <div class="stat">
              <span>Frames:</span>
              <span>{{ framesProcessed }}</span>
            </div>
            <div class="stat">
              <span>Detections:</span>
              <span>{{ totalDetections }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Live Preview -->
      <div class="preview-panel">
        <h2>🎬 Live Preview</h2>
        <div class="preview-container">
          <canvas v-if="currentFileType === 'video'" ref="videoCanvas" class="preview-canvas"></canvas>
          <img v-else-if="detectedImageUrl" :src="detectedImageUrl" class="preview-image">
          <div v-else class="preview-placeholder">
            <p>No media loaded</p>
          </div>
          <div v-if="isProcessing" class="processing-overlay">
            <div class="spinner"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const API_BASE = 'http://localhost:5000/api'

// Server status
const serverOnline = ref(false)
const serverStatusText = ref('Checking...')

// Model
const selectedModel = ref('yolo11s.pt')

// File upload
const currentFile = ref(null)
const currentFileType = ref('video')
const fileInput = ref(null)

// Processing
const isProcessing = ref(false)
const currentJobId = ref(null)
const frameSkip = ref('3')
const progress = ref(0)
const framesProcessed = ref(0)

// Results
const totalDetections = ref(0)
const soldierCount = ref(0)
const civilianCount = ref(0)
const detectedImageUrl = ref(null)
const videoCanvas = ref(null)
let eventSource = null
let statusCheckInterval = null

// Computed
const uploadText = computed(() => {
  return currentFileType.value === 'video' 
    ? 'Drag & drop video or click to browse'
    : 'Drag & drop image or click to browse'
})

const fileAccept = computed(() => {
  return currentFileType.value === 'video' ? 'video/*' : 'image/*'
})

// Methods
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const checkServerHealth = async () => {
  try {
    const response = await axios.get(`${API_BASE}/health`)
    const data = response.data
    
    if (data.status === 'running') {
      serverOnline.value = true
      serverStatusText.value = 'Online'
      if (data.current_model) {
        selectedModel.value = data.current_model + '.pt'
      }
      return true
    }
  } catch (error) {
    serverOnline.value = false
    serverStatusText.value = 'Offline'
    return false
  }
}

const switchModel = async () => {
  try {
    const response = await axios.post(`${API_BASE}/model/load`, {
      model_name: selectedModel.value
    })
    if (response.data.success) {
      serverStatusText.value = `Model: ${response.data.current_model}`
    }
  } catch (error) {
    console.error('Model switch error:', error)
  }
}

const cleanupPreviousProcessing = () => {
  // Close EventSource
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }
  
  // Clear intervals
  if (statusCheckInterval) {
    clearInterval(statusCheckInterval)
    statusCheckInterval = null
  }
  
  // Reset state
  isProcessing.value = false
  currentJobId.value = null
  progress.value = 0
  framesProcessed.value = 0
  totalDetections.value = 0
  soldierCount.value = 0
  civilianCount.value = 0
  detectedImageUrl.value = null
}

const switchFileType = (type) => {
  cleanupPreviousProcessing()
  currentFileType.value = type
  currentFile.value = null
}

const onFileSelect = async (event) => {
  const file = event.target.files[0]
  if (file) {
    cleanupPreviousProcessing()
    currentFile.value = file
    await startProcessing()
    // Reset file input to allow re-uploading same file
    event.target.value = ''
  }
}

const onDragOver = (event) => {
  event.currentTarget.style.borderColor = '#667eea'
}

const onDragLeave = (event) => {
  event.currentTarget.style.borderColor = '#dee2e6'
}

const onDrop = async (event) => {
  event.currentTarget.style.borderColor = '#dee2e6'
  
  const file = event.dataTransfer.files[0]
  if (!file) return
  
  const isValidType = currentFileType.value === 'video' 
    ? file.type.startsWith('video/') 
    : file.type.startsWith('image/')
  
  if (file && isValidType) {
    cleanupPreviousProcessing()
    currentFile.value = file
    await startProcessing()
  } else {
    alert(`Please select a valid ${currentFileType.value} file`)
  }
}

const uploadFile = async () => {
  if (!currentFile.value) return null
  
  const formData = new FormData()
  formData.append(currentFileType.value, currentFile.value)
  
  try {
    const response = await axios.post(`${API_BASE}/upload`, formData)
    const data = response.data
    return data.success ? data.filename : null
  } catch (error) {
    console.error('Upload error:', error)
    return null
  }
}

const startProcessing = async () => {
  const serverHealthy = await checkServerHealth()
  if (!serverHealthy) {
    alert('Backend server is not running.')
    return
  }
  
  const filename = await uploadFile()
  if (!filename) return
  
  if (currentFileType.value === 'image') {
    await processImage(filename)
  } else {
    await processVideo(filename)
  }
}

const processImage = async (filename) => {
  try {
    const response = await axios.post(`${API_BASE}/detect/image`, {
      filename: filename
    })
    
    const data = response.data
    
    if (data.frame_base64) {
      detectedImageUrl.value = `data:image/jpeg;base64,${data.frame_base64}`
      
      let soldiers = 0, civilians = 0
      data.detections.forEach(det => {
        const className = det.class.toLowerCase()
        if (className === 'soldier') soldiers++
        else if (className === 'civilian') civilians++
      })
      
      totalDetections.value = data.count
      soldierCount.value = soldiers
      civilianCount.value = civilians
    }
  } catch (error) {
    console.error('Image processing error:', error)
  }
}

const processVideo = async (filename) => {
  try {
    const response = await axios.post(`${API_BASE}/detect/video`, {
      filename: filename,
      frame_skip: parseInt(frameSkip.value)
    })
    
    const data = response.data
    
    if (data.success) {
      currentJobId.value = data.job_id
      isProcessing.value = true
      
      nextTick(() => {
        if (videoCanvas.value) {
          const canvas = videoCanvas.value
          const ctx = canvas.getContext('2d')
          const container = canvas.parentElement
          canvas.width = container.clientWidth || 1280
          canvas.height = (canvas.width * 9) / 16
          // Clear canvas
          ctx.clearRect(0, 0, canvas.width, canvas.height)
        }
      })
      
      startProgressMonitoring()
      connectToStream(currentJobId.value)
    }
  } catch (error) {
    console.error('Video processing error:', error)
  }
}

const connectToStream = (jobId) => {
  if (eventSource) {
    eventSource.close()
  }
  
  eventSource = new EventSource(`${API_BASE}/stream/${jobId}`)
  
  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      
      if (data.type === 'frame') {
        if (videoCanvas.value) {
          const canvas = videoCanvas.value
          const ctx = canvas.getContext('2d')
          
          const img = new Image()
          img.onload = () => {
            const container = canvas.parentElement
            const containerWidth = container.clientWidth
            const aspectRatio = img.height / img.width
            
            canvas.width = containerWidth
            canvas.height = containerWidth * aspectRatio
            
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
          }
          img.src = `data:image/jpeg;base64,${data.frame}`
        }
        
        if (data.detections) {
          let soldiers = 0, civilians = 0
          data.detections.forEach(det => {
            const className = det.class.toLowerCase()
            if (className === 'soldier') soldiers++
            else if (className === 'civilian') civilians++
          })
          
          soldierCount.value = soldiers
          civilianCount.value = civilians
          totalDetections.value = soldiers + civilians
        }
      } else if (data.type === 'complete') {
        eventSource.close()
        eventSource = null
        isProcessing.value = false
      }
    } catch (error) {
      console.error('Stream error:', error)
    }
  }
  
  eventSource.onerror = () => {
    eventSource.close()
    eventSource = null
    isProcessing.value = false
  }
}

const startProgressMonitoring = () => {
  if (statusCheckInterval) {
    clearInterval(statusCheckInterval)
  }
  
  statusCheckInterval = setInterval(async () => {
    if (!currentJobId.value) return
    
    try {
      const response = await axios.get(`${API_BASE}/status/${currentJobId.value}`)
      const data = response.data
      
      progress.value = data.progress || 0
      framesProcessed.value = data.frames_processed || 0
      
      if (data.status === 'completed' || data.status === 'error') {
        clearInterval(statusCheckInterval)
        isProcessing.value = false
      }
    } catch (error) {
      console.error('Status check error:', error)
    }
  }, 1000)
}

const cancelProcessing = async () => {
  if (currentJobId.value) {
    try {
      await axios.post(`${API_BASE}/cancel/${currentJobId.value}`)
    } catch (error) {
      console.error('Cancel error:', error)
    }
  }
  
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }
  
  if (statusCheckInterval) {
    clearInterval(statusCheckInterval)
  }
  
  isProcessing.value = false
  currentJobId.value = null
}

const goBack = () => {
  router.push('/')
}

onMounted(() => {
  checkServerHealth()
})

onUnmounted(() => {
  if (eventSource) {
    eventSource.close()
  }
  if (statusCheckInterval) {
    clearInterval(statusCheckInterval)
  }
})
</script>

<style scoped>
.detection-page {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

.detection-grid {
  display: grid;
  grid-template-columns: 400px 1fr;
  height: 100vh;
  gap: 0;
}

/* Left Sidebar */
.sidebar {
  background: #f8f9fa;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
}

.header-section {
  background: white;
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.btn-back {
  background: none;
  border: none;
  color: #667eea;
  cursor: pointer;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  padding: 0.5rem;
}

.btn-back:hover {
  color: #764ba2;
}

h1 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  color: #2c3e50;
}

.server-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #6c757d;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.online {
  background: #10b981;
}

.status-dot.offline {
  background: #ef4444;
}

/* Upload Card */
.upload-card, .options-card, .progress-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

h2 {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  color: #2c3e50;
}

.file-type-toggle {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.toggle-btn {
  flex: 1;
  padding: 0.75rem;
  border: 2px solid #dee2e6;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s;
}

.toggle-btn.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.upload-area {
  border: 2px dashed #dee2e6;
  border-radius: 12px;
  padding: 2rem 1rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-area:hover:not(.processing) {
  border-color: #667eea;
  background: #f8f9fa;
}

.upload-area.processing {
  opacity: 0.7;
  cursor: not-allowed;
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.upload-area p {
  margin: 0.5rem 0;
  color: #6c757d;
}

.upload-hint {
  font-size: 0.85rem;
  color: #8b5cf6;
}

.btn-upload {
  margin-top: 1rem;
  padding: 0.75rem 2rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s;
}

.btn-upload:hover:not(:disabled) {
  background: #764ba2;
}

.btn-upload:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.file-info {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  font-size: 0.9rem;
}

.file-info p {
  margin: 0.25rem 0;
}

/* Options Card */
.option-group {
  margin-bottom: 1rem;
}

.option-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #2c3e50;
  font-weight: 500;
  font-size: 0.9rem;
}

.option-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  font-size: 0.9rem;
}

.btn-cancel {
  width: 100%;
  padding: 0.75rem;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  margin-top: 1rem;
}

.btn-cancel:hover {
  background: #dc2626;
}

/* Progress Card */
.progress-bar-container {
  position: relative;
  height: 30px;
  background: #e9ecef;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.3s;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #2c3e50;
  font-weight: 600;
  font-size: 0.9rem;
}

.stats {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 6px;
  font-size: 0.9rem;
}

/* Right Preview Panel */
.preview-panel {
  background: #1a1a1a;
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
}

.preview-panel h2 {
  color: white;
  margin: 0 0 1rem 0;
  font-size: 1.3rem;
}

.preview-container {
  flex: 1;
  background: #000;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.preview-canvas, .preview-image {
  max-width: 100%;
  max-height: 100%;
  border-radius: 12px;
  object-fit: contain;
}

.preview-placeholder {
  color: #6c757d;
  font-size: 1.2rem;
}

.processing-overlay {
  position: absolute;
  top: 1rem;
  right: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
