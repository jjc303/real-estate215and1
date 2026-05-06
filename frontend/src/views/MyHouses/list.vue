<template>
  <div class="my-houses">
    <div class="page-header">
      <h2>我的房源列表</h2>
      <router-link to="/myhouses/publish" class="btn-primary">
        + 发布新房源
      </router-link>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <input 
        v-model="searchKeyword"
        type="text" 
        placeholder="搜索房源标题、地址、小区..."
        @keyup.enter="handleSearch"
      />
      <button @click="handleSearch">搜索</button>
      <button v-if="searchKeyword" class="clear" @click="clearSearch">清空</button>
    </div>

    <!-- 状态筛选 -->
    <div class="filter-tabs">
      <span 
        v-for="tab in tabs" 
        :key="tab.value"
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
        <div class="house-info">
          <h3>{{ house.title }}</h3>
          <p>{{ house.address }} · {{ house.house_type }} · {{ house.area }}㎡</p>
          <p class="price">¥{{ house.rent }}/月</p>
          <span class="status" :class="house.status">{{ statusText(house.status) }}</span>
        </div>

        <div class="house-actions">
          <button 
            v-if="house.status === 'draft'"
            @click="publishHouse(house.id)"
          >
            上架
          </button>
          <button 
            v-if="house.status === 'listed'"
            @click="offlineHouse(house.id)"
          >
            下架
          </button>
          <button @click="editHouse(house.id)">编辑</button>
          <button @click="deleteHouse(house.id)" class="danger">删除</button>
        </div>
      </div>
      <Pagination 
        v-if="total > 0"
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
// import { mockMyHouses } from '@/mock/myhouseList'

// 调试开关：true=用mock，false=用真实接口
const USE_MOCK = false

const router = useRouter()
const loading = ref(false)
const currentTab = ref('all')
const searchKeyword = ref('')

// 分页数据
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

// 加载我的房源列表
const fetchHouseList = async () => {
  loading.value = true
  
  if (USE_MOCK) {
    // 用本地 mock 数据
    setTimeout(() => {
      // houses.value = mockMyHouses
      // total.value = mockMyHouses.length
      loading.value = false
    }, 500)
    return
  }

  try {
    const params = {
      mine: true,
      page: pageNum.value,
      page_size: pageSize.value
    }
    
    // 关键字搜索
    if (searchKeyword.value.trim()) {
      params.keyword = searchKeyword.value.trim()
    }

    const res = await service.get('/v1/houses', { params })
    
    if (res.code === 0) {
      houses.value = res.data.list
      total.value = res.data.total
    }
  } catch (e) {
    ElMessage.error('加载房源列表失败')
    console.error(e)
  } finally {
    loading.value = false
  }
}

// 筛选后的列表（前端状态筛选）
const filteredHouses = computed(() => {
  let result = houses.value

  // 状态筛选
  if (currentTab.value !== 'all') {
    result = result.filter(h => h.status === currentTab.value)
  }

  return result
})

const statusText = (status) => {
  const map = { draft: '草稿', listed: '已上架', offline: '已下架' }
  return map[status] || status
}

// 搜索
const handleSearch = () => {
  pageNum.value = 1
  fetchHouseList()
}

// 清空搜索
const clearSearch = () => {
  searchKeyword.value = ''
  pageNum.value = 1
  fetchHouseList()
}

// 上架
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

// 下架
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

// 编辑
const editHouse = (id) => {
  // 跳转到编辑页，id通过路由传参
  router.push(`/myhouses/edit/${id}`)
}

// 删除
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

// 分页变化
const handlePageChange = (newPage) => {
  pageNum.value = newPage
  fetchHouseList()
}

// 筛选tab变化时重新加载
watch(currentTab, () => {
  pageNum.value = 1
  // 状态筛选前端做，接口只给 mine=true
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
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.btn-primary {
  padding: 10px 20px;
  background: #3072f6;
  color: #fff;
  text-decoration: none;
  border-radius: 4px;
}

/* 搜索栏 */
.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.search-bar input {
  flex: 1;
  height: 40px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 0 16px;
  font-size: 14px;
  outline: none;
}

.search-bar input:focus {
  border-color: #3072f6;
}

.search-bar button {
  padding: 0 24px;
  height: 40px;
  background: #3072f6;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.search-bar button.clear {
  background: #f5f5f5;
  color: #666;
}

.search-bar button:hover {
  opacity: 0.9;
}

/* 筛选标签 */
.filter-tabs {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.filter-tabs span {
  padding: 10px 0;
  cursor: pointer;
  color: #666;
}

.filter-tabs span.active {
  color: #3072f6;
  border-bottom: 2px solid #3072f6;
}

/* 房源卡片 */
.house-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.house-info h3 {
  font-size: 16px;
  margin-bottom: 8px;
}

.house-info p {
  color: #666;
  font-size: 14px;
}

.price {
  color: #ff4d4f;
  font-weight: 600;
}

.status {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  margin-top: 8px;
}

.status.draft { background: #fff7e6; color: #fa8c16; }
.status.listed { background: #f6ffed; color: #52c41a; }
.status.offline { background: #f5f5f5; color: #999; }

.house-actions {
  display: flex;
  gap: 10px;
}

.house-actions button {
  padding: 6px 16px;
  border: 1px solid #d9d9d9;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
}

.house-actions button:hover {
  border-color: #3072f6;
  color: #3072f6;
}

.house-actions button.danger:hover {
  border-color: #ff4d4f;
  color: #ff4d4f;
}

.loading, .empty {
  text-align: center;
  padding: 60px;
  color: #999;
}
</style>