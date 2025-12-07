<template>
  <div class="landing-page">
    <!-- Hero Background with Overlay -->
    <div class="hero-background">
      <div class="hero-overlay"></div>
      <img src="../assets/pexels-specna-arms-306304-1927974.jpg" alt="Aerial Surveillance" class="hero-image">
    </div>

    <!-- Top Navigation Bar -->
    <nav class="top-nav">
      <div class="nav-logo">
        <span class="logo-icon">🛡️</span>
        <span class="logo-text">SKYGUARD INTELLIGENCE</span>
      </div>
      <div class="nav-links">
        <a href="#home" class="nav-link" :class="{ active: activeSection === 'home' }" @click.prevent="scrollToSection('home')">HOME</a>
        <a href="#detection" class="nav-link" @click.prevent="startDetection">DETECTION</a>
        <a href="#features" class="nav-link" :class="{ active: activeSection === 'features' }" @click.prevent="scrollToSection('features')">FEATURES</a>
        <a href="#about" class="nav-link" :class="{ active: activeSection === 'about' }" @click.prevent="scrollToSection('about')">ABOUT</a>
      </div>
    </nav>

    <!-- Main Content Container -->
    <div id="home" class="content-wrapper">
      <!-- Left Side: Hero Content -->
      <div class="hero-content">
        <h1 class="main-title">
          SKYGUARD<br>
          INTELLIGENCE
        </h1>
        
        <p class="hero-subtitle">
          Advanced AI-powered surveillance system for real-time threat identification.
          Protecting critical zones with precision and reliability.
        </p>

        <div class="hero-actions">
          <button class="btn-play" @click="startDetection">
            <span class="play-icon">▶</span>
          </button>
          <button class="btn-explore" @click="scrollToFeatures">
            EXPLORE MORE
            <span class="arrow-down">↓</span>
          </button>
        </div>
      </div>

      <!-- Right Side: Feature Cards -->
      <div class="feature-gallery">
        <div class="gallery-card card-1" @click="startDetection">
          <img src="../assets/forcard1.jpg" alt="Real-time Detection">
          <div class="card-overlay">
            <div class="card-category">REAL-TIME</div>
            <div class="card-title">DETECTION<br>SYSTEM</div>
            <div class="card-icon">▶</div>
          </div>
        </div>

        <div class="gallery-card card-2" @click="startDetection">
          <img src="../assets/forcard2.jpg" alt="AI Analysis">
          <div class="card-overlay">
            <div class="card-category">AI-POWERED</div>
            <div class="card-title">THREAT<br>ANALYSIS</div>
          </div>
        </div>

        <div class="gallery-card card-3" @click="startDetection">
          <img src="../assets/forcard3.jpg" alt="Military Grade">
          <div class="card-overlay">
            <div class="card-category">MILITARY-GRADE</div>
            <div class="card-title">SURVEILLANCE<br>TECHNOLOGY</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <section id="features" class="features-section">
      <div class="section-container">
        <h2 class="section-title">KEY FEATURES</h2>
        <p class="section-subtitle">Advanced capabilities for comprehensive threat detection and analysis</p>
        
        <div class="features-grid">
          <div class="feature-box">
            <div class="feature-icon-box">🎯</div>
            <h3>Real-Time Detection</h3>
            <p>Instant object classification with YOLO11s deep learning model, processing video streams and images in real-time for immediate threat identification.</p>
          </div>
          
          <div class="feature-box">
            <div class="feature-icon-box">🤖</div>
            <h3>AI-Powered Classification</h3>
            <p>Advanced neural networks trained to distinguish between civilian and soldier classifications with 99.5% accuracy for reliable threat assessment.</p>
          </div>
          
          <div class="feature-box">
            <div class="feature-icon-box">📹</div>
            <h3>Video & Image Support</h3>
            <p>Process both video streams and static images with configurable frame-skip settings for optimized performance and resource management.</p>
          </div>
          
          <div class="feature-box">
            <div class="feature-icon-box">📊</div>
            <h3>Live Preview & Analytics</h3>
            <p>Real-time visualization with bounding boxes, detection counts, and processing statistics displayed during analysis operations.</p>
          </div>
          
          <div class="feature-box">
            <div class="feature-icon-box">⚡</div>
            <h3>High-Speed Processing</h3>
            <p>Optimized inference pipeline with GPU acceleration support, delivering fast and efficient threat detection without compromising accuracy.</p>
          </div>
          
          <div class="feature-box">
            <div class="feature-icon-box">🔒</div>
            <h3>Secure & Reliable</h3>
            <p>Local processing ensures data privacy and security, with robust error handling and automatic server health monitoring.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- About Section -->
    <section id="about" class="about-section">
      <div class="section-container">
        <h2 class="section-title">ABOUT THE SYSTEM</h2>
        <p class="section-subtitle">Next-generation aerial surveillance technology</p>
        
        <div class="about-content">
          <div class="about-text">
            <h3>Mission-Critical Surveillance</h3>
            <p>SkyGuard Intelligence is a cutting-edge AI-powered platform designed for real-time identification and classification of potential threats in aerial surveillance operations. Leveraging state-of-the-art YOLO11s (You Only Look Once) deep learning architecture, our system provides military-grade accuracy and reliability for critical security applications.</p>
            
            <h3>Advanced Technology Stack</h3>
            <p>Built with a modern technology stack including Python backend for AI inference, Vue.js frontend for responsive user interface, and Electron for cross-platform desktop deployment. The system utilizes PyTorch and Ultralytics YOLO framework for optimal performance and accuracy.</p>
            
            <h3>Key Capabilities</h3>
            <ul class="capabilities-list">
              <li><strong>Dual Classification:</strong> Accurate identification of civilian and soldier personnel</li>
              <li><strong>Real-Time Processing:</strong> Instant analysis with minimal latency</li>
              <li><strong>Flexible Input:</strong> Support for video streams and static images</li>
              <li><strong>Visual Feedback:</strong> Color-coded bounding boxes (Green: Civilian, Red: Soldier)</li>
              <li><strong>Performance Monitoring:</strong> Live statistics and detection metrics</li>
              <li><strong>Export Functionality:</strong> Save processed results for documentation and analysis</li>
            </ul>
            
            <h3>Applications</h3>
            <p>Ideal for military operations, border security, critical infrastructure protection, event monitoring, and emergency response scenarios where rapid threat identification is essential for operational success and safety.</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeSection = ref('home')

const startDetection = () => {
  router.push('/detection')
}

const scrollToSection = (sectionId) => {
  const element = document.getElementById(sectionId)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const scrollToFeatures = () => {
  scrollToSection('features')
}

const updateActiveSection = () => {
  const sections = ['home', 'features', 'about']
  const scrollPosition = window.scrollY + 200 // Offset for navbar height
  
  for (const sectionId of sections) {
    const element = document.getElementById(sectionId)
    if (element) {
      const { offsetTop, offsetHeight } = element
      if (scrollPosition >= offsetTop && scrollPosition < offsetTop + offsetHeight) {
        activeSection.value = sectionId
        break
      }
    }
  }
}

onMounted(() => {
  window.addEventListener('scroll', updateActiveSection)
  updateActiveSection() // Initial check
})

onUnmounted(() => {
  window.removeEventListener('scroll', updateActiveSection)
})

const openDocumentation = () => {
  if (window.require) {
    const { shell } = window.require('electron')
    shell.openExternal('https://github.com/reymartjohneva/Aerial-Threat-Detection#readme')
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.landing-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background: #000;
  color: #fff;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Hero Background */
.hero-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.hero-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  filter: brightness(0.85);
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to right,
    rgba(0, 0, 0, 0.7) 0%,
    rgba(0, 0, 0, 0.45) 50%,
    rgba(0, 0, 0, 0.2) 100%
  );
  z-index: 1;
}

/* Top Navigation */
.top-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 60px;
  z-index: 100;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.7), transparent);
  backdrop-filter: blur(10px);
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 900;
  font-size: 1.1rem;
  letter-spacing: 2px;
}

.logo-icon {
  font-size: 1.8rem;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.logo-text {
  background: linear-gradient(135deg, #fff 0%, #a78bfa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-links {
  display: flex;
  gap: 40px;
}

.nav-link {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 1.5px;
  transition: all 0.3s ease;
  position: relative;
  cursor: pointer;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 0;
  height: 2px;
  background: #fff;
  transition: width 0.3s ease;
}

.nav-link:hover,
.nav-link.active {
  color: #fff;
}

.nav-link:hover::after,
.nav-link.active::after {
  width: 100%;
}

/* Main Content Wrapper */
.content-wrapper {
  position: relative;
  z-index: 10;
  min-height: 100vh;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 150px 60px 60px 60px;
  gap: 60px;
}

/* Hero Content (Left Side) */
.hero-content {
  flex: 1;
  max-width: 600px;
  animation: fadeInLeft 1s ease-out;
}

@keyframes fadeInLeft {
  from {
    opacity: 0;
    transform: translateX(-50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.main-title {
  font-size: 5.5rem;
  font-weight: 900;
  line-height: 1;
  letter-spacing: -3px;
  margin-bottom: 30px;
  text-shadow: 2px 2px 20px rgba(0, 0, 0, 0.8);
  background: linear-gradient(to bottom, #fff 0%, rgba(255, 255, 255, 0.8) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.1rem;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 40px;
  max-width: 500px;
  font-weight: 400;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 30px;
  margin-bottom: 0;
}

.btn-play {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.95);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 10px 40px rgba(255, 255, 255, 0.3);
  position: relative;
}

.btn-play::before {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}

.play-icon {
  font-size: 1.8rem;
  color: #000;
  margin-left: 5px;
  position: relative;
  z-index: 1;
}

.btn-play:hover {
  transform: scale(1.1);
  box-shadow: 0 15px 50px rgba(255, 255, 255, 0.5);
}

.btn-explore {
  background: transparent;
  border: 2px solid rgba(255, 255, 255, 0.5);
  color: #fff;
  padding: 15px 35px;
  border-radius: 30px;
  font-size: 0.9rem;
  font-weight: 700;
  letter-spacing: 1.5px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
  backdrop-filter: blur(10px);
}

.btn-explore:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: #fff;
  transform: translateY(-3px);
}

.arrow-down {
  font-size: 1.2rem;
  transition: transform 0.3s ease;
}

.btn-explore:hover .arrow-down {
  transform: translateY(5px);
}

/* Feature Gallery (Right Side) */
.feature-gallery {
  position: relative;
  display: flex;
  gap: 20px;
  animation: fadeInRight 1s ease-out;
  margin-top: 200px;
}

@keyframes fadeInRight {
  from {
    opacity: 0;
    transform: translateX(50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.gallery-card {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
}

.gallery-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.card-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 30px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.9) 0%, transparent 100%);
  transform: translateY(20px);
  opacity: 0;
  transition: all 0.4s ease;
}

.gallery-card:hover .card-overlay {
  transform: translateY(0);
  opacity: 1;
}

.gallery-card:hover img {
  transform: scale(1.1);
}

.gallery-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 60px rgba(167, 139, 250, 0.4);
  border-color: rgba(167, 139, 250, 0.5);
}

.card-1 {
  width: 280px;
  height: 380px;
  margin-top: 0;
}

.card-2 {
  width: 280px;
  height: 380px;
  margin-top: 0;
}

.card-3 {
  width: 280px;
  height: 380px;
  margin-top: 0;
}

.card-category {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 2px;
  color: #a78bfa;
  margin-bottom: 10px;
  text-transform: uppercase;
}

.card-title {
  font-size: 1.4rem;
  font-weight: 900;
  line-height: 1.2;
  letter-spacing: -1px;
}

.card-icon {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.gallery-card:hover .card-icon {
  opacity: 1;
}

/* Features Section */
.features-section {
  position: relative;
  z-index: 10;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.65) 0%, rgba(20, 20, 20, 0.7) 100%),
              url('../assets/pexels-eric-mufasa-578798-12640833.jpg');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  padding: 120px 60px;
  min-height: 100vh;
}

.section-container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  font-size: 3.5rem;
  font-weight: 900;
  text-align: center;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #fff 0%, #a78bfa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -2px;
}

.section-subtitle {
  text-align: center;
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 80px;
  font-weight: 400;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 40px;
}

.feature-box {
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.5) 0%, rgba(30, 30, 30, 0.6) 100%);
  padding: 50px 40px;
  border-radius: 20px;
  border: 1px solid rgba(167, 139, 250, 0.3);
  backdrop-filter: blur(15px);
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
}

.feature-box::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.1) 0%, transparent 100%);
  opacity: 0;
  transition: opacity 0.4s ease;
}

.feature-box:hover::before {
  opacity: 1;
}

.feature-box:hover {
  transform: translateY(-10px);
  border-color: rgba(167, 139, 250, 0.5);
  box-shadow: 0 20px 60px rgba(167, 139, 250, 0.3);
}

.feature-icon-box {
  font-size: 4rem;
  margin-bottom: 25px;
  filter: drop-shadow(0 0 20px rgba(167, 139, 250, 0.5));
}

.feature-box h3 {
  font-size: 1.6rem;
  font-weight: 700;
  margin-bottom: 15px;
  color: #fff;
}

.feature-box p {
  font-size: 1rem;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.7);
}

/* About Section */
.about-section {
  position: relative;
  z-index: 10;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.65) 0%, rgba(20, 20, 20, 0.7) 100%),
              url('../assets/pexels-george-pak-7985504.jpg');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  padding: 120px 60px;
  min-height: 100vh;
}

.about-content {
  max-width: 900px;
  margin: 0 auto;
}

.about-text {
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.5) 0%, rgba(30, 30, 30, 0.6) 100%);
  padding: 60px;
  border-radius: 20px;
  border: 1px solid rgba(167, 139, 250, 0.3);
  backdrop-filter: blur(15px);
}

.about-text h3 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 20px;
  margin-top: 40px;
  background: linear-gradient(135deg, #fff 0%, #a78bfa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.about-text h3:first-child {
  margin-top: 0;
}

.about-text p {
  font-size: 1.1rem;
  line-height: 1.9;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 30px;
}

.capabilities-list {
  list-style: none;
  padding: 0;
  margin: 30px 0;
}

.capabilities-list li {
  font-size: 1.1rem;
  line-height: 2;
  color: rgba(255, 255, 255, 0.8);
  padding-left: 30px;
  position: relative;
  margin-bottom: 15px;
}

.capabilities-list li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #a78bfa;
  font-weight: 900;
  font-size: 1.3rem;
}

.capabilities-list strong {
  color: #fff;
  font-weight: 700;
}

/* Responsive Design */
@media (max-width: 1400px) {
  .content-wrapper {
    padding: 100px 40px;
  }
  
  .main-title {
    font-size: 4.5rem;
  }
  
  .card-1 {
    width: 240px;
    height: 350px;
  }
  
  .card-2,
  .card-3 {
    width: 180px;
    height: 260px;
  }
  
  .features-section,
  .about-section {
    padding: 100px 40px;
  }
}

@media (max-width: 1024px) {
  .content-wrapper {
    flex-direction: column;
    padding: 120px 30px 80px;
    text-align: center;
  }
  
  .hero-content {
    max-width: 100%;
    align-items: center;
  }
  
  .main-title {
    font-size: 4rem;
  }
  
  .hero-actions {
    justify-content: center;
  }
  
  .feature-gallery {
    grid-template-columns: 1fr;
  }
  
  .features-section,
  .about-section {
    padding: 80px 30px;
  }
  
  .section-title {
    font-size: 3rem;
  }
  
  .feature-gallery {
    flex-direction: row;
    justify-content: center;
    margin-top: 60px;
  }
  
  .card-2,
  .card-3 {
    margin-top: 0;
  }
  
  .nav-links {
    display: none;
  }
}

@media (max-width: 768px) {
  .top-nav {
    padding: 15px 20px;
  }
  
  .content-wrapper {
    padding: 100px 20px 60px;
  }
  
  .main-title {
    font-size: 3rem;
    letter-spacing: -2px;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .btn-play {
    width: 60px;
    height: 60px;
  }
  
  .play-icon {
    font-size: 1.4rem;
  }
  
  .feature-gallery {
    flex-wrap: wrap;
    gap: 15px;
  }
  
  .gallery-card {
    width: 100% !important;
    height: 250px !important;
    margin-top: 0 !important;
  }
  
  .features-section,
  .about-section {
    padding: 60px 20px;
  }
  
  .section-title {
    font-size: 2.5rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
    gap: 30px;
  }
  
  .feature-box {
    padding: 40px 30px;
  }
  
  .about-text {
    padding: 40px 30px;
  }
  
  .about-text h3 {
    font-size: 1.6rem;
  }
  
  .about-text p {
    font-size: 1rem;
  }
  
  .capabilities-list li {
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .main-title {
    font-size: 2.5rem;
  }
  
  .hero-actions {
    flex-direction: column;
    gap: 20px;
  }
  
  .logo-text {
    font-size: 0.9rem;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .section-subtitle {
    font-size: 1rem;
  }
  
  .feature-icon-box {
    font-size: 3rem;
  }
  
  .feature-box h3 {
    font-size: 1.4rem;
  }
  
  .about-text h3 {
    font-size: 1.4rem;
  }
}
</style>
