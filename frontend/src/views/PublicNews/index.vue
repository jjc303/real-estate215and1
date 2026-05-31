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
        <div class="news-card fade-in" v-for="(item, idx) in newsList" :key="item.id" :style="{ animationDelay: `${0.6 + idx * 0.12}s` }" @click="openDetail(item)">
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

    <el-dialog v-model="showDetail" width="680px" top="6vh" :close-on-click-modal="true" destroy-on-close>
      <div v-if="detailItem" class="news-detail-content">
        <button class="detail-close" @click="showDetail = false">
          <i class="fa-solid fa-xmark"></i>
        </button>
        <div class="detail-banner">
          <div class="detail-meta">
            <span class="detail-category">{{ detailItem.category }}</span>
            <span class="detail-date">
              <i class="fa-regular fa-calendar"></i> {{ detailItem.date }}
            </span>
          </div>
          <h2 class="detail-title">{{ detailItem.title }}</h2>
          <div class="detail-author">
            <span class="author-avatar"><i class="fa-solid fa-user-circle"></i></span>
            <span class="author-name">{{ detailItem.author }}</span>
          </div>
        </div>
        <div class="detail-body">
          <div class="detail-divider"></div>
          <p class="detail-text">{{ detailItem.content }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import ParticlesBg from '@/components/ParticlesBg/index.vue'
import { listNews } from '@/api/news.js'

const newsList = ref([])
const titleChars = '新闻通知'.split('')
const showDetail = ref(false)
const detailItem = ref(null)

const openDetail = (item) => {
  detailItem.value = item
  showDetail.value = true
}

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
        content: item.content || '暂无内容',
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
  display: flex;
  flex-direction: column;
  height: 290px;
  cursor: pointer;
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
  z-index: 1;
}

.news-card-body {
  padding: 24px;
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.news-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 14px;
  flex-shrink: 0;
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
  font-size: 17px;
  font-weight: 700;
  color: #262626;
  margin: 0 0 10px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  flex-shrink: 0;
}

.news-desc {
  font-size: 14px;
  color: #595959;
  line-height: 1.7;
  margin: 0;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 4;
  overflow: hidden;
  flex: 1;
}

.news-card-footer {
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  flex-shrink: 0;
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

.news-detail-content {
  position: relative;
  padding: 0;
}

.detail-close {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.04);
  color: #8c8c8c;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  z-index: 10;
}

.detail-close:hover {
  background: rgba(0, 0, 0, 0.08);
  color: #262626;
  transform: rotate(90deg);
}

.detail-banner {
  padding: 20px 24px 16px;
  background: linear-gradient(135deg, #fafafe 0%, #f0f5ff 100%);
  border-radius: 12px 12px 0 0;
}

.detail-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 10px;
  align-items: center;
}

.detail-category {
  background: linear-gradient(135deg, #1890ff, #096dd9);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 6px;
  letter-spacing: 0.5px;
}

.detail-date {
  font-size: 13px;
  color: #8c8c8c;
  display: flex;
  align-items: center;
  gap: 4px;
}

.detail-title {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 8px;
  line-height: 1.4;
  letter-spacing: 0.3px;
}

.detail-author {
  display: flex;
  align-items: center;
  gap: 6px;
}

.author-avatar {
  font-size: 16px;
  color: #bfbfbf;
}

.author-name {
  font-size: 13px;
  color: #595959;
  font-weight: 500;
}

.detail-body {
  padding: 16px 24px 24px;
  max-height: 55vh;
  overflow-y: auto;
}

.detail-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, #e8e8e8 20%, #e8e8e8 80%, transparent);
  margin-bottom: 16px;
}

.detail-text {
  font-size: 14px;
  color: #434343;
  line-height: 1.8;
  margin: 0;
  white-space: pre-wrap;
}

:deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

:deep(.el-dialog__header) {
  display: none;
}

:deep(.el-dialog__body) {
  padding: 0;
}

:deep(.el-overlay) {
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(4px);
}
</style>
