<template>
  <div class="message-news-page">
    <div class="page-header">
      <h1>{{ userStore.userRole === 'admin' ? '新闻管理' : '新闻查看' }}</h1>
      <p class="subtitle">
        {{ userStore.userRole === 'admin' ? '发布和管理平台新闻公告' : '浏览最新平台公告和新闻资讯' }}
      </p>
      <el-button v-if="userStore.userRole === 'admin'" type="primary" class="create-btn" @click="openCreateDialog">
        <i class="fa-solid fa-plus"></i> 发布新闻
      </el-button>
    </div>

    <div class="news-container">
      <div class="news-list-wrapper">
        <div class="news-card" v-for="item in paginatedNewsList" :key="item.id">
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
            <div class="news-actions" v-if="userStore.userRole === 'admin'">
              <el-button type="primary" link size="small" @click="openEditDialog(item)">编辑</el-button>
              <el-button type="danger" link size="small" @click="deleteNews(item.id)">删除</el-button>
            </div>
          </div>
        </div>
      </div>
      
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="4"
          :total="newsList.length"
          layout="total, prev, pager, next"
          background
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '发布新闻' : '编辑新闻'"
      width="720px"
      :close-on-click-modal="false"
    >
      <el-form :model="newsForm" label-width="100px" label-position="top">
        <el-form-item label="新闻标题">
          <el-input v-model="newsForm.title" placeholder="请输入新闻标题" />
        </el-form-item>
        <el-form-item label="新闻分类">
          <el-select v-model="newsForm.category" placeholder="请选择分类">
            <el-option label="平台公告" value="平台公告" />
            <el-option label="政策通知" value="政策通知" />
            <el-option label="活动资讯" value="活动资讯" />
            <el-option label="租房指南" value="租房指南" />
          </el-select>
        </el-form-item>
        <el-form-item label="新闻内容">
          <el-input v-model="newsForm.content" type="textarea" :rows="8" placeholder="请输入新闻详细内容" />
        </el-form-item>
        <el-form-item label="置顶推荐">
          <el-switch v-model="newsForm.isTop" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveNews">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '@/stores/user.js'
import { ElMessage, ElMessageBox } from 'element-plus'

const userStore = useUserStore()
const dialogVisible = ref(false)
const dialogMode = ref('create')
const editNewsId = ref(null)
const currentPage = ref(1)
const pageSize = ref(4)

const newsForm = ref({
  title: '',
  category: '',
  content: '',
  isTop: false
})

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

const paginatedNewsList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return newsList.value.slice(start, end)
})

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

const openCreateDialog = () => {
  dialogMode.value = 'create'
  editNewsId.value = null
  newsForm.value = {
    title: '',
    category: '',
    content: '',
    isTop: false
  }
  dialogVisible.value = true
}

const openEditDialog = (item) => {
  dialogMode.value = 'edit'
  editNewsId.value = item.id
  newsForm.value = {
    title: item.title,
    category: item.category,
    content: item.summary,
    isTop: item.isTop
  }
  dialogVisible.value = true
}

const saveNews = () => {
  if (userStore.userRole !== 'admin') {
    ElMessage.error('只有管理员可以发布和编辑新闻')
    return
  }
  
  if (!newsForm.value.title.trim()) {
    ElMessage.warning('请输入新闻标题')
    return
  }
  if (!newsForm.value.category) {
    ElMessage.warning('请选择新闻分类')
    return
  }
  if (!newsForm.value.content.trim()) {
    ElMessage.warning('请输入新闻内容')
    return
  }

  if (dialogMode.value === 'create') {
    const now = new Date()
    const newId = newsList.value.length + 1
    newsList.value.unshift({
      id: newId,
      title: newsForm.value.title,
      category: newsForm.value.category,
      summary: newsForm.value.content,
      date: `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`,
      author: '管理员',
      isTop: newsForm.value.isTop
    })
    ElMessage.success('新闻发布成功')
  } else {
    const idx = newsList.value.findIndex(n => n.id === editNewsId.value)
    if (idx !== -1) {
      newsList.value[idx].title = newsForm.value.title
      newsList.value[idx].category = newsForm.value.category
      newsList.value[idx].summary = newsForm.value.content
      newsList.value[idx].isTop = newsForm.value.isTop
    }
    ElMessage.success('新闻更新成功')
  }
  dialogVisible.value = false
}

const deleteNews = (id) => {
  if (userStore.userRole !== 'admin') {
    ElMessage.error('只有管理员可以删除新闻')
    return
  }
  
  ElMessageBox.confirm('确定要删除这条新闻吗？此操作不可恢复。', '提示', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    newsList.value = newsList.value.filter(n => n.id !== id)
    ElMessage.success('新闻已删除')
  }).catch(() => {})
}

onMounted(() => {
})
</script>

<style scoped>
.message-news-page {
  width: 100%;
  height: calc(100vh - 130px);
  display: flex;
  flex-direction: column;
}

.page-header {
  margin: 0 0 16px;
  padding: 0;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 16px;
  flex-shrink: 0;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 6px;
}

.subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
  text-align: right;
}

.create-btn {
  border-radius: 24px;
  padding-left: 24px;
  padding-right: 24px;
  height: 40px;
}

.news-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(25, 118, 210, 0.08);
}

.news-list-wrapper {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
  align-content: start;
}

.news-list-wrapper::-webkit-scrollbar {
  width: 6px;
}

.news-list-wrapper::-webkit-scrollbar-thumb {
  background: #e0e0e0;
  border-radius: 3px;
}

.pagination-wrapper {
  flex-shrink: 0;
  padding: 16px 24px;
  border-top: 1px solid #f0f2f5;
  display: flex;
  justify-content: center;
  background: white;
}

.news-card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(25, 118, 210, 0.08);
  overflow: hidden;
  position: relative;
  transition: transform 0.25s, box-shadow 0.25s;
}

.news-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(25, 118, 210, 0.14);
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
  background: #e3f2fd;
  color: #1976d2;
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
  color: #1a1a2e;
  margin: 0 0 10px;
  line-height: 1.4;
}

.news-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.7;
  margin: 0;
}

.news-card-footer {
  padding: 16px 24px;
  border-top: 1px solid #f5f7fa;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.news-author {
  font-size: 13px;
  color: #888;
  display: flex;
  align-items: center;
  gap: 6px;
}

.news-actions {
  display: flex;
  gap: 8px;
}
</style>
