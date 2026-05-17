<template>
  <div class="repair-page">
    <!-- 房东端视图 -->
    <div class="page-header">
      <div class="header-left">
        <h2>维修处理</h2>
        <p class="subtitle">处理租客的维修申请</p>
      </div>
    </div>

    <div class="filter-tabs">
      <span 
        v-for="tab in tabs" 
        :key="tab.value"
        class="filter-tab"
        :class="{ active: currentTab === tab.value }"
        @click="currentTab = tab.value"
      >
        {{ tab.label }}
        <span v-if="getTabCount(tab.value) > 0" class="tab-badge">{{ getTabCount(tab.value) }}</span>
      </span>
    </div>

    <div class="repair-list">
      <div v-if="loading" class="loading">加载中...</div>
      
      <div v-else-if="filteredRepairs.length === 0" class="empty">
        暂无{{ currentTab === 'all' ? '' : tabs.find(t => t.value === currentTab)?.label }}维修申请
      </div>

      <div 
        v-for="repair in filteredRepairs" 
        :key="repair.id"
        class="repair-card"
        @click="viewDetail(repair)"
      >
        <div class="repair-info">
          <div class="repair-header">
            <span class="repair-no">维修 #{{ repair.id }}</span>
            <span class="repair-status" :class="repair.status">{{ getStatusText(repair.status) }}</span>
          </div>
          
          <div class="repair-title">{{ repair.title }}</div>
          
          <div class="repair-house">
            <i class="fa-solid fa-home"></i>
            <span>房源：{{ repair.house?.title }}</span>
          </div>
          
          <div class="repair-tenant">
            <i class="fa-solid fa-user"></i>
            <span>租客：{{ repair.tenant_name }}</span>
          </div>
          
          <div class="repair-type">
            <i class="fa-solid fa-tag"></i>
            <span>类型：{{ getTypeText(repair.type) }}</span>
          </div>
          
          <div class="repair-desc">
            <i class="fa-solid fa-file-text"></i>
            <span>描述：{{ repair.description }}</span>
          </div>
          
          <div class="repair-dates">
            <div class="date-item">
              <i class="fa-solid fa-clock"></i>
              <span>申请时间：{{ repair.created_at }}</span>
            </div>
            <div v-if="repair.processed_at" class="date-item">
              <i class="fa-solid fa-check-circle"></i>
              <span>处理时间：{{ repair.processed_at }}</span>
            </div>
          </div>
        </div>
        
        <div class="repair-actions">
          <el-button type="text" @click.stop="viewDetail(repair)">
            <i class="fa-solid fa-eye"></i> 查看详情
          </el-button>
          <el-button 
            v-if="repair.status === 'pending'" 
            type="success" 
            size="small"
            @click.stop="handleRepair(repair)"
          >
            <i class="fa-solid fa-wrench"></i> 处理维修
          </el-button>
          <el-button 
            v-if="repair.status === 'processing'" 
            type="primary" 
            size="small"
            @click.stop="completeRepair(repair)"
          >
            <i class="fa-solid fa-check"></i> 完成维修
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
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import Pagination from '@/components/Pagination.vue'
import { mockRepairs } from '@/mock/repairs'
import { getRepairList, processRepair, completeRepair as completeRepairApi } from '@/api/repair'

const USE_MOCK_DATA = true

const loading = ref(false)
const currentTab = ref('all')
const pageNum = ref(1)
const pageSize = ref(10)
const total = ref(0)
const repairs = ref([])

// 标签列表
const tabs = [
  { label: '全部', value: 'all' },
  { label: '待处理', value: 'pending' },
  { label: '处理中', value: 'processing' },
  { label: '已完成', value: 'completed' }
]

const filteredRepairs = computed(() => {
  if (currentTab.value === 'all') {
    return repairs.value
  }
  return repairs.value.filter(repair => repair.status === currentTab.value)
})

const getTabCount = (status) => {
  if (status === 'all') return repairs.value.length
  return repairs.value.filter(r => r.status === status).length
}

const getStatusText = (status) => {
  const map = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成'
  }
  return map[status] || status
}

const getTypeText = (type) => {
  const map = {
    water: '水管维修',
    electricity: '电路维修',
    furniture: '家具维修',
    other: '其他维修'
  }
  return map[type] || type
}

const fetchRepairs = async () => {
  loading.value = true
  try {
    if (USE_MOCK_DATA) {
      const start = (pageNum.value - 1) * pageSize.value
      const end = start + pageSize.value
      repairs.value = mockRepairs.slice(start, end)
      total.value = mockRepairs.length
    } else {
      const res = await getRepairList({ page: pageNum.value, page_size: pageSize.value })
      if (res.code === 0) {
        repairs.value = res.data.list
        total.value = res.data.total
      }
    }
  } catch (error) {
    console.error('获取维修列表失败', error)
    repairs.value = []
  } finally {
    loading.value = false
  }
}

const viewDetail = (repair) => {
  ElMessage.info(`查看维修详情: ${repair.title}`)
}

const handleRepair = async (repair) => {
  try {
    await ElMessageBox.confirm(
      `确认处理维修申请「${repair.title}」？`,
      '提示',
      {
        confirmButtonText: '确认处理',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    if (USE_MOCK_DATA) {
      repair.status = 'processing'
      repair.processed_at = new Date().toLocaleString()
    } else {
      const res = await processRepair(repair.id)
      if (res.code === 0) {
        fetchRepairs()
      }
    }
    ElMessage.success('已开始处理')
  } catch {
    ElMessage.info('已取消')
  }
}

const completeRepair = async (repair) => {
  try {
    await ElMessageBox.confirm(
      `确认维修已完成「${repair.title}」？`,
      '提示',
      {
        confirmButtonText: '确认完成',
        cancelButtonText: '取消',
        type: 'success'
      }
    )
    if (USE_MOCK_DATA) {
      repair.status = 'completed'
    } else {
      const res = await completeRepairApi(repair.id)
      if (res.code === 0) {
        fetchRepairs()
      }
    }
    ElMessage.success('维修已完成')
  } catch {
    ElMessage.info('已取消')
  }
}

const handlePageChange = (page) => {
  pageNum.value = page
  fetchRepairs()
}

onMounted(() => {
  fetchRepairs()
})
</script>

<style scoped>
.repair-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20px 200px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.header-left h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.header-left .subtitle {
  margin: 5px 0 0;
  color: #999;
  font-size: 14px;
}

.filter-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  padding: 15px 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.filter-tab {
  padding: 10px 20px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s ease;
  position: relative;
}

.filter-tab:hover {
  background: #f0f5ff;
  color: #1890ff;
}

.filter-tab.active {
  background: #1890ff;
  color: #fff;
}

.filter-tab.active .tab-badge {
  background: rgba(255, 255, 255, 0.3);
}

.tab-badge {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 12px;
  margin-left: 6px;
  min-width: 20px;
  height: 20px;
  line-height: 18px;
  text-align: center;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(255, 77, 79, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.2s ease;
}

.tab-badge:hover {
  transform: scale(1.05);
  box-shadow: 0 3px 10px rgba(255, 77, 79, 0.45);
}

.repair-list {
  display: flex;
  flex-direction: column;
}

.loading, .empty {
  text-align: center;
  padding: 40px;
  color: #8c8c8c;
  background: #fff;
  border-radius: 8px;
  margin-bottom: 20px;
}

.repair-card {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  margin-bottom: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s ease;
}

.repair-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.repair-info {
  flex: 1;
  min-width: 0;
}

.repair-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.repair-no {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.repair-status {
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 20px;
}

.repair-status.pending {
  background: #fff7e6;
  color: #fa8c16;
}

.repair-status.processing {
  background: #e6f7ff;
  color: #1890ff;
}

.repair-status.completed {
  background: #f6ffed;
  color: #52c41a;
}

.repair-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

.repair-house,
.repair-tenant,
.repair-type,
.repair-desc {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.repair-house i,
.repair-tenant i,
.repair-type i,
.repair-desc i {
  margin-right: 8px;
  color: #1890ff;
}

.repair-desc {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.repair-dates {
  display: flex;
  gap: 20px;
  margin-top: 12px;
}

.date-item {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #999;
}

.date-item i {
  margin-right: 6px;
}

.repair-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-left: 20px;
}

.repair-actions .el-button {
  white-space: nowrap;
}
</style>