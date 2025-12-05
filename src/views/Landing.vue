<template>
  <div class="landing-page">
    <div class="background-decoration decoration-1"></div>
    <div class="background-decoration decoration-2"></div>

    <div class="landing-container">
      <div class="landing-hero">
        <div class="hero-icon">🛡️</div>
        <h1 class="hero-title">
          <span class="title-gradient">Aerial Threat</span><br>
          Detection System
        </h1>
        <p class="hero-description">
          Advanced AI-powered object detection and classification for aerial surveillance.
          Identify threats in real-time with state-of-the-art YOLO technology.
        </p>

        <div class="hero-features">
          <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <h3>Real-Time Detection</h3>
            <p>Instant object classification and threat assessment using advanced machine learning algorithms</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h3>AI-Powered Analysis</h3>
            <p>Leveraging YOLO11s & YOLOv8s neural networks for accurate and reliable object detection</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Detailed Reports</h3>
            <p>Comprehensive analytics and visualizations of detection results and statistics</p>
          </div>
        </div>

        <div class="cta-section">
          <button class="btn-hero" @click="startDetection">
            <span class="btn-hero-text">
              Start Detection
              <span class="btn-arrow">→</span>
            </span>
          </button>
          
          <div class="secondary-cta">
            <a href="#" class="btn-secondary-link" @click.prevent="openDocumentation">
              📖 View Documentation
              <span>→</span>
            </a>
          </div>
        </div>

        <div class="stats-section">
          <div class="stat-item">
            <div class="stat-number">99.5%</div>
            <div class="stat-label">Accuracy</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">Real-time</div>
            <div class="stat-label">Processing</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">Multi-class</div>
            <div class="stat-label">Detection</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const startDetection = () => {
  router.push('/detection')
}

const openDocumentation = () => {
  if (window.require) {
    const { shell } = window.require('electron')
    shell.openExternal('https://github.com/reymartjohneva/Aerial-Threat-Detection#readme')
  }
}
</script>

<style scoped>
.landing-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%);
  color: #f1f5f9;
  position: relative;
  overflow: hidden;
}

.landing-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
  position: relative;
  overflow: hidden;
}

.landing-hero {
  text-align: center;
  max-width: 900px;
  margin: 0 auto;
  position: relative;
  z-index: 2;
}

.hero-icon {
  font-size: 8rem;
  margin-bottom: 30px;
  display: inline-block;
  animation: heroFloat 4s ease-in-out infinite;
  filter: drop-shadow(0 0 40px rgba(139, 92, 246, 0.6));
}

@keyframes heroFloat {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  25% { transform: translateY(-20px) rotate(-2deg); }
  75% { transform: translateY(-10px) rotate(2deg); }
}

.hero-title {
  font-size: 4.5rem;
  font-weight: 900;
  margin-bottom: 25px;
  line-height: 1.1;
  letter-spacing: -2px;
}

.title-gradient {
  background: linear-gradient(135deg, #a78bfa 0%, #ec4899 50%, #f59e0b 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: 1.5rem;
  color: #cbd5e1;
  margin-bottom: 50px;
  line-height: 1.6;
  font-weight: 500;
}

.hero-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
  margin: 60px 0;
}

.feature-card {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(17, 24, 39, 0.9) 100%);
  padding: 40px 30px;
  border-radius: 20px;
  border: 1px solid rgba(139, 92, 246, 0.3);
  backdrop-filter: blur(20px);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, transparent 100%);
  opacity: 0;
  transition: opacity 0.4s;
}

.feature-card:hover::before {
  opacity: 1;
}

.feature-card:hover {
  transform: translateY(-10px) scale(1.05);
  border-color: rgba(139, 92, 246, 0.6);
  box-shadow: 0 20px 60px rgba(139, 92, 246, 0.3);
}

.feature-icon {
  font-size: 3.5rem;
  margin-bottom: 20px;
  display: inline-block;
  filter: drop-shadow(0 0 15px rgba(139, 92, 246, 0.4));
}

.feature-card h3 {
  font-size: 1.4rem;
  color: #e4e8f0;
  margin-bottom: 15px;
  font-weight: 700;
}

.feature-card p {
  color: #94a3b8;
  font-size: 1rem;
  line-height: 1.6;
}

.cta-section {
  margin-top: 60px;
  text-align: center;
}

.btn-hero {
  padding: 24px 60px;
  font-size: 1.4rem;
  font-weight: 800;
  border: none;
  border-radius: 16px;
  cursor: pointer;
  background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 50%, #f59e0b 100%);
  background-size: 200% 200%;
  color: white;
  box-shadow: 0 10px 40px rgba(139, 92, 246, 0.5);
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
  animation: gradientMove 3s ease infinite;
}

@keyframes gradientMove {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.btn-hero::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.btn-hero:hover::before {
  width: 400px;
  height: 400px;
}

.btn-hero:hover {
  transform: translateY(-5px) scale(1.05);
  box-shadow: 0 20px 60px rgba(139, 92, 246, 0.7);
}

.btn-hero-text {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 15px;
  justify-content: center;
}

.btn-arrow {
  font-size: 1.6rem;
  transition: transform 0.3s;
}

.btn-hero:hover .btn-arrow {
  transform: translateX(10px);
}

.stats-section {
  display: flex;
  justify-content: center;
  gap: 60px;
  margin-top: 80px;
  flex-wrap: wrap;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 3.5rem;
  font-weight: 900;
  background: linear-gradient(135deg, #a78bfa 0%, #ec4899 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 1.1rem;
  color: #94a3b8;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.background-decoration {
  position: absolute;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.3;
  animation: decorationFloat 20s ease-in-out infinite;
}

.decoration-1 {
  top: -200px;
  left: -200px;
  background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
}

.decoration-2 {
  bottom: -200px;
  right: -200px;
  background: linear-gradient(135deg, #f59e0b 0%, #ec4899 100%);
  animation-delay: -10s;
}

@keyframes decorationFloat {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(50px, -50px) scale(1.1); }
  50% { transform: translate(-30px, 30px) scale(0.9); }
  75% { transform: translate(30px, 50px) scale(1.05); }
}

.secondary-cta {
  margin-top: 30px;
}

.btn-secondary-link {
  color: #a78bfa;
  font-size: 1.1rem;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-secondary-link:hover {
  color: #ec4899;
  gap: 12px;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 3rem;
  }

  .hero-description {
    font-size: 1.2rem;
  }

  .hero-icon {
    font-size: 5rem;
  }

  .btn-hero {
    padding: 18px 40px;
    font-size: 1.2rem;
  }

  .hero-features {
    grid-template-columns: 1fr;
  }

  .stats-section {
    gap: 40px;
  }
}
</style>
