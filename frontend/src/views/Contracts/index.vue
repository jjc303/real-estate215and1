<template>
  <div class="contracts-page">
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

    <div class="filter-tabs">
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

    <div class="contracts-list">
      <div v-if="loading" class="loading">加载中...</div>
      
      <div v-else-if="filteredContracts.length === 0" class="empty">
        暂无{{ currentTab === 'all' ? '' : tabs.find(t => t.value === currentTab)?.label }}合同
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
import service from '@/utils/request'

const USE_MOCK_DATA = true

const loading = ref(false)
const currentTab = ref('all')
const pageNum = ref(1)
const pageSize = ref(10)
const total = ref(0)
const contracts = ref([])

const tabs = [
  { label: '全部', value: 'all' },
  { label: '待确认', value: 'pending' },
  { label: '已生效', value: 'active' },
  { label: '已拒绝', value: 'rejected' },
  { label: '已终止', value: 'terminated' }
]

const mockContracts = [
  {
    id: 1,
    house_id: 1,
    tenant_id: 2,
    landlord_id: 3,
    appointment_id: 1,
    start_date: '2024-01-20',
    end_date: '2025-01-19',
    monthly_rent: '5000.00',
    deposit: '10000.00',
    status: 'active',
    remark: '一年整租',
    created_at: '2024-01-15T10:00:00',
    updated_at: '2024-01-15T10:30:00',
    house: {
      id: 1,
      title: '中南大学14舍',
      region: '岳麓区',
      address: '中南大学14舍',
      house_type: '三室一厅',
      area: '100.00',
      rent: '5000.00',
      deposit: '10000.00',
      status: 'listed'
    }
  },
  {
    id: 2,
    house_id: 2,
    tenant_id: 4,
    landlord_id: 5,
    appointment_id: 2,
    start_date: '2024-01-25',
    end_date: '2025-01-24',
    monthly_rent: '3500.00',
    deposit: '7000.00',
    status: 'pending',
    remark: '',
    created_at: '2024-01-16T14:00:00',
    updated_at: '2024-01-16T14:00:00',
    house: {
      id: 2,
      title: '麓山南路88号',
      region: '岳麓区',
      address: '麓山南路88号',
      house_type: '两室一厅',
      area: '80.00',
      rent: '3500.00',
      deposit: '7000.00',
      status: 'listed'
    }
  },
  {
    id: 3,
    house_id: 3,
    tenant_id: 6,
    landlord_id: 7,
    appointment_id: 3,
    start_date: '2023-06-15',
    end_date: '2024-06-14',
    monthly_rent: '2800.00',
    deposit: '5600.00',
    status: 'terminated',
    remark: '合同到期',
    created_at: '2023-06-10T09:00:00',
    updated_at: '2024-06-14T18:00:00',
    house: {
      id: 3,
      title: '天马小区3栋',
      region: '岳麓区',
      address: '天马小区3栋',
      house_type: '一室一厅',
      area: '50.00',
      rent: '2800.00',
      deposit: '5600.00',
      status: 'listed'
    }
  },
  {
    id: 4,
    house_id: 4,
    tenant_id: 8,
    landlord_id: 9,
    appointment_id: 4,
    start_date: '2024-01-15',
    end_date: '2025-01-14',
    monthly_rent: '4200.00',
    deposit: '8400.00',
    status: 'active',
    remark: '',
    created_at: '2024-01-10T11:00:00',
    updated_at: '2024-01-10T11:30:00',
    house: {
      id: 4,
      title: '阳光公寓A座',
      region: '雨花区',
      address: '阳光公寓A座',
      house_type: '两室两厅',
      area: '90.00',
      rent: '4200.00',
      deposit: '8400.00',
      status: 'listed'
    }
  },
  {
    id: 5,
    house_id: 5,
    tenant_id: 10,
    landlord_id: 11,
    appointment_id: 5,
    start_date: '2023-03-05',
    end_date: '2024-03-04',
    monthly_rent: '3000.00',
    deposit: '6000.00',
    status: 'rejected',
    remark: '租客拒绝签署',
    created_at: '2023-03-01T10:00:00',
    updated_at: '2023-03-02T10:00:00',
    house: {
      id: 5,
      title: '望月湖小区',
      region: '岳麓区',
      address: '望月湖小区',
      house_type: '两室一厅',
      area: '70.00',
      rent: '3000.00',
      deposit: '6000.00',
      status: 'listed'
    }
  },
  {
    id: 6,
    house_id: 6,
    tenant_id: 12,
    landlord_id: 13,
    appointment_id: 6,
    start_date: '2024-01-22',
    end_date: '2025-01-21',
    monthly_rent: '4800.00',
    deposit: '9600.00',
    status: 'pending',
    remark: '待租客确认',
    created_at: '2024-01-18T15:00:00',
    updated_at: '2024-01-18T15:00:00',
    house: {
      id: 6,
      title: '溁湾镇地铁口',
      region: '岳麓区',
      address: '溁湾镇地铁口',
      house_type: '三室两厅',
      area: '120.00',
      rent: '4800.00',
      deposit: '9600.00',
      status: 'listed'
    }
  }
]

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

const fetchContracts = async () => {
  loading.value = true
  
  try {
    if (USE_MOCK_DATA) {
      const start = (pageNum.value - 1) * pageSize.value
      const end = start + pageSize.value
      contracts.value = mockContracts.slice(start, end)
      total.value = mockContracts.length
    } else {
      const params = {
        page: pageNum.value,
        page_size: pageSize.value
      }
      const res = await service.get('/v1/contracts', { params })
      if (res.code === 0) {
        contracts.value = res.data.list
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
  // 跳转到合同详情页
  window.location.href = `/contracts/detail/${contract.id}`
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
      const idx = mockContracts.findIndex(c => c.id === contract.id)
      if (idx !== -1) {
        mockContracts[idx].status = 'active'
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
      const idx = mockContracts.findIndex(c => c.id === contract.id)
      if (idx !== -1) {
        mockContracts[idx].status = 'rejected'
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
      const idx = mockContracts.findIndex(c => c.id === contract.id)
      if (idx !== -1) {
        mockContracts[idx].status = 'cancelled'
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
      const idx = mockContracts.findIndex(c => c.id === contract.id)
      if (idx !== -1) {
        mockContracts[idx].status = 'terminated'
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
  padding: 20px;
  max-width: 1000px;
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
  border-bottom: 1px solid #f0f0f0;
}

.header-left.page-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #262626;
  margin: 0;
}

.page-header .subtitle {
  font-size: 14px;
  color: #8c8c8c;
  margin: 8px 0 0;
}

.header-right .el-button {
  padding: 8px 20px;
}

.filter-tabs {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.filter-tab {
  font-size: 14px;
  color: #595959;
  cursor: pointer;
  padding: 6px 12px 12px;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.filter-tab:hover {
  color: #1890ff;
  border-bottom-color: #1890ff;
}

.filter-tab.active {
  color: #1890ff;
  border-bottom-color: #1890ff;
}

.tab-badge {
  background: #ff4d4f;
  color: #fff;
  font-size: 12px;
  padding: 0 5px;
  border-radius: 10px;
  margin-left: 4px;
  min-width: 18px;
  text-align: center;
}

.contracts-list {
  display: flex;
  flex-direction: column;
}

.loading, .empty {
  text-align: center;
  padding: 60px;
  color: #8c8c8c;
}

.contract-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #fff;
  margin-bottom: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  border-radius: 8px;
  border: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.2s;
}

.contract-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
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
</style>
