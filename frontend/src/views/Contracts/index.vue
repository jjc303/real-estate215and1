<template>
  <div class="contracts-page">
    <!-- 租客端视图 -->
    <template v-if="isTenant">
      <div class="page-header">
        <div class="header-left">
          <h2>我的合同</h2>
          <p class="subtitle">管理我的租房合同</p>
        </div>
      </div>

      <div class="stats-row" v-if="!loading && contractStats.total">
        <div class="stat-card" :class="{ success: contractStats.active > 0 }">
          <div class="stat-value">{{ contractStats.active }}</div>
          <div class="stat-label">已生效合同</div>
        </div>
        <div class="stat-card" :class="{ warning: contractStats.pending > 0 }">
          <div class="stat-value">{{ contractStats.pending }}</div>
          <div class="stat-label">待确认合同</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ contractStats.total }}</div>
          <div class="stat-label">合同总数</div>
        </div>
      </div>

      <div class="filter-tabs">
        <span 
          v-for="tab in tenantTabs" 
          :key="tab.value"
          class="filter-tab"
          :class="{ active: currentTab === tab.value }"
          @click="currentTab = tab.value"
        >
          {{ tab.label }}
          <span v-if="getTabCount(tab.value) > 0" class="tab-badge">{{ getTabCount(tab.value) }}</span>
        </span>
      </div>

      <div class="contracts-list">
        <div v-if="loading" class="loading">加载中...</div>
        
        <div v-else-if="filteredContracts.length === 0" class="empty">
          <div class="empty-icon"><i class="fa-solid fa-file-signature"></i></div>
          <p class="empty-text">暂无{{ currentTab === 'all' ? '' : tenantTabs.find(t => t.value === currentTab)?.label }}合同</p>
          <p class="empty-hint">租房合同会在这里显示</p>
        </div>

        <div 
          v-for="contract in filteredContracts" 
          :key="contract.id"
          class="contract-card"
          @click="viewDetail(contract)"
        >
          <div class="contract-info">
            <div class="contract-header">
              <span class="contract-no">合同 #{{ contract.id }}</span>
              <span class="contract-status" :class="contract.status">{{ getStatusText(contract.status) }}</span>
            </div>
            
            <div class="contract-title">{{ contract.house?.title }}</div>
            
            <div class="contract-parties">
              <div class="party-item">
                <span class="party-label">房东：</span>
                <span class="party-value">{{ contract.landlord_name }}</span>
              </div>
            </div>
            
            <div class="contract-dates">
              <div class="date-item">
                <i class="fa-solid fa-calendar-days"></i>
                <span>租期：{{ contract.start_date }} 至 {{ contract.end_date }}</span>
              </div>
            </div>
            
            <div class="contract-price">
              <span class="price-label">租金：</span>
              <span class="price-value">¥{{ contract.monthly_rent }}/月</span>
              <span class="deposit-info">押金：¥{{ contract.deposit }}</span>
            </div>
          </div>
          
          <div class="contract-actions">
            <el-button link @click.stop="viewDetail(contract)">
              <i class="fa-solid fa-eye"></i> 查看详情
            </el-button>
            <el-button 
              v-if="contract.status === 'pending'" 
              type="success" 
              size="small"
              @click.stop="confirmContract(contract)"
            >
              <i class="fa-solid fa-check"></i> 确认合同
            </el-button>
            <el-button 
              v-if="contract.status === 'pending'" 
              type="danger" 
              size="small"
              @click.stop="rejectContract(contract)"
            >
              <i class="fa-solid fa-x"></i> 拒绝
            </el-button>
          </div>
        </div>
      </div>
    </template>

    <!-- 房东端视图 -->
    <template v-else>
      <div class="page-header">
        <div class="header-left">
          <h2>合同管理</h2>
          <p class="subtitle">管理您的租房合同</p>
        </div>
        <div class="header-right">
          <el-button type="primary" @click="createContract">
            <i class="fa-solid fa-plus"></i> 新建合同
          </el-button>
        </div>
      </div>

      <div class="stats-row" v-if="!loading && contractStats.total">
        <div class="stat-card" :class="{ success: contractStats.active > 0 }">
          <div class="stat-value">{{ contractStats.active }}</div>
          <div class="stat-label">已生效合同</div>
        </div>
        <div class="stat-card" :class="{ warning: contractStats.pending > 0 }">
          <div class="stat-value">{{ contractStats.pending }}</div>
          <div class="stat-label">待确认合同</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ contractStats.total }}</div>
          <div class="stat-label">合同总数</div>
        </div>
      </div>

      <div class="filter-tabs">
        <span 
          v-for="tab in landlordTabs" 
          :key="tab.value"
          class="filter-tab"
          :class="{ active: currentTab === tab.value }"
          @click="currentTab = tab.value"
        >
          {{ tab.label }}
          <span v-if="getTabCount(tab.value) > 0" class="tab-badge">{{ getTabCount(tab.value) }}</span>
        </span>
      </div>

      <div class="contracts-list">
      <div v-if="loading" class="loading">加载中...</div>
      
      <div v-else-if="filteredContracts.length === 0" class="empty">
        <div class="empty-icon"><i class="fa-solid fa-file-signature"></i></div>
        <p class="empty-text">暂无{{ currentTab === 'all' ? '' : tabs.find(t => t.value === currentTab)?.label }}合同</p>
        <p class="empty-hint">租房合同会在这里显示</p>
      </div>

      <div 
        v-for="contract in filteredContracts" 
        :key="contract.id"
        class="contract-card"
        @click="viewDetail(contract)"
      >
        <div class="contract-info">
          <div class="contract-header">
            <span class="contract-no">合同 #{{ contract.id }}</span>
            <span class="contract-status" :class="contract.status">{{ getStatusText(contract.status) }}</span>
          </div>
          
          <div class="contract-title">{{ contract.house?.title }}</div>
          
          <div class="contract-dates">
            <div class="date-item">
              <i class="fa-solid fa-calendar-days"></i>
              <span>租期：{{ contract.start_date }} 至 {{ contract.end_date }}</span>
            </div>
          </div>
          
          <div class="contract-price">
            <span class="price-label">租金：</span>
            <span class="price-value">¥{{ contract.monthly_rent }}/月</span>
            <span class="deposit-info">押金：¥{{ contract.deposit }}</span>
          </div>
        </div>
        
        <div class="contract-actions">
          <el-button type="text" @click.stop="viewDetail(contract)">
            <i class="fa-solid fa-eye"></i> 查看详情
          </el-button>
          <el-button 
            v-if="contract.status === 'pending'" 
            type="success" 
            size="small"
            @click.stop="confirmContract(contract)"
          >
            <i class="fa-solid fa-check"></i> 确认合同
          </el-button>
          <el-button 
            v-if="contract.status === 'pending'" 
            type="danger" 
            size="small"
            @click.stop="rejectContract(contract)"
          >
            <i class="fa-solid fa-x"></i> 拒绝
          </el-button>
          <el-button 
            v-if="contract.status === 'active'" 
            type="warning" 
            size="small"
            @click.stop="terminateContract(contract)"
          >
            <i class="fa-solid fa-stop-circle"></i> 终止合同
          </el-button>
          <el-button 
            v-if="contract.status === 'active' || contract.status === 'pending'" 
            type="info" 
            size="small"
            @click.stop="cancelContract(contract)"
          >
            <i class="fa-solid fa-ban"></i> 取消合同
          </el-button>
        </div>
      </div>
    </div>
    </template>

    <Pagination 
      v-if="total > 0 && !loading"
      :pageNum="pageNum"
      :pageSize="pageSize"
      :total="total"
      @change="handlePageChange"
    />

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="合同详情"
      width="560px"
    >
      <div v-if="detailContract" class="detail-content">
        <div class="detail-section">
          <div class="detail-section-title">
            <i class="fa-solid fa-calendar-days"></i> 租期信息
          </div>
          <div class="detail-grid">
            <div class="detail-item-row">
              <span class="detail-label">起租日期</span>
              <span class="detail-value">{{ detailContract.start_date }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">到期日期</span>
              <span class="detail-value">{{ detailContract.end_date }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">租期时长</span>
              <span class="detail-value">{{ getLeaseTerm(detailContract) }}个月</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">创建时间</span>
              <span class="detail-value">{{ formatDateTime(detailContract.created_at) }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <div class="detail-section-title">
            <i class="fa-solid fa-money-bill"></i> 费用信息
          </div>
          <div class="detail-grid">
            <div class="detail-item-row">
              <span class="detail-label">月租金</span>
              <span class="detail-value price">¥{{ detailContract.monthly_rent }}/月</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">押金金额</span>
              <span class="detail-value price">¥{{ detailContract.deposit }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <div class="detail-section-title">
            <i class="fa-solid fa-home"></i> 房源信息
          </div>
          <div class="detail-grid">
            <div class="detail-item-row">
              <span class="detail-label">房源名称</span>
              <span class="detail-value">{{ detailContract.house?.title }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">所在区域</span>
              <span class="detail-value">{{ detailContract.house?.region }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">详细地址</span>
              <span class="detail-value">{{ detailContract.house?.address }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">房源类型</span>
              <span class="detail-value">{{ detailContract.house?.house_type }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">建筑面积</span>
              <span class="detail-value">{{ detailContract.house?.area }}㎡</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <div class="detail-section-title">
            <i class="fa-solid fa-users"></i> 签约方信息
          </div>
          <div class="detail-grid">
            <div class="detail-item-row">
              <span class="detail-label">{{ isTenant ? '房东' : '租客' }}</span>
              <span class="detail-value">{{ isTenant ? detailContract.landlord_name : detailContract.tenant_name }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">合同编号</span>
              <span class="detail-value">#{{ detailContract.id }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">合同状态</span>
              <span class="detail-value">
                <span class="contract-status" :class="detailContract.status">{{ getStatusText(detailContract.status) }}</span>
              </span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <div class="detail-section-title">
            <i class="fa-solid fa-clock"></i> 时间记录
          </div>
          <div class="detail-grid">
            <div class="detail-item-row">
              <span class="detail-label">创建时间</span>
              <span class="detail-value">{{ formatDateTime(detailContract.created_at) }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">更新时间</span>
              <span class="detail-value">{{ formatDateTime(detailContract.updated_at) }}</span>
            </div>
          </div>
        </div>

        <div v-if="detailContract.remark" class="detail-section">
          <div class="detail-section-title">
            <i class="fa-solid fa-file-text"></i> 备注信息
          </div>
          <div class="detail-remark">{{ detailContract.remark }}</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
    <BackToTop />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import Pagination from '@/components/Pagination.vue'
import BackToTop from '@/components/BackToTop.vue'
import service from '@/utils/request'
import { useUserStore } from '@/stores/user'
import { mockTenantContracts, mockLandlordContracts } from '@/mock/contracts'

const userStore = useUserStore()

const USE_MOCK_DATA = false

const loading = ref(false)
const currentTab = ref('all')
const pageNum = ref(1)
const pageSize = ref(10)
const total = ref(0)
const contracts = ref([])

// 查看详情相关
const detailDialogVisible = ref(false)
const detailContract = ref(null)

// 判断当前用户是否是租客
const isTenant = computed(() => userStore.userRole === 'tenant')

// 租客端标签
const tenantTabs = [
  { label: '全部', value: 'all' },
  { label: '待确认', value: 'pending' },
  { label: '已生效', value: 'active' },
  { label: '已拒绝', value: 'rejected' },
  { label: '已终止', value: 'terminated' }
]

// 房东端标签
const landlordTabs = [
  { label: '全部', value: 'all' },
  { label: '待确认', value: 'pending' },
  { label: '已生效', value: 'active' },
  { label: '已拒绝', value: 'rejected' },
  { label: '已终止', value: 'terminated' }
]

// 当前使用的标签列表
const currentTabs = computed(() => isTenant.value ? tenantTabs : landlordTabs)

const filteredContracts = computed(() => {
  if (currentTab.value === 'all') {
    return contracts.value
  }
  return contracts.value.filter(c => c.status === currentTab.value)
})

const getTabCount = (status) => {
  if (status === 'all') return contracts.value.length
  return contracts.value.filter(c => c.status === status).length
}

const contractStats = computed(() => ({
  active: contracts.value.filter(c => c.status === 'active').length,
  pending: contracts.value.filter(c => c.status === 'pending').length,
  total: contracts.value.length
}))

const getStatusText = (status) => {
  const map = {
    pending: '待确认',
    active: '已生效',
    rejected: '已拒绝',
    cancelled: '已取消',
    terminated: '已终止'
  }
  return map[status] || status
}

const getHouseStatusText = (status) => {
  const map = {
    draft: '草稿',
    listed: '已上架',
    offline: '已下架'
  }
  return map[status] || status
}

const getLeaseTerm = (contract) => {
  if (!contract.start_date || !contract.end_date) return 0
  const start = new Date(contract.start_date)
  const end = new Date(contract.end_date)
  return (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth())
}

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  const date = new Date(datetime)
  return date.toLocaleString('zh-CN')
}

const fetchContracts = async () => {
  loading.value = true
  
  try {
    if (USE_MOCK_DATA) {
      // 根据角色使用不同的模拟数据
      const currentMockData = isTenant.value ? mockTenantContracts : mockLandlordContracts
      const start = (pageNum.value - 1) * pageSize.value
      const end = start + pageSize.value
      contracts.value = currentMockData.slice(start, end)
      total.value = currentMockData.length
    } else {
      const params = {
        page: pageNum.value,
        page_size: pageSize.value
      }
      const res = await service.get('/v1/contracts', { params })
      if (res.code === 0) {
        contracts.value = res.data.list.map(item => ({
          ...item,
          landlord_name: isTenant.value ? `房东 #${item.landlord_id}` : '',
          tenant_name: isTenant.value ? '' : `租客 #${item.tenant_id}`
        }))
        total.value = res.data.total
      }
    }
  } catch (e) {
    ElMessage.error('加载合同列表失败')
    console.error(e)
  } finally {
    loading.value = false
  }
}

const createContract = () => {
  // 跳转到创建合同页面
  window.location.href = '/contracts/create'
}

const viewDetail = (contract) => {
  detailContract.value = contract
  detailDialogVisible.value = true
}

const confirmContract = async (contract) => {
  try {
    await ElMessageBox.confirm(
      `确定要确认合同吗？\n合同 #${contract.id}\n房源：${contract.house?.title}\n租期：${contract.start_date} 至 ${contract.end_date}`,
      '确认合同',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    if (USE_MOCK_DATA) {
      const currentMockData = isTenant.value ? mockTenantContracts : mockLandlordContracts
      const idx = currentMockData.findIndex(c => c.id === contract.id)
      if (idx !== -1) {
        currentMockData[idx].status = 'active'
      }
      ElMessage.success(`合同 #${contract.id} 已确认生效！`)
      fetchContracts()
    } else {
      const res = await service.patch(`/v1/contracts/${contract.id}/confirm`)
      if (res.code === 0) {
        ElMessage.success(`合同 #${contract.id} 已确认生效！`)
        fetchContracts()
      }
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('确认失败，请稍后重试')
      console.error(e)
    }
  }
}

const rejectContract = async (contract) => {
  try {
    await ElMessageBox.confirm(
      `确定要拒绝合同吗？\n合同 #${contract.id}\n房源：${contract.house?.title}`,
      '拒绝合同',
      {
        confirmButtonText: '拒绝',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    if (USE_MOCK_DATA) {
      const currentMockData = isTenant.value ? mockTenantContracts : mockLandlordContracts
      const idx = currentMockData.findIndex(c => c.id === contract.id)
      if (idx !== -1) {
        currentMockData[idx].status = 'rejected'
      }
      ElMessage.success(`合同 #${contract.id} 已拒绝！`)
      fetchContracts()
    } else {
      const res = await service.patch(`/v1/contracts/${contract.id}/reject`)
      if (res.code === 0) {
        ElMessage.success(`合同 #${contract.id} 已拒绝！`)
        fetchContracts()
      }
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('操作失败，请稍后重试')
      console.error(e)
    }
  }
}

const cancelContract = async (contract) => {
  try {
    await ElMessageBox.confirm(
      `确定要取消合同吗？\n合同 #${contract.id}\n房源：${contract.house?.title}`,
      '取消合同',
      {
        confirmButtonText: '取消',
        cancelButtonText: '返回',
        type: 'warning'
      }
    )
    
    if (USE_MOCK_DATA) {
      const currentMockData = isTenant.value ? mockTenantContracts : mockLandlordContracts
      const idx = currentMockData.findIndex(c => c.id === contract.id)
      if (idx !== -1) {
        currentMockData[idx].status = 'cancelled'
      }
      ElMessage.success(`合同 #${contract.id} 已取消！`)
      fetchContracts()
    } else {
      const res = await service.patch(`/v1/contracts/${contract.id}/cancel`)
      if (res.code === 0) {
        ElMessage.success(`合同 #${contract.id} 已取消！`)
        fetchContracts()
      }
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('操作失败，请稍后重试')
      console.error(e)
    }
  }
}

const terminateContract = async (contract) => {
  try {
    await ElMessageBox.confirm(
      `确定要终止合同吗？\n合同 #${contract.id}\n房源：${contract.house?.title}`,
      '终止合同',
      {
        confirmButtonText: '终止',
        cancelButtonText: '取消',
        type: 'danger'
      }
    )
    
    if (USE_MOCK_DATA) {
      const currentMockData = isTenant.value ? mockTenantContracts : mockLandlordContracts
      const idx = currentMockData.findIndex(c => c.id === contract.id)
      if (idx !== -1) {
        currentMockData[idx].status = 'terminated'
      }
      ElMessage.success(`合同 #${contract.id} 已终止！`)
      fetchContracts()
    } else {
      const res = await service.patch(`/v1/contracts/${contract.id}/terminate`)
      if (res.code === 0) {
        ElMessage.success(`合同 #${contract.id} 已终止！`)
        fetchContracts()
      }
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('操作失败，请稍后重试')
      console.error(e)
    }
  }
}

const handlePageChange = (newPage) => {
  pageNum.value = newPage
  fetchContracts()
}

onMounted(() => {
  fetchContracts()
})
</script>

<style scoped>
.contracts-page {
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

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.stat-card {
  background: #fff;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border-left: 3px solid #e2e8f0;
  transition: all 0.2s ease;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.stat-card.warning {
  border-left-color: #f59e0b;
}

.stat-card.danger {
  border-left-color: #ef4444;
}

.stat-card.success {
  border-left-color: #10b981;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: #94a3b8;
}

.header-right .el-button {
  padding: 8px 20px;
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

.contracts-list {
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

.contract-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  margin-bottom: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.2s ease;
}

.contract-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transform: translateY(-3px);
}

.contract-info {
  flex: 1;
  min-width: 0;
}

.contract-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.contract-no {
  font-size: 14px;
  color: #8c8c8c;
}

.contract-status {
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 3px;
}

.contract-status.pending {
  background: #fff7e6;
  color: #fa8c16;
}

.contract-status.active {
  background: #f6ffed;
  color: #52c41a;
}

.contract-status.rejected {
  background: #fff2f0;
  color: #ff4d4f;
}

.contract-status.cancelled {
  background: #f5f5f5;
  color: #8c8c8c;
}

.contract-status.terminated {
  background: #fff2f0;
  color: #ff4d4f;
}

.contract-title {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 12px;
}

.contract-parties {
  display: flex;
  gap: 24px;
  margin-bottom: 10px;
}

.party-item {
  font-size: 14px;
}

.party-label {
  color: #8c8c8c;
}

.party-value {
  color: #595959;
}

.contract-dates {
  display: flex;
  gap: 24px;
  margin-bottom: 10px;
}

.date-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #595959;
}

.date-item i {
  color: #8c8c8c;
}

.contract-price {
  display: flex;
  align-items: center;
  gap: 16px;
}

.price-label {
  font-size: 14px;
  color: #8c8c8c;
}

.contracts-page .contract-card .price-value {
  font-size: 18px;
  font-weight: 600;
  color: #64748b !important;
}

.deposit-info {
  font-size: 14px;
  color: #8c8c8c;
}

.contract-actions {
  flex-shrink: 0;
  display: flex;
  gap: 10px;
  margin-left: 20px;
}

.contract-actions .el-button {
  padding: 6px 16px;
  border-radius: 6px;
  font-weight: normal;
}

.contract-actions .el-button--success {
  background: #69c0ff !important;
  border-color: #69c0ff !important;
  color: #fff !important;
}

.contract-actions .el-button--danger {
  background: #ff7875 !important;
  border-color: #ff7875 !important;
  color: #fff !important;
}

.contract-actions .el-button--warning {
  background: #ff7875 !important;
  border-color: #ff7875 !important;
  color: #fff !important;
}

@media (max-width: 768px) {
  .contract-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .contract-actions {
    margin-left: 0;
    width: 100%;
    justify-content: flex-end;
  }
  
  .contract-parties, .contract-dates {
    gap: 12px;
    flex-wrap: wrap;
  }
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

.detail-value.price {
  font-size: 16px;
  font-weight: 600;
  color: #1890ff;
}

.detail-remark {
  font-size: 14px;
  color: #595959;
  line-height: 1.6;
  padding: 10px 12px;
  background: #fafafa;
  border-radius: 6px;
}
</style>
