<template>
  <div class="my-houses">
    <div class="page-header">
      <h2>我的房源</h2>
      <el-button type="primary" class="publish-btn" @click="$router.push('/myhouses/publish')">
        <i class="fa-solid fa-plus"></i> 发布新房源
      </el-button>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-section">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fa-solid fa-house"></i>
        </div>
        <div class="stat-info">
          <div class="stat-number">{{ total }}</div>
          <div class="stat-label">全部房源</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="color: #52c41a">
          <i class="fa-solid fa-check-circle"></i>
        </div>
        <div class="stat-info">
          <div class="stat-number">{{ listedCount }}</div>
          <div class="stat-label">已上架</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="color: #fa8c16">
          <i class="fa-solid fa-edit"></i>
        </div>
        <div class="stat-info">
          <div class="stat-number">{{ draftCount }}</div>
          <div class="stat-label">草稿</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="color: #8c8c8c">
          <i class="fa-solid fa-archive"></i>
        </div>
        <div class="stat-info">
          <div class="stat-number">{{ offlineCount }}</div>
          <div class="stat-label">已下架</div>
        </div>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input 
        v-model="searchKeyword"
        placeholder="搜索房源标题、地址、小区..."
        clearable
        @keyup.enter="handleSearch"
      >
        <template #prefix>
          <i class="fa-solid fa-magnifying-glass"></i>
        </template>
      </el-input>
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <el-button v-if="searchKeyword" @click="clearSearch">清空</el-button>
    </div>

    <!-- 状态筛选 -->
    <div class="filter-section">
      <span 
        v-for="tab in tabs" 
        :key="tab.value"
        class="filter-tab"
        :class="{ active: currentTab === tab.value }"
        @click="currentTab = tab.value"
      >
        {{ tab.label }}
      </span>
    </div>

    <!-- 房源列表 -->
    <div class="house-list">
      <div v-if="loading" class="loading">加载中...</div>
      
      <div v-else-if="filteredHouses.length === 0" class="empty">
        {{ searchKeyword ? '未找到匹配的房源' : '暂无房源，去发布一个吧' }}
      </div>

      <div 
        v-for="house in filteredHouses" 
        :key="house.id"
        class="house-card"
      >
        <div class="house-left">
          <h3>{{ house.title }}</h3>
          <div class="house-tags">
            <span class="mini-tag">{{ house.house_type }}</span>
            <span v-if="house.area" class="mini-tag">{{ house.area }}㎡</span>
            <span v-if="house.decoration" class="mini-tag">{{ house.decoration }}</span>
          </div>
          <div class="house-info-line">
            <i class="fa-solid fa-location-dot" style="color: #8c8c8c;"></i>
            <span>{{ house.region }} · {{ house.address }}</span>
          </div>
          <div v-if="house.deposit" class="house-info-line">
            <i class="fa-solid fa-coins" style="color: #8c8c8c;"></i>
            <span>押金：¥{{ house.deposit }}</span>
          </div>
          <span class="status" :class="house.status">{{ statusText(house.status) }}</span>
        </div>
        
        <div class="house-right">
          <div class="house-price">
            <span class="price-num">¥{{ house.rent }}</span>
            <span class="price-unit">/月</span>
          </div>
          <div class="house-actions">
            <el-button 
              v-if="house.status === 'draft'"
              link
              style="color: #52c41a;"
              @click="publishHouse(house.id)"
            >
              <i class="fa-solid fa-arrow-up"></i> 上架
            </el-button>
            <el-button 
              v-if="house.status === 'listed'"
              link
              style="color: #262626;"
              @click="offlineHouse(house.id)"
            >
              <i class="fa-solid fa-arrow-down"></i> 下架
            </el-button>
            <el-button v-if="house.status !== 'offline'" link style="color: #1890ff;" @click="editHouse(house.id)">
              <i class="fa-solid fa-pen-to-square"></i> 编辑
            </el-button>
            <el-button link style="color: #ff4d4f;" @click="deleteHouse(house.id)">
              <i class="fa-solid fa-trash"></i> 删除
            </el-button>
          </div>
        </div>
      </div>

      <Pagination 
        v-if="total > 0 && !loading"
        :pageNum="pageNum"
        :pageSize="pageSize"
        :total="total"
        @change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import Pagination from '@/components/Pagination.vue'
import service from '@/utils/request'

const router = useRouter()
const loading = ref(false)
const currentTab = ref('all')
const searchKeyword = ref('')

const pageNum = ref(1)
const pageSize = ref(10)
const total = ref(0)
const houses = ref([])

const tabs = [
  { label: '全部', value: 'all' },
  { label: '已上架', value: 'listed' },
  { label: '草稿', value: 'draft' },
  { label: '已下架', value: 'offline' }
]

const listedCount = computed(() => houses.value.filter(h => h.status === 'listed').length)
const draftCount = computed(() => houses.value.filter(h => h.status === 'draft').length)
const offlineCount = computed(() => houses.value.filter(h => h.status === 'offline').length)

const imagePrompts = [
  'modern bright apartment living room with large window and city view',
  'cozy minimalist bedroom with wooden furniture',
  'modern kitchen with white cabinets and stainless steel appliances',
  'spacious balcony with green plants and sunset view',
  'elegant study room with bookshelf and desk',
  'luxury bathroom with marble finish and shower',
  'sunny apartment with large sofa and coffee table',
  'nordic style dining area with wooden table',
  'modern apartment hallway with clean white walls',
  'bright children room with colorful decor',
  'home office setup with window view',
  'minimalist living room with natural plants'
]

const getRandomHouseImage = () => {
  const randomPrompt = imagePrompts[Math.floor(Math.random() * imagePrompts.length)]
  return 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=' + encodeURIComponent(randomPrompt) + '&image_size=landscape_16_9'
}

const fetchHouseList = async () => {
  loading.value = true

  try {
    const params = {
      mine: true,
      page: pageNum.value,
      page_size: pageSize.value
    }
    
    if (searchKeyword.value.trim()) {
      params.keyword = searchKeyword.value.trim()
    }

    const res = await service.get('/v1/houses', { params })
    
    if (res.code === 0) {
      houses.value = res.data.list.map(house => ({
        ...house,
        randomImageUrl: getRandomHouseImage()
      }))
      total.value = res.data.total
    }
  } catch (e) {
    ElMessage.error('加载房源列表失败')
    console.error(e)
  } finally {
    loading.value = false
  }
}

const filteredHouses = computed(() => {
  let result = houses.value

  if (currentTab.value !== 'all') {
    result = result.filter(h => h.status === currentTab.value)
  }

  return result
})

const statusText = (status) => {
  const map = { draft: '草稿', listed: '已上架', offline: '已下架' }
  return map[status] || status
}

const handleSearch = () => {
  pageNum.value = 1
  fetchHouseList()
}

const clearSearch = () => {
  searchKeyword.value = ''
  pageNum.value = 1
  fetchHouseList()
}

const publishHouse = async (id) => {
  try {
    const res = await service.patch(`/v1/houses/${id}/publish`)
    if (res.code === 0) {
      ElMessage.success('上架成功！')
      fetchHouseList()
    }
  } catch (e) {
    ElMessage.error('上架失败')
    console.error(e)
  }
}

const offlineHouse = async (id) => {
  try {
    const res = await service.patch(`/v1/houses/${id}/offline`)
    if (res.code === 0) {
      ElMessage.success('已下架！')
      fetchHouseList()
    }
  } catch (e) {
    ElMessage.error('下架失败')
    console.error(e)
  }
}

const editHouse = (id) => {
  router.push(`/myhouses/edit/${id}`)
}

const deleteHouse = async (id) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除该房源吗？删除后无法恢复！',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const res = await service.delete(`/v1/houses/${id}`)
    if (res.code === 0) {
      ElMessage.success('删除成功！')
      fetchHouseList()
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(e)
    }
  }
}

const handlePageChange = (newPage) => {
  pageNum.value = newPage
  fetchHouseList()
}

watch(currentTab, () => {
  pageNum.value = 1
})

onMounted(() => {
  fetchHouseList()
})
</script>

<style scoped>
.my-houses {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background: #fff;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
}

.page-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #262626;
  margin: 0;
}

.publish-btn {
  height: 36px;
}

/* 统计卡片区域 */
.stats-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.stat-card {
  background: #fff;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

.stat-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #3072f6;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 22px;
  font-weight: 600;
  color: #262626;
  line-height: 1.2;
  margin-bottom: 2px;
}

.stat-label {
  font-size: 13px;
  color: #8c8c8c;
}

/* 搜索栏 */
.search-bar {
  margin-bottom: 20px;
  padding: 12px 16px;
  background: #fff;
  display: flex;
  gap: 10px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

.search-bar :deep(.el-input) {
  flex: 1;
}

/* 筛选区域 */
.filter-section {
  margin-bottom: 20px;
  display: flex;
  gap: 32px;
}

.filter-tab {
  font-size: 16px;
  color: #595959;
  cursor: pointer;
  padding: 4px 0;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.filter-tab.active {
  color: #1890ff;
  border-bottom-color: #1890ff;
}

.filter-tab:hover {
  color: #1890ff;
}

/* 房源列表 */
.house-list {
  display: flex;
  flex-direction: column;
}

.loading, .empty {
  text-align: center;
  padding: 60px;
  color: #8c8c8c;
}

/* 房源卡片 */
.house-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #fff;
  margin-bottom: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  border-radius: 6px;
  transition: none;
}

.house-card:hover {
  transform: none;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

.house-left {
  flex: 1;
  min-width: 0;
}

.house-left h3 {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 10px 0;
  text-decoration: none;
  border-bottom: none;
}

.house-tags {
  display: flex;
  gap: 6px;
  margin-bottom: 10px;
}

.mini-tag {
  display: inline-block;
  padding: 2px 8px;
  font-size: 12px;
  color: #8c8c8c;
  background: #f5f5f5;
  border-radius: 3px;
  margin-right: 0;
}

.house-info-line {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #595959;
  font-size: 14px;
  margin-top: 8px;
}

.house-info-line i {
  color: #8c8c8c;
  width: 16px;
  text-align: center;
  font-size: 14px;
}

.status {
  display: inline-block;
  padding: 3px 10px;
  font-size: 13px;
  margin-top: 10px;
  border-radius: 3px;
}

.status.draft { background: #fff7e6; color: #fa8c16; }
.status.listed { background: #f6ffed; color: #52c41a; }
.status.offline { background: #f5f5f5; color: #8c8c8c; }

.house-right {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 30px;
}

.house-price {
  text-align: right;
}

.price-num {
  font-size: 24px;
  font-weight: 600;
  color: #ff4d4f;
  line-height: 1;
}

.price-unit {
  font-size: 16px;
  color: #8c8c8c;
  margin-left: 2px;
}

.house-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.house-actions :deep(.el-button--link) {
  font-size: 14px;
  padding: 0;
  height: auto;
  line-height: 1;
  font-weight: 500;
}

@media (max-width: 992px) {
  .stats-section {
    grid-template-columns: repeat(2, 1fr);
  }

  .house-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .house-actions {
    margin-left: 0;
  }
}
</style>
