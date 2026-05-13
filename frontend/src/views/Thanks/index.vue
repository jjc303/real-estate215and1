<template>
  <div class="acknowledgement-container">
    <ParticlesBg />
    
    <div class="content-wrapper">
      <div class="page-header">
        <h1 class="main-title">
          <span class="title-char" v-for="(char, idx) in titleChars" :key="idx" :style="{ '--delay': `${idx * 0.1}s` }">
            {{ char }}
          </span>
        </h1>
        <p class="sub-title">感恩所有相遇与陪伴</p>
      </div>
      
      <div class="card-grid">
        <div class="card fade-in" v-for="(item, idx) in cards" :key="idx" :style="{ animationDelay: `${0.5 + idx * 0.15}s` }">
          <div class="card-icon-wrapper">
            <span class="card-icon">{{ item.icon }}</span>
          </div>
          <h3 class="card-title">{{ item.title }}</h3>
          <p class="card-desc">{{ item.desc }}</p>
        </div>
      </div>
      
      <div class="quote-section">
        <div class="quote-mark left">"</div>
        <p class="quote-content">
          <span class="quote-char" v-for="(char, idx) in quoteChars" :key="idx" :style="{ '--delay': `${idx * 0.15}s` }">
            {{ char }}
          </span>
        </p>
        <div class="quote-mark right">"</div>
      </div>
      
      <div class="footer">
        <span class="footer-text">中南大学房地产租赁项目组 · 2026</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ParticlesBg from '@/components/ParticlesBg/index.vue'

const cards = [
  { icon: '🎓', title: '中南大学', desc: '感谢母校提供的优良学习环境与资源支持' },
  { icon: '👨‍🏫', title: '指导老师', desc: '感谢老师们在项目开发过程中的悉心指导与帮助' },
  { icon: '🤝', title: '团队伙伴', desc: '感谢每一位成员的日夜奋战与通力协作' },
  { icon: '💻', title: '开源社区', desc: '感谢所有优秀的开源技术与社区贡献者' }
]

const titleChars = '特别鸣谢'.split('')
const quoteChars = '以梦为马，不负韶华'.split('')

onMounted(() => {
  document.querySelectorAll('.fade-in').forEach((el, idx) => {
    setTimeout(() => el.classList.add('visible'), idx * 150)
  })
})
</script>

<style scoped>
.acknowledgement-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #fafafa 0%, #f0f5ff 100%);
  position: relative;
  overflow: hidden;
}

.content-wrapper {
  position: relative;
  z-index: 10;
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.bg-decoration {
  position: absolute;
  top: -200px;
  right: -100px;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(24, 144, 255, 0.06) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

.bg-decoration::before {
  content: '';
  position: absolute;
  bottom: -300px;
  left: -200px;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(19, 194, 194, 0.06) 0%, transparent 70%);
  border-radius: 50%;
}

.page-header {
  text-align: center;
  margin-bottom: 60px;
}

.main-title {
  font-size: 48px;
  font-weight: 700;
  margin: 0 0 12px 0;
  position: relative;
  display: inline-block;
}

.title-char {
  display: inline-block;
  opacity: 0;
  transform: translateY(20px);
  animation: charAppear 0.6s ease-out forwards;
  animation-delay: var(--delay, 0s);
  background: linear-gradient(90deg, #1890ff, #52c41a, #1890ff);
  background-size: 200% 100%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: charAppear 0.6s ease-out forwards, shine 3s linear infinite;
  animation-delay: var(--delay, 0s), calc(var(--delay, 0s) + 0.5s);
}

@keyframes charAppear {
  0% {
    opacity: 0;
    transform: translateY(20px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes shine {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.sub-title {
  font-size: 16px;
  color: #8c8c8c;
  margin: 0;
  letter-spacing: 4px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  width: 100%;
  margin-bottom: 50px;
}

.card {
  background: #fff;
  border-radius: 16px;
  padding: 24px 16px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.card.visible {
  opacity: 1;
  transform: translateY(0);
}

.card:hover {
  transform: translateY(-8px) scale(1.03);
  border-color: rgba(24, 144, 255, 0.5);
  box-shadow: 0 20px 40px rgba(24, 144, 255, 0.12);
  background: rgba(24, 144, 255, 0.05);
}

.card-icon-wrapper {
  width: 72px;
  height: 72px;
  margin: 0 auto 20px auto;
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-icon {
  font-size: 36px;
}

.card-title {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 10px 0;
}

.card-desc {
  font-size: 14px;
  color: #595959;
  line-height: 1.7;
  margin: 0;
}

.quote-section {
  text-align: center;
  padding: 50px 40px;
  background: #fff;
  border-radius: 12px;
  position: relative;
  margin-bottom: 60px;
  width: 100%;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.quote-mark {
  position: absolute;
  font-size: 100px;
  color: #e6f7ff;
  font-family: serif;
  line-height: 1;
}

.quote-mark.left {
  top: 10px;
  left: 20px;
}

.quote-mark.right {
  bottom: -20px;
  right: 40px;
}

.quote-content {
  font-size: 32px;
  font-weight: 500;
  margin: 0;
  letter-spacing: 2px;
  position: relative;
  display: inline-block;
}

.quote-char {
  display: inline-block;
  opacity: 0;
  transform: translateY(15px);
  animation: quoteCharAppear 0.5s ease-out forwards;
  animation-delay: var(--delay, 0s);
  background: linear-gradient(90deg, #1890ff, #52c41a, #1890ff);
  background-size: 200% 100%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: quoteCharAppear 0.5s ease-out forwards, quoteShine 3s linear infinite;
  animation-delay: var(--delay, 0s), calc(var(--delay, 0s) + 0.4s);
}

@keyframes quoteCharAppear {
  0% {
    opacity: 0;
    transform: translateY(15px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes quoteShine {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.footer {
  text-align: center;
  margin-top: auto;
}

.footer-text {
  font-size: 14px;
  color: #8c8c8c;
  letter-spacing: 3px;
}

@media (max-width: 768px) {
  .main-title {
    font-size: 32px;
  }
  
  .card-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .quote-content {
    font-size: 20px;
    letter-spacing: 4px;
  }
}
</style>
