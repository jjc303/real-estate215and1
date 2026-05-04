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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Pagination from '@/components/Pagination.vue'
import service from '@/utils/request'
import mockData from'@/mock/myhouseList'
// 开发时备用
const USE_MOCK = true

const router = useRouter()
const loading = ref(false)
const currentTab = ref('all')
const searchKeyword = ref('')

//分页数据
const pageNum=ref(0)
const pageSize=ref(10)
const total=ref(6)


const tabs = [
  { label: '全部', value: 'all' },
  { label: '已上架', value: 'listed' },
  { label: '草稿', value: 'draft' },
  { label: '已下架', value: 'offline' }
]

// 筛选后的列表（状态 + 搜索）
const filteredHouses = computed(() => {
  if(USE_MOCK){
    let result = houses.value
  
    // 状态筛选
    if (currentTab.value !== 'all') {
        result = result.filter(h => h.status === currentTab.value)
    }
  
    // 搜索筛选
    if (searchKeyword.value.trim()) {
        const keyword = searchKeyword.value.toLowerCase()
        result = result.filter(h => 
            h.title?.toLowerCase().includes(keyword) ||
            h.address?.toLowerCase().includes(keyword) ||
            h.community?.toLowerCase().includes(keyword) ||
            h.house_type?.toLowerCase().includes(keyword)
        )
    }
  
    return result
  }
  //真实接口
  
})

const statusText = (status) => {
  const map = { draft: '草稿', listed: '已上架', offline: '已下架' }
  return map[status] || status
}

// 搜索
const handleSearch = () => {
  // 前端筛选，已自动响应
}

// 清空搜索
const clearSearch = () => {
  searchKeyword.value = ''
}

// 上架
const publishHouse = (id) => {
  const house = houses.value.find(h => h.id === id)
  if (house) house.status = 'listed'
}

// 下架
const offlineHouse = (id) => {
  const house = houses.value.find(h => h.id === id)
  if (house) house.status = 'offline'
}

// 编辑
const editHouse = (id) => {
  router.push({ name: 'editHouse', params: { id } })
}

// 删除
const deleteHouse = (id) => {
  if (!confirm('确定删除该房源？')) return
  const index = houses.value.findIndex(h => h.id === id)
  if (index > -1) houses.value.splice(index, 1)
}

onMounted(() => {
  // 模拟加载
  loading.value = true
  setTimeout(() => {
    loading.value = false
  }, 500)
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