<template>
  <div class="detection-page">
    <div class="detection-grid">
      <!-- Left Sidebar: Upload and Options -->
      <div class="sidebar">
        <!-- Header -->
        <div class="header-section">
          <button class="btn-back" @click="goBack">← Back</button>
          <h1>🛡️ SkyGuard Detection</h1>
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
            <button 
              :class="['toggle-btn', { active: currentFileType === 'youtube' }]" 
              @click="switchFileType('youtube')"
            >
              🎬 YouTube
            </button>
          </div>
          
          <!-- YouTube URL Input -->
          <div v-if="currentFileType === 'youtube'" class="youtube-input-area">
            <div class="url-input-group">
              <input 
                v-model="youtubeUrl"
                type="text" 
                placeholder="Paste YouTube URL here..."
                class="youtube-url-input"
                :disabled="isProcessing"
                @keyup.enter="processYouTubeUrl"
              >
              <button 
                class="btn-process-url" 
                @click="processYouTubeUrl"
                :disabled="isProcessing || !youtubeUrl.trim()"
              >
                {{ isProcessing ? '⏳ Processing...' : '🎬 Analyze' }}
              </button>
            </div>
            <p class="upload-hint">{{ isProcessing ? '⏳ Processing YouTube video...' : '💡 Supports youtube.com and youtu.be links' }}</p>
          </div>
          
          <!-- File Upload Area -->
          <div 
            v-else
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
            <label>🤖 Model: YOLO11s</label>
            <p class="model-info">Optimized for real-time detection</p>
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
              <span>Total Detections:</span>
              <span>{{ totalDetections }}</span>
            </div>
            <div class="stat stat-soldier">
              <span>🎯 Soldiers:</span>
              <span>{{ soldierCount }}</span>
            </div>
            <div class="stat stat-civilian">
              <span>👤 Civilians:</span>
              <span>{{ civilianCount }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Live Preview -->
      <div class="preview-panel">
        <h2>🎬 Live Preview</h2>
        <div class="preview-container">
          <canvas v-if="currentFileType === 'video' || currentFileType === 'youtube'" ref="videoCanvas" class="preview-canvas"></canvas>
          <img v-else-if="detectedImageUrl" :src="detectedImageUrl" class="preview-image">
          <div v-else class="preview-placeholder">
            <p>No media loaded</p>
          </div>
          
          <!-- Small Status Badge (not covering video) -->
          <div v-if="isProcessing" class="status-badge">
            <div class="status-badge-content">
              <div class="small-spinner"></div>
              <span v-if="processingStatus === 'downloading'">📹 Downloading...</span>
              <span v-else-if="progress < 5">⚙️ Initializing...</span>
              <span v-else>🎬 Processing {{ progress }}%</span>
            </div>
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

// File upload
const currentFile = ref(null)
const currentFileType = ref('video')
const fileInput = ref(null)
const youtubeUrl = ref('')

// Processing
const isProcessing = ref(false)
const currentJobId = ref(null)
const progress = ref(0)
const framesProcessed = ref(0)
const processingStatus = ref('')

// Results
const totalDetections = ref(0)
const soldierCount = ref(0)
const civilianCount = ref(0)
const detectedImageUrl = ref(null)
const videoCanvas = ref(null)
let eventSource = null
let statusCheckInterval = null
let frameBuffer = []
let animationFrameId = null
let lastRenderTime = 0
let isRendering = false
let videoFPS = 30 // Default FPS, will be updated from stream
let frameInterval = 1000 / 30 // ms between frames

// Computed
const uploadText = computed(() => {
  if (currentFileType.value === 'youtube') {
    return 'Paste YouTube URL above'
  }
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
      return true
    }
  } catch (error) {
    serverOnline.value = false
    serverStatusText.value = 'Offline'
    return false
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
  
  // Clear animation frame
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
    animationFrameId = null
  }
  
  // Clear frame buffer
  frameBuffer = []
  isRendering = false
  lastRenderTime = 0
  
  // Reset state
  isProcessing.value = false
  currentJobId.value = null
  progress.value = 0
  framesProcessed.value = 0
  totalDetections.value = 0
  soldierCount.value = 0
  civilianCount.value = 0
  detectedImageUrl.value = null
  processingStatus.value = ''
}

const switchFileType = (type) => {
  cleanupPreviousProcessing()
  currentFileType.value = type
  currentFile.value = null
  youtubeUrl.value = ''
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

const processYouTubeUrl = async () => {
  if (!youtubeUrl.value.trim()) {
    alert('Please enter a YouTube URL')
    return
  }
  
  // Validate YouTube URL
  const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)[\w-]+/
  if (!youtubeRegex.test(youtubeUrl.value.trim())) {
    alert('Please enter a valid YouTube URL (youtube.com or youtu.be)')
    return
  }
  
  cleanupPreviousProcessing()
  isProcessing.value = true
  
  try {
    const serverHealthy = await checkServerHealth()
    if (!serverHealthy) {
      alert('Backend server is not running. Please start the server first.')
      isProcessing.value = false
      return
    }
    
    const response = await axios.post(`${API_BASE}/detect/youtube`, {
      url: youtubeUrl.value.trim()
    })
    
    const data = response.data
    
    if (data.success) {
      currentJobId.value = data.job_id
      
      nextTick(() => {
        if (videoCanvas.value) {
          const canvas = videoCanvas.value
          const ctx = canvas.getContext('2d')
          ctx.clearRect(0, 0, canvas.width, canvas.height)
        }
      })
      
      startProgressMonitoring()
      connectToStream(currentJobId.value)
    } else {
      throw new Error(data.error || 'Failed to process YouTube video')
    }
  } catch (error) {
    console.error('YouTube processing error:', error)
    alert(error.response?.data?.error || 'Failed to process YouTube video. Please check the URL and try again.')
    isProcessing.value = false
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
    const response = await axios.post(`${API_BASE}/upload`, formData, {
      timeout: 60000 // 60 second timeout
    })
    const data = response.data
    return data.success ? data.filename : null
  } catch (error) {
    console.error('Upload error:', error)
    alert('Failed to upload file. Please check your connection and try again.')
    return null
  }
}

const startProcessing = async () => {
  try {
    const serverHealthy = await checkServerHealth()
    if (!serverHealthy) {
      alert('Backend server is not running. Please start the server first.')
      return
    }
    
    const filename = await uploadFile()
    if (!filename) {
      isProcessing.value = false
      return
    }
    
    if (currentFileType.value === 'image') {
      await processImage(filename)
    } else {
      await processVideo(filename)
    }
  } catch (error) {
    console.error('Processing error:', error)
    alert('An error occurred during processing. Please try again.')
    isProcessing.value = false
  }
}

const processImage = async (filename) => {
  isProcessing.value = true
  
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
      progress.value = 100
      framesProcessed.value = 1
    }
  } catch (error) {
    console.error('Image processing error:', error)
    alert('Failed to process image. Please try again.')
  } finally {
    isProcessing.value = false
  }
}

const processVideo = async (filename) => {
  isProcessing.value = true
  
  try {
    const response = await axios.post(`${API_BASE}/detect/video`, {
      filename: filename,
      frame_skip: 1  // Process every frame for real-time playback
    })
    
    const data = response.data
    
    if (data.success) {
      currentJobId.value = data.job_id
      
      nextTick(() => {
        if (videoCanvas.value) {
          const canvas = videoCanvas.value
          const ctx = canvas.getContext('2d')
          // Clear canvas initially
          ctx.clearRect(0, 0, canvas.width, canvas.height)
        }
      })
      
      startProgressMonitoring()
      connectToStream(currentJobId.value)
    } else {
      throw new Error('Failed to start video processing')
    }
  } catch (error) {
    console.error('Video processing error:', error)
    alert('Failed to start video processing. Please try again.')
    isProcessing.value = false
  }
}

const renderNextFrame = () => {
  if (!videoCanvas.value || frameBuffer.length === 0) {
    isRendering = false
    return
  }
  
  const currentTime = performance.now()
  const timeSinceLastFrame = currentTime - lastRenderTime
  
  // Only render if enough time has passed based on video FPS
  if (timeSinceLastFrame < frameInterval && lastRenderTime > 0) {
    // Schedule next check
    animationFrameId = requestAnimationFrame(renderNextFrame)
    return
  }
  
  const canvas = videoCanvas.value
  const ctx = canvas.getContext('2d')
  const frameData = frameBuffer.shift()
  
  if (frameData) {
    const img = new Image()
    img.onload = () => {
      const container = canvas.parentElement
      const containerWidth = container.clientWidth
      const containerHeight = container.clientHeight
      
      // Calculate scaling to fit entire video while maintaining aspect ratio
      const videoAspectRatio = img.width / img.height
      const containerAspectRatio = containerWidth / containerHeight
      
      let canvasWidth, canvasHeight
      
      if (videoAspectRatio > containerAspectRatio) {
        canvasWidth = containerWidth
        canvasHeight = containerWidth / videoAspectRatio
      } else {
        canvasHeight = containerHeight
        canvasWidth = containerHeight * videoAspectRatio
      }
      
      canvas.width = img.width
      canvas.height = img.height
      canvas.style.width = `${canvasWidth}px`
      canvas.style.height = `${canvasHeight}px`
      
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
      
      lastRenderTime = performance.now()
      
      // Update detection stats
      if (frameData.detections) {
        let soldiers = 0, civilians = 0
        frameData.detections.forEach(det => {
          const className = det.class.toLowerCase()
          if (className === 'soldier') soldiers++
          else if (className === 'civilian') civilians++
        })
        
        soldierCount.value = soldiers
        civilianCount.value = civilians
        totalDetections.value = soldiers + civilians
      }
      
      // Schedule next frame rendering
      if (frameBuffer.length > 0) {
        // If buffer is getting too large, drop oldest frames
        if (frameBuffer.length > 10) {
          const framesToDrop = frameBuffer.length - 5
          frameBuffer.splice(0, framesToDrop)
          console.log(`Dropped ${framesToDrop} frames - buffer too large`)
        }
        animationFrameId = requestAnimationFrame(renderNextFrame)
      } else {
        isRendering = false
      }
    }
    img.onerror = () => {
      console.error('Failed to load frame image')
      isRendering = false
    }
    img.src = `data:image/jpeg;base64,${frameData.frame}`
  } else {
    isRendering = false
  }
}

const connectToStream = (jobId) => {
  if (eventSource) {
    eventSource.close()
  }
  
  // Reset frame buffer and rendering state
  frameBuffer = []
  isRendering = false
  lastRenderTime = 0
  
  eventSource = new EventSource(`${API_BASE}/stream/${jobId}`)
  
  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      
      if (data.type === 'frame') {
        // Update FPS if provided
        if (data.fps && data.fps > 0) {
          videoFPS = data.fps
          frameInterval = 1000 / videoFPS
        }
        
        // Add frame to buffer
        frameBuffer.push({
          frame: data.frame,
          detections: data.detections,
          timestamp: performance.now()
        })
        
        // Start rendering if not already rendering
        if (!isRendering && videoCanvas.value) {
          isRendering = true
          lastRenderTime = 0 // Reset timing for first frame
          animationFrameId = requestAnimationFrame(renderNextFrame)
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
      processingStatus.value = data.status || ''
      
      if (data.status === 'completed' || data.status === 'error') {
        clearInterval(statusCheckInterval)
        isProcessing.value = false
        
        if (data.status === 'error') {
          alert(`Processing error: ${data.error || 'Unknown error'}`)
        }
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
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
  frameBuffer = []
})
</script>

<style scoped>
.detection-page {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
  overflow: hidden;
  position: relative;
}

.detection-page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 20% 50%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 80% 50%, rgba(236, 72, 153, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.detection-grid {
  display: grid;
  grid-template-columns: 420px 1fr;
  height: 100vh;
  gap: 0;
  position: relative;
  z-index: 1;
}

/* Left Sidebar */
.sidebar {
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(167, 139, 250, 0.2);
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 2rem;
  height: 100vh;
  position: relative;
  -webkit-overflow-scrolling: touch;
}

.sidebar::-webkit-scrollbar {
  width: 8px;
}

.sidebar::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.5);
  border-radius: 4px;
}

.sidebar::-webkit-scrollbar-thumb {
  background: rgba(167, 139, 250, 0.3);
  border-radius: 4px;
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background: rgba(167, 139, 250, 0.5);
}

.header-section {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
  padding: 1.5rem;
  border-radius: 16px;
  border: 1px solid rgba(167, 139, 250, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.btn-back {
  background: rgba(167, 139, 250, 0.1);
  border: 1px solid rgba(167, 139, 250, 0.3);
  color: #a78bfa;
  cursor: pointer;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-weight: 600;
}

.btn-back:hover {
  background: rgba(167, 139, 250, 0.2);
  border-color: rgba(167, 139, 250, 0.5);
  transform: translateX(-3px);
}

h1 {
  margin: 0 0 1rem 0;
  font-size: 1.6rem;
  background: linear-gradient(135deg, #fff 0%, #a78bfa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 900;
  letter-spacing: -0.5px;
}

.server-status {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  background: rgba(15, 23, 42, 0.5);
  padding: 0.7rem 1rem;
  border-radius: 8px;
  border: 1px solid rgba(167, 139, 250, 0.1);
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  box-shadow: 0 0 10px currentColor;
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-dot.online {
  background: #10b981;
  box-shadow: 0 0 15px #10b981;
}

.status-dot.offline {
  background: #ef4444;
  box-shadow: 0 0 15px #ef4444;
}

/* Upload Card */
.upload-card, .options-card, .progress-card {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
  padding: 1.8rem;
  border-radius: 16px;
  border: 1px solid rgba(167, 139, 250, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(20px);
}

h2 {
  margin: 0 0 1.2rem 0;
  font-size: 1.2rem;
  color: #fff;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.file-type-toggle {
  display: flex;
  gap: 0.8rem;
  margin-bottom: 1.5rem;
}

.toggle-btn {
  flex: 1;
  padding: 1rem;
  border: 2px solid rgba(167, 139, 250, 0.2);
  background: rgba(30, 41, 59, 0.5);
  border-radius: 12px;
  cursor: pointer;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 600;
}

.toggle-btn:hover {
  border-color: rgba(167, 139, 250, 0.4);
  background: rgba(167, 139, 250, 0.1);
}

.toggle-btn.active {
  background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
  color: white;
  border-color: #a78bfa;
  box-shadow: 0 4px 20px rgba(167, 139, 250, 0.4);
}

.upload-area {
  border: 2px dashed rgba(167, 139, 250, 0.3);
  border-radius: 16px;
  padding: 2.5rem 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(15, 23, 42, 0.3);
}

.upload-area:hover:not(.processing) {
  border-color: rgba(167, 139, 250, 0.6);
  background: rgba(167, 139, 250, 0.05);
  transform: translateY(-2px);
}

.upload-area.processing {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
  user-select: none;
}

.upload-icon {
  font-size: 3.5rem;
  margin-bottom: 1rem;
  filter: drop-shadow(0 0 20px rgba(167, 139, 250, 0.5));
}

.upload-area p {
  margin: 0.7rem 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
}

.upload-hint {
  font-size: 0.9rem;
  color: #a78bfa;
  font-weight: 600;
}

.btn-upload {
  margin-top: 1.2rem;
  padding: 1rem 2.5rem;
  background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 700;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(139, 92, 246, 0.3);
}

.btn-upload:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 30px rgba(139, 92, 246, 0.5);
}

.btn-upload:disabled {
  background: rgba(107, 114, 128, 0.5);
  cursor: not-allowed;
  box-shadow: none;
}

/* YouTube Input Area */
.youtube-input-area {
  padding: 2rem;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.6) 0%, rgba(30, 30, 50, 0.6) 100%);
  border: 2px dashed rgba(167, 139, 250, 0.3);
  border-radius: 16px;
  text-align: center;
  transition: all 0.3s ease;
}

.url-input-group {
  display: flex;
  gap: 0.8rem;
  margin-bottom: 1rem;
}

.youtube-url-input {
  flex: 1;
  padding: 1rem 1.5rem;
  background: rgba(15, 23, 42, 0.8);
  border: 2px solid rgba(167, 139, 250, 0.3);
  border-radius: 12px;
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.youtube-url-input:focus {
  outline: none;
  border-color: #a78bfa;
  box-shadow: 0 0 20px rgba(167, 139, 250, 0.3);
}

.youtube-url-input::placeholder {
  color: rgba(167, 139, 250, 0.5);
}

.youtube-url-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-process-url {
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 700;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(255, 0, 0, 0.3);
  white-space: nowrap;
}

.btn-process-url:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 30px rgba(255, 0, 0, 0.5);
}

.btn-process-url:disabled {
  background: rgba(107, 114, 128, 0.5);
  cursor: not-allowed;
  box-shadow: none;
}

.file-info {
  margin-top: 1.2rem;
  padding: 1.2rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 12px;
  font-size: 0.9rem;
  border: 1px solid rgba(167, 139, 250, 0.1);
}

.file-info p {
  margin: 0.4rem 0;
  color: rgba(255, 255, 255, 0.9);
}

.file-info strong {
  color: #a78bfa;
}

/* Options Card */
.option-group {
  margin-bottom: 1.2rem;
}

.option-group label {
  display: block;
  margin-bottom: 0.7rem;
  color: #fff;
  font-weight: 600;
  font-size: 0.95rem;
}

.model-info {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 0.5rem;
  font-style: italic;
}

.option-group select {
  width: 100%;
  padding: 1rem;
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 12px;
  font-size: 0.95rem;
  background: rgba(15, 23, 42, 0.5);
  color: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
}

.option-group select:hover {
  border-color: rgba(167, 139, 250, 0.5);
}

.option-group select:focus {
  outline: none;
  border-color: #a78bfa;
  box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.1);
}

.btn-cancel {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 700;
  margin-top: 1.2rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(239, 68, 68, 0.3);
}

.btn-cancel:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 30px rgba(239, 68, 68, 0.5);
}

/* Progress Card */
.progress-bar-container {
  position: relative;
  height: 40px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 1.5rem;
  border: 1px solid rgba(167, 139, 250, 0.2);
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #8b5cf6, #a78bfa, #ec4899);
  background-size: 200% 100%;
  animation: gradient-shift 2s ease infinite;
  transition: width 0.3s ease;
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.5);
}

@keyframes gradient-shift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #fff;
  font-weight: 700;
  font-size: 1rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.stats {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.stat {
  display: flex;
  justify-content: space-between;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 10px;
  font-size: 0.95rem;
  border: 1px solid rgba(167, 139, 250, 0.1);
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.stat span:last-child {
  color: #a78bfa;
  font-weight: 700;
}

/* Soldier and Civilian specific styles */
.stat-soldier {
  border: 1px solid rgba(239, 68, 68, 0.3);
  background: rgba(239, 68, 68, 0.1);
}

.stat-soldier span:last-child {
  color: #ef4444;
  font-weight: 700;
  font-size: 1.1rem;
}

.stat-civilian {
  border: 1px solid rgba(16, 185, 129, 0.3);
  background: rgba(16, 185, 129, 0.1);
}

.stat-civilian span:last-child {
  color: #10b981;
  font-weight: 700;
  font-size: 1.1rem;
}

/* Right Preview Panel */
.preview-panel {
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  padding: 2rem;
}

.preview-panel h2 {
  color: white;
  margin: 0 0 1.5rem 0;
  font-size: 1.6rem;
  font-weight: 900;
  background: linear-gradient(135deg, #fff 0%, #a78bfa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

.preview-container {
  flex: 1;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.5) 0%, rgba(0, 0, 0, 0.8) 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(167, 139, 250, 0.2);
  box-shadow: inset 0 2px 20px rgba(0, 0, 0, 0.5);
}

.preview-canvas, .preview-image {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  border-radius: 12px;
  object-fit: contain;
  display: block;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
}

.preview-placeholder {
  color: rgba(255, 255, 255, 0.3);
  font-size: 1.4rem;
  font-weight: 600;
  text-align: center;
}

/* Small Status Badge (non-blocking) */
.status-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(15, 23, 42, 0.95);
  padding: 0.75rem 1.25rem;
  border-radius: 12px;
  border: 1px solid rgba(167, 139, 250, 0.4);
  backdrop-filter: blur(10px);
  z-index: 5;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.status-badge-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #fff;
  font-size: 0.9rem;
  font-weight: 600;
}

.small-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(167, 139, 250, 0.3);
  border-top-color: #a78bfa;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(167, 139, 250, 0.2);
  border-top-color: #a78bfa;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Responsive Design */
@media (max-width: 1024px) {
  .detection-grid {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }
  
  .sidebar {
    height: auto;
    max-height: 50vh;
    border-right: none;
    border-bottom: 1px solid rgba(167, 139, 250, 0.2);
  }
  
  .preview-panel {
    height: 50vh;
  }
}

@media (max-width: 768px) {
  .sidebar {
    padding: 1.5rem;
    gap: 1rem;
  }
  
  .header-section,
  .upload-card,
  .options-card,
  .progress-card {
    padding: 1.2rem;
  }
  
  h1 {
    font-size: 1.3rem;
  }
  
  h2 {
    font-size: 1rem;
  }
  
  .preview-panel {
    padding: 1.5rem;
  }
  
  .preview-panel h2 {
    font-size: 1.3rem;
  }
}
</style>

