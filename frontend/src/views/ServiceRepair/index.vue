<template>
  <div class="repair-page">
    <div class="page-header">
      <div class="header-left">
        <h2>维修申请</h2>
        <p class="subtitle">提交和管理您的维修申请</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showRepairDialog">
          <i class="fa-solid fa-plus"></i> 提交维修申请
        </el-button>
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
        <div class="empty-icon"><i class="fa-solid fa-tools"></i></div>
        <p class="empty-text">暂无{{ currentTab === 'all' ? '' : tabs.find(t => t.value === currentTab)?.label }}维修申请</p>
        <p class="empty-hint">维修申请记录会在这里显示</p>
      </div>

      <div 
        v-for="repair in filteredRepairs" 
        :key="repair.id"
        class="repair-card"
      >
        <div class="repair-info" @click="viewDetail(repair)">
          <div class="repair-header">
            <span class="repair-no">维修 #{{ repair.id }}</span>
            <span class="repair-status" :class="repair.status">{{ getStatusText(repair.status) }}</span>
          </div>
          
          <div class="repair-title">{{ repair.title }}</div>
          
          <div class="repair-house">
            <i class="fa-solid fa-home"></i>
            <span>房源：{{ repair.house?.title }}</span>
          </div>
          
          <div class="repair-type">
            <i class="fa-solid fa-tag"></i>
            <span>类型：{{ getTypeText(repair.type) }}</span>
          </div>
          
          <div class="repair-desc">
            <i class="fa-solid fa-file-text"></i>
            <span>{{ repair.description }}</span>
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
          <el-button link @click.stop="viewDetail(repair)">
            <i class="fa-solid fa-eye"></i> 查看详情
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

    <el-dialog
      v-model="dialogVisible"
      title="提交维修申请"
      width="500px"
    >
      <el-form :model="repairForm" label-width="80px">
        <el-form-item label="合同">
          <el-select v-model="repairForm.contract_id" placeholder="请选择合同" style="width: 100%">
            <el-option 
              v-for="house in myHouses" 
              :key="house.id" 
              :label="house.title" 
              :value="house.id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="维修类型">
          <el-select v-model="repairForm.type" placeholder="请选择类型" style="width: 100%">
            <el-option label="水管维修" value="water" />
            <el-option label="电路维修" value="electricity" />
            <el-option label="家具维修" value="furniture" />
            <el-option label="其他维修" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="维修标题">
          <el-input v-model="repairForm.title" placeholder="请输入维修标题" />
        </el-form-item>
        <el-form-item label="问题描述">
          <el-input 
            v-model="repairForm.description" 
            type="textarea" 
            :rows="4" 
            placeholder="请详细描述需要维修的问题"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRepair">提交</el-button>
      </template>
    </el-dialog>

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="维修详情"
      width="560px"
    >
      <div v-if="detailRepair" class="detail-content">
        <div class="detail-section">
          <div class="detail-section-title">
            <i class="fa-solid fa-file-text"></i> 基本信息
          </div>
          <div class="detail-grid">
            <div class="detail-item-row">
              <span class="detail-label">维修编号</span>
              <span class="detail-value">#{{ detailRepair.id }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">维修标题</span>
              <span class="detail-value">{{ detailRepair.title }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">维修类型</span>
              <span class="detail-value">
                <span class="type-tag">{{ getTypeText(detailRepair.type) }}</span>
              </span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">维修状态</span>
              <span class="detail-value">
                <span class="repair-status-detail" :class="detailRepair.status">{{ getStatusText(detailRepair.status) }}</span>
              </span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <div class="detail-section-title">
            <i class="fa-solid fa-align-left"></i> 问题描述
          </div>
          <div class="detail-desc">{{ detailRepair.description }}</div>
        </div>

        <div class="detail-section">
          <div class="detail-section-title">
            <i class="fa-solid fa-home"></i> 关联信息
          </div>
          <div class="detail-grid">
            <div class="detail-item-row">
              <span class="detail-label">房源</span>
              <span class="detail-value">{{ detailRepair.house?.title }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">合同编号</span>
              <span class="detail-value">#{{ detailRepair.contract_id }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <div class="detail-section-title">
            <i class="fa-solid fa-clock"></i> 时间记录
          </div>
          <div class="detail-grid">
            <div class="detail-item-row">
              <span class="detail-label">申请时间</span>
              <span class="detail-value">{{ detailRepair.created_at }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">处理时间</span>
              <span class="detail-value">{{ detailRepair.processed_at || '未处理' }}</span>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <BackToTop />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import Pagination from '@/components/Pagination.vue'
import BackToTop from '@/components/BackToTop.vue'
import { mockTenantRepairs, mockMyHouses } from '@/mock/serviceRepairs'
import { getRepairList, createRepair } from '@/api/repair'
import service from '@/utils/request'

const USE_MOCK_DATA = false

const loading = ref(false)
const currentTab = ref('all')
const pageNum = ref(1)
const pageSize = ref(10)
const total = ref(0)
const repairs = ref([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const detailRepair = ref(null)
const myHouses = ref([])

const repairForm = ref({
  contract_id: '',
  type: '',
  title: '',
  description: ''
})

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

const formatDateTime = (datetime) => {
  if (!datetime) return ''
  const date = new Date(datetime)
  return date.toLocaleString('zh-CN')
}

const fetchRepairs = async () => {
  loading.value = true
  try {
    if (USE_MOCK_DATA) {
      const start = (pageNum.value - 1) * pageSize.value
      const end = start + pageSize.value
      repairs.value = mockTenantRepairs.slice(start, end)
      total.value = mockTenantRepairs.length
    } else {
      const res = await getRepairList({ page: pageNum.value, page_size: pageSize.value })
      if (res.code === 0) {
        repairs.value = res.data.list.map(item => ({
          ...item,
          title: item.description ? item.description.slice(0, 20) + (item.description.length > 20 ? '...' : '') : '维修申请',
          house: { title: `房源 #${item.house_id}` },
          type: 'other',
          created_at: formatDateTime(item.created_at),
          processed_at: item.processed_at ? formatDateTime(item.processed_at) : null
        }))
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

const fetchMyHouses = async () => {
  if (USE_MOCK_DATA) {
    myHouses.value = mockMyHouses
  } else {
    try {
      const res = await service.get('/v1/contracts', { params: { page: 1, page_size: 100 } })
      if (res.code === 0) {
        myHouses.value = res.data.list
          .filter(c => c.status === 'active')
          .map(c => ({
            id: c.id,
            title: c.house?.title || `房源 #${c.house_id}`
          }))
      }
    } catch (e) {
      console.error('获取合同列表失败', e)
      myHouses.value = []
    }
  }
}

const showRepairDialog = () => {
  repairForm.value = {
    contract_id: '',
    type: '',
    title: '',
    description: ''
  }
  dialogVisible.value = true
}

const submitRepair = async () => {
  if (!repairForm.value.contract_id) {
    ElMessage.warning('请选择合同')
    return
  }
  if (!repairForm.value.type) {
    ElMessage.warning('请选择维修类型')
    return
  }
  if (!repairForm.value.title) {
    ElMessage.warning('请输入维修标题')
    return
  }
  if (!repairForm.value.description) {
    ElMessage.warning('请输入问题描述')
    return
  }

  try {
    if (USE_MOCK_DATA) {
      const newRepair = {
        id: repairs.value.length + 1,
        contract_id: repairForm.value.contract_id,
        house: myHouses.value.find(h => h.id === repairForm.value.contract_id),
        type: repairForm.value.type,
        title: repairForm.value.title,
        description: repairForm.value.description,
        status: 'pending',
        created_at: new Date().toLocaleString(),
        processed_at: null
      }
      repairs.value.unshift(newRepair)
      total.value++
      dialogVisible.value = false
      ElMessage.success('维修申请提交成功')
    } else {
      const res = await createRepair({
        contract_id: repairForm.value.contract_id,
        description: repairForm.value.description
      })
      if (res.code === 0) {
        dialogVisible.value = false
        ElMessage.success('维修申请提交成功')
        fetchRepairs()
      }
    }
  } catch (error) {
    ElMessage.error('提交失败，请稍后重试')
  }
}

const viewDetail = (repair) => {
  detailRepair.value = repair
  detailVisible.value = true
}

const handlePageChange = (page) => {
  pageNum.value = page
  fetchRepairs()
}

onMounted(() => {
  fetchRepairs()
  fetchMyHouses()
})
</script>

<style scoped>
.repair-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f4f6f9 0%, #edf0f5 100%);
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
  padding: 60px 40px;
  color: #8c8c8c;
  background: #fff;
  border-radius: 8px;
  margin-bottom: 20px;
}

.empty-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 15px;
  color: #8c8c8c;
  margin: 0 0 4px;
}

.empty-hint {
  font-size: 13px;
  color: #b0b4bc;
  margin: 0;
}

.repair-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  margin-bottom: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s ease;
}

.repair-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transform: translateY(-3px);
}

.repair-info {
  flex: 1;
  min-width: 0;
  cursor: pointer;
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
.repair-type,
.repair-desc {
  display: flex;
  align-items: flex-start;
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.repair-house i,
.repair-type i,
.repair-desc i {
  margin-right: 8px;
  color: #1890ff;
  min-width: 16px;
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
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-left: 20px;
}

.detail-content {
  padding: 0;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section-title {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-section-title i {
  color: #1890ff;
  margin-right: 6px;
}

.detail-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.detail-item-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.detail-label {
  font-size: 14px;
  color: #8c8c8c;
  flex-shrink: 0;
}

.detail-value {
  font-size: 14px;
  color: #262626;
  text-align: right;
}

.detail-desc {
  font-size: 14px;
  color: #595959;
  line-height: 1.6;
  padding: 10px 12px;
  background: #fafafa;
  border-radius: 6px;
}

.type-tag {
  font-size: 12px;
  padding: 3px 10px;
  background: #e6f7ff;
  color: #1890ff;
  border-radius: 4px;
}

.repair-status-detail {
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 3px;
}

.repair-status-detail.pending {
  background: #fff7e6;
  color: #fa8c16;
}

.repair-status-detail.processing {
  background: #e6f7ff;
  color: #1890ff;
}

.repair-status-detail.completed {
  background: #f6ffed;
  color: #52c41a;
}
</style>
