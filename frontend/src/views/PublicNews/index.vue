<template>
  <div class="public-news-page">
    <ParticlesBg />
    <div class="page-inner">
      <div class="page-header">
        <h1 class="main-title">
          <span class="news-title-char" v-for="(char, idx) in titleChars" :key="idx" :style="{ '--delay': `${idx * 0.15}s` }">
            {{ char }}
          </span>
        </h1>
        <p class="subtitle">浏览最新平台公告和新闻资讯</p>
      </div>

      <div class="news-list-wrapper">
        <div class="news-card fade-in" v-for="(item, idx) in newsList" :key="item.id" :style="{ animationDelay: `${0.6 + idx * 0.12}s` }">
          <div class="news-badge" v-if="item.isTop">置顶</div>
          <div class="news-card-body">
            <div class="news-meta">
              <span class="news-category">{{ item.category }}</span>
              <span class="news-date">{{ item.date }}</span>
            </div>
            <h3 class="news-title">{{ item.title }}</h3>
            <p class="news-desc">{{ item.summary }}</p>
          </div>
          <div class="news-card-footer">
            <div class="news-author">
              <i class="fa-solid fa-user-circle"></i> {{ item.author }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ParticlesBg from '@/components/ParticlesBg/index.vue'

const newsList = ref([
  {
    id: 1,
    title: '2026年第二季度租房补贴政策正式上线',
    summary: '为进一步支持新市民安居，本市第二季度租房补贴申请通道已正式开放，符合条件的租客可通过平台直接在线申报。',
    category: '政策通知',
    date: '2026-05-08',
    author: '平台运营',
    isTop: true
  },
  {
    id: 2,
    title: '中南找房系统全面升级，全新功能上线',
    summary: '本次升级新增智能推荐、VR看房、电子合同自动签署等多项重磅功能，大幅提升您的租房体验。',
    category: '平台公告',
    date: '2026-05-05',
    author: '技术部',
    isTop: true
  },
  {
    id: 3,
    title: '夏季租房高峰来临，教您如何快速选到好房',
    summary: '毕业季即将到来，为帮助租客高效筛选高性价比房源，我们整理了夏季租房避坑指南和看房注意事项。',
    category: '租房指南',
    date: '2026-05-02',
    author: '运营团队',
    isTop: false
  },
  {
    id: 4,
    title: '五一限时活动圆满结束，中奖名单公布',
    summary: '为期7天的五一租房优惠券活动已顺利落幕，现将幸运中奖用户名单公示，奖品将在3个工作日内陆续发放。',
    category: '活动资讯',
    date: '2026-05-01',
    author: '市场部',
    isTop: false
  }
])

const titleChars = '新闻通知'.split('')

onMounted(() => {
  document.querySelectorAll('.fade-in').forEach((el, idx) => {
    setTimeout(() => el.classList.add('visible'), parseFloat(el.style.animationDelay) * 1000 + 200)
  })
})
</script>

<style scoped>
.public-news-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #fafafa 0%, #f0f5ff 100%);
  padding: 40px 20px;
  position: relative;
  overflow: hidden;
}

.page-inner {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 10;
}

.page-header {
  margin: 0 0 48px;
  text-align: center;
}

.main-title {
  font-size: 42px;
  font-weight: 700;
  margin: 0 0 12px;
  position: relative;
  display: inline-block;
}

.news-title-char {
  display: inline-block;
  opacity: 0;
  transform: translateY(20px);
  animation: newsTitleAppear 0.6s ease-out forwards;
  animation-delay: var(--delay, 0s);
  background: linear-gradient(90deg, #1890ff, #52c41a, #1890ff);
  background-size: 200% 100%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: newsTitleAppear 0.6s ease-out forwards, newsShine 3s linear infinite;
  animation-delay: var(--delay, 0s), calc(var(--delay, 0s) + 0.4s);
}

@keyframes newsTitleAppear {
  0% {
    opacity: 0;
    transform: translateY(20px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes newsShine {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.fade-in {
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.5s ease-out;
}

.fade-in.visible {
  opacity: 1;
  transform: translateY(0);
}

.subtitle {
  font-size: 16px;
  color: #8c8c8c;
  margin: 0;
  letter-spacing: 3px;
}

.news-list-wrapper {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 24px;
}

.news-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  position: relative;
  border: 1px solid #f0f0f0;
  transition: transform 0.25s, box-shadow 0.25s;
}

.news-card:hover {
  transform: translateY(-6px);
  border-color: rgba(24, 144, 255, 0.5);
  box-shadow: 0 12px 32px rgba(24, 144, 255, 0.12);
}

.news-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  background: linear-gradient(135deg, #f44336 0%, #ef5350 100%);
  color: white;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 12px;
}

.news-card-body {
  padding: 24px;
}

.news-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 14px;
}

.news-category {
  background: #e6f7ff;
  color: #1890ff;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 8px;
}

.news-date {
  font-size: 13px;
  color: #999;
  display: flex;
  align-items: center;
}

.news-title {
  font-size: 20px;
  font-weight: 700;
  color: #262626;
  margin: 0 0 10px;
  line-height: 1.4;
}

.news-desc {
  font-size: 14px;
  color: #595959;
  line-height: 1.7;
  margin: 0;
}

.news-card-footer {
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-start;
  align-items: center;
}

.news-author {
  font-size: 13px;
  color: #8c8c8c;
  display: flex;
  align-items: center;
  gap: 6px;
}
</style>
