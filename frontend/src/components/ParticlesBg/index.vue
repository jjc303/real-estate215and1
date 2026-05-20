<template>
  <canvas ref="particleCanvas" class="particle-canvas"></canvas>
</template>

<script setup>
import { ref, onMounted, onUnmounted, defineProps } from 'vue'

const props = defineProps({
  particleCount: {
    type: Number,
    default: 200
  },
  maxDist: {
    type: Number,
    default: 100
  },
  color: {
    type: String,
    default: '#1890ff'
  }
})

const particleCanvas = ref(null)
const ctx = ref(null)
let animationId = null
let particles = []
let dpr = 1

const hexToRgba = (hex, alpha) => {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

const initParticles = () => {
  const canvas = particleCanvas.value
  if (!canvas) return
  
  dpr = window.devicePixelRatio || 1
  const w = window.innerWidth
  const h = window.innerHeight
  
  canvas.width = w * dpr
  canvas.height = h * dpr
  canvas.style.width = w + 'px'
  canvas.style.height = h + 'px'
  
  ctx.value = canvas.getContext('2d')
  ctx.value.scale(dpr, dpr)
  
  particles = []
  for (let i = 0; i < props.particleCount; i++) {
    particles.push({
      x: Math.random() * w,
      y: Math.random() * h,
      radius: Math.random() * 1.5 + 0.8,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      alpha: Math.random() * 0.7 + 0.3
    })
  }
}

const animateParticles = () => {
  const canvas = particleCanvas.value
  if (!canvas || !ctx.value) return
  
  const w = window.innerWidth
  const h = window.innerHeight
  ctx.value.clearRect(0, 0, w, h)
  
  particles.forEach((p, i) => {
    p.x += p.vx
    p.y += p.vy
    
    if (p.x < 0) p.x = w
    if (p.x > w) p.x = 0
    if (p.y < 0) p.y = h
    if (p.y > h) p.y = 0
    
    ctx.value.beginPath()
    ctx.value.arc(p.x, p.y, p.radius, 0, Math.PI * 2)
    ctx.value.fillStyle = hexToRgba(props.color, p.alpha)
    ctx.value.fill()
    
    for (let j = i + 1; j < particles.length; j++) {
      const dx = p.x - particles[j].x
      const dy = p.y - particles[j].y
      const dist = Math.sqrt(dx * dx + dy * dy)
      
      if (dist < props.maxDist) {
        ctx.value.beginPath()
        ctx.value.strokeStyle = hexToRgba(props.color, 0.25 * (1 - dist / props.maxDist))
        ctx.value.lineWidth = 0.8
        ctx.value.moveTo(p.x, p.y)
        ctx.value.lineTo(particles[j].x, particles[j].y)
        ctx.value.stroke()
      }
    }
  })
  
  animationId = requestAnimationFrame(animateParticles)
}

const handleResize = () => {
  initParticles()
}

onMounted(() => {
  initParticles()
  animateParticles()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.particle-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}
</style>
