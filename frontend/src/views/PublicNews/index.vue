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

      <div class="news-list-wrapper" v-if="newsList.length > 0">
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
      <div v-else class="empty-state">
        <i class="fa-solid fa-newspaper"></i>
        <p>暂无新闻公告</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import ParticlesBg from '@/components/ParticlesBg/index.vue'
import { listNews } from '@/api/news.js'

const newsList = ref([])
const titleChars = '新闻通知'.split('')

const loadNews = async () => {
  try {
    const res = await listNews({ page: 1, page_size: 50 })
    console.log('新闻接口返回:', res)
    if (res && res.code === 0) {
      const list = res.data?.list || res.data?.items || []
      console.log('实际列表数据:', list)
      newsList.value = list.map(item => ({
        id: item.id,
        title: item.title || '无标题',
        summary: (item.content && item.content.length > 150) ? item.content.substring(0, 150) + '...' : (item.content || '暂无内容'),
        category: '平台公告',
        date: item.created_at ? item.created_at.substring(0, 10) : '',
        author: '平台运营',
        isTop: item.is_top === true || item.status === 'published'
      }))
      console.log('处理后newsList:', newsList.value)
    } else {
      console.log('接口返回错误:', res)
    }
  } catch (e) {
    console.error('加载新闻列表失败', e)
  }
}

onMounted(() => {
  loadNews().then(() => {
    nextTick(() => {
      document.querySelectorAll('.fade-in').forEach((el, idx) => {
        setTimeout(() => el.classList.add('visible'), idx * 120)
      })
    })
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

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #8c8c8c;
}

.empty-state i {
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-state p {
  font-size: 16px;
  margin: 0;
}
</style>
