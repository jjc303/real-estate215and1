<template>
  <div class="contract-detail-page">
    <div class="page-header">
      <div class="header-left">
        <button class="back-btn" @click="goBack">
          <i class="fa-solid fa-arrow-left"></i> 返回
        </button>
        <h2>合同详情</h2>
        <p class="subtitle">查看合同详细信息</p>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <span>加载中...</span>
    </div>
    
    <div v-else class="contract-content">
      <div class="contract-header-card">
        <div class="contract-title-row">
          <span class="contract-no">合同 #{{ contract.id }}</span>
          <span class="contract-status" :class="contract.status">{{ getStatusText(contract.status) }}</span>
        </div>
        <div class="house-title">{{ contract.house?.title }}</div>
        <div class="house-address">{{ contract.house?.region }} - {{ contract.house?.address }}</div>
      </div>

      <div class="contract-info-section">
        <div class="section-title">
          <i class="fa-solid fa-calendar-days"></i> 租期信息
        </div>
        <div class="info-grid">
          <div class="info-item">
            <label>起租日期</label>
            <span>{{ contract.start_date }}</span>
          </div>
          <div class="info-item">
            <label>到期日期</label>
            <span>{{ contract.end_date }}</span>
          </div>
          <div class="info-item">
            <label>租期时长</label>
            <span>{{ getLeaseTerm }}个月</span>
          </div>
          <div class="info-item">
            <label>创建时间</label>
            <span>{{ formatDatetime(contract.created_at) }}</span>
          </div>
        </div>
      </div>

      <div class="contract-info-section">
        <div class="section-title">
          <i class="fa-solid fa-money-bill"></i> 费用信息
        </div>
        <div class="info-grid">
          <div class="info-item">
            <label>月租金</label>
            <span class="price">¥{{ contract.monthly_rent }}/月</span>
          </div>
          <div class="info-item">
            <label>押金金额</label>
            <span class="price">¥{{ contract.deposit }}</span>
          </div>
        </div>
      </div>

      <div class="contract-info-section">
        <div class="section-title">
          <i class="fa-solid fa-home"></i> 房源信息
        </div>
        <div class="info-grid">
          <div class="info-item">
            <label>房源类型</label>
            <span>{{ contract.house?.house_type }}</span>
          </div>
          <div class="info-item">
            <label>建筑面积</label>
            <span>{{ contract.house?.area }}㎡</span>
          </div>
          <div class="info-item">
            <label>房源状态</label>
            <span :class="['status-tag', contract.house?.status]">{{ getHouseStatusText(contract.house?.status) }}</span>
          </div>
          <div class="info-item">
            <label>房源ID</label>
            <span>#{{ contract.house?.id }}</span>
          </div>
        </div>
      </div>

      <div class="contract-info-section">
        <div class="section-title">
          <i class="fa-solid fa-users"></i> 签约方信息
        </div>
        <div class="info-grid">
          <div class="info-item">
            <label>租客ID</label>
            <span>#{{ contract.tenant_id }}</span>
          </div>
          <div class="info-item">
            <label>房东ID</label>
            <span>#{{ contract.landlord_id }}</span>
          </div>
          <div class="info-item">
            <label>预约ID</label>
            <span>#{{ contract.appointment_id }}</span>
          </div>
          <div class="info-item">
            <label>合同ID</label>
            <span>#{{ contract.id }}</span>
          </div>
        </div>
      </div>

      <div class="contract-info-section">
        <div class="section-title">
          <i class="fa-solid fa-clock"></i> 时间记录
        </div>
        <div class="info-grid">
          <div class="info-item">
            <label>创建时间</label>
            <span>{{ formatDatetime(contract.created_at) }}</span>
          </div>
          <div class="info-item">
            <label>更新时间</label>
            <span>{{ formatDatetime(contract.updated_at) }}</span>
          </div>
        </div>
      </div>

      <div class="contract-info-section" v-if="contract.remark">
        <div class="section-title">
          <i class="fa-solid fa-file-text"></i> 备注信息
        </div>
        <div class="remark-content">{{ contract.remark }}</div>
      </div>

      <div class="contract-actions">
        <el-button 
          v-if="contract.status === 'pending'" 
          type="success"
          @click="confirmContract"
        >
          <i class="fa-solid fa-check"></i> 确认合同
        </el-button>
        <el-button 
          v-if="contract.status === 'pending'" 
          type="danger"
          @click="rejectContract"
        >
          <i class="fa-solid fa-x"></i> 拒绝合同
        </el-button>
        <el-button 
          v-if="contract.status === 'active'" 
          type="warning"
          @click="terminateContract"
        >
          <i class="fa-solid fa-stop-circle"></i> 终止合同
        </el-button>
        <el-button 
          v-if="contract.status === 'active' || contract.status === 'pending'" 
          type="info"
          @click="cancelContract"
        >
          <i class="fa-solid fa-ban"></i> 取消合同
        </el-button>
        <el-button 
          type="primary"
          @click="downloadContract"
        >
          <i class="fa-solid fa-download"></i> 下载合同
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import service from '@/utils/request'

const USE_MOCK_DATA = true

const loading = ref(true)
const contract = ref({
  id: 0,
  house_id: 0,
  tenant_id: 0,
  landlord_id: 0,
  appointment_id: 0,
  start_date: '',
  end_date: '',
  monthly_rent: '',
  deposit: '',
  status: 'pending',
  remark: '',
  created_at: '',
  updated_at: '',
  house: null
})

const mockContract = {
  id: 1,
  house_id: 12,
  tenant_id: 21,
  landlord_id: 9,
  appointment_id: 5,
  start_date: '2026-06-01',
  end_date: '2027-05-31',
  monthly_rent: '3000.00',
  deposit: '3000.00',
  status: 'active',
  remark: '一年整租',
  created_at: '2026-05-03T09:00:00',
  updated_at: '2026-05-03T09:30:00',
  house: {
    id: 12,
    title: '近地铁一室一厅',
    region: '浦东新区',
    address: 'xx路88号',
    house_type: '1室1厅1卫',
    area: '58.00',
    rent: '3200.00',
    deposit: '3200.00',
    status: 'listed'
  }
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

const getHouseStatusText = (status) => {
  const map = {
    draft: '草稿',
    listed: '已上架',
    offline: '已下架'
  }
  return map[status] || status
}

const getLeaseTerm = computed(() => {
  if (!contract.value.start_date || !contract.value.end_date) return 0
  const start = new Date(contract.value.start_date)
  const end = new Date(contract.value.end_date)
  const months = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth())
  return months
})

const formatDatetime = (datetime) => {
  if (!datetime) return ''
  const date = new Date(datetime)
  return date.toLocaleString('zh-CN')
}

const fetchContractDetail = async () => {
  loading.value = true
  
  try {
    const urlParams = new URLSearchParams(window.location.search)
    const id = urlParams.get('id') || window.location.pathname.split('/').pop() || '1'
    
    if (USE_MOCK_DATA) {
      contract.value = { ...mockContract, id: parseInt(id) }
    } else {
      const res = await service.get(`/v1/contracts/${id}`)
      if (res.code === 0) {
        contract.value = res.data
      }
    }
  } catch (e) {
    ElMessage.error('加载合同详情失败')
    console.error(e)
  } finally {
    loading.value = false
  }
}

const confirmContract = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要确认合同吗？\n合同 #${contract.value.id}\n房源：${contract.value.house?.title}`,
      '确认合同',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    if (USE_MOCK_DATA) {
      contract.value.status = 'active'
      ElMessage.success(`合同 #${contract.value.id} 已确认生效！`)
    } else {
      const res = await service.patch(`/v1/contracts/${contract.value.id}/confirm`)
      if (res.code === 0) {
        contract.value.status = 'active'
        ElMessage.success(`合同 #${contract.value.id} 已确认生效！`)
      }
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('确认失败，请稍后重试')
      console.error(e)
    }
  }
}

const rejectContract = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要拒绝合同吗？\n合同 #${contract.value.id}\n房源：${contract.value.house?.title}`,
      '拒绝合同',
      {
        confirmButtonText: '拒绝',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    if (USE_MOCK_DATA) {
      contract.value.status = 'rejected'
      ElMessage.success(`合同 #${contract.value.id} 已拒绝！`)
    } else {
      const res = await service.patch(`/v1/contracts/${contract.value.id}/reject`)
      if (res.code === 0) {
        contract.value.status = 'rejected'
        ElMessage.success(`合同 #${contract.value.id} 已拒绝！`)
      }
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('操作失败，请稍后重试')
      console.error(e)
    }
  }
}

const cancelContract = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要取消合同吗？\n合同 #${contract.value.id}\n房源：${contract.value.house?.title}`,
      '取消合同',
      {
        confirmButtonText: '取消',
        cancelButtonText: '返回',
        type: 'warning'
      }
    )
    
    if (USE_MOCK_DATA) {
      contract.value.status = 'cancelled'
      ElMessage.success(`合同 #${contract.value.id} 已取消！`)
    } else {
      const res = await service.patch(`/v1/contracts/${contract.value.id}/cancel`)
      if (res.code === 0) {
        contract.value.status = 'cancelled'
        ElMessage.success(`合同 #${contract.value.id} 已取消！`)
      }
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('操作失败，请稍后重试')
      console.error(e)
    }
  }
}

const terminateContract = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要终止合同吗？\n合同 #${contract.value.id}\n房源：${contract.value.house?.title}`,
      '终止合同',
      {
        confirmButtonText: '终止',
        cancelButtonText: '取消',
        type: 'danger'
      }
    )
    
    if (USE_MOCK_DATA) {
      contract.value.status = 'terminated'
      ElMessage.success(`合同 #${contract.value.id} 已终止！`)
    } else {
      const res = await service.patch(`/v1/contracts/${contract.value.id}/terminate`)
      if (res.code === 0) {
        contract.value.status = 'terminated'
        ElMessage.success(`合同 #${contract.value.id} 已终止！`)
      }
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('操作失败，请稍后重试')
      console.error(e)
    }
  }
}

const downloadContract = () => {
  ElMessage.success(`合同 #${contract.value.id} 下载成功！`)
}

const goBack = () => {
  window.history.back()
}

onMounted(() => {
  fetchContractDetail()
})
</script>

<style scoped>
.contract-detail-page {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #f5f5f5;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: #595959;
  font-size: 14px;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #e8e8e8;
}

.header-left h2 {
  font-size: 24px;
  font-weight: 600;
  color: #262626;
  margin: 0;
}

.header-left .subtitle {
  font-size: 14px;
  color: #8c8c8c;
  margin: 8px 0 0;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px;
  color: #8c8c8c;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f0f0f0;
  border-top-color: #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.contract-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.contract-header-card {
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  border-radius: 12px;
  padding: 24px;
  color: #fff;
}

.contract-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.contract-no {
  font-size: 14px;
  opacity: 0.9;
}

.contract-status {
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 20px;
  background: rgba(255,255,255,0.2);
}

.contract-status.active {
  background: #52c41a;
}

.house-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.house-address {
  font-size: 14px;
  opacity: 0.9;
}

.contract-info-section {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  border: 1px solid #f0f0f0;
  transition: all 0.3s ease;
}

.contract-info-section:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
  transform: translateY(-2px);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title i {
  color: #1890ff;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-item label {
  font-size: 14px;
  color: #8c8c8c;
}

.info-item span {
  font-size: 16px;
  color: #262626;
}

.info-item span.price {
  font-weight: 600;
  color: #ff4d4f;
}

.remark-content {
  font-size: 16px;
  color: #262626;
  line-height: 1.6;
}

.status-tag {
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 3px;
  display: inline-block;
}

.status-tag.draft {
  background: #f5f5f5;
  color: #8c8c8c;
}

.status-tag.listed {
  background: #f6ffed;
  color: #52c41a;
}

.status-tag.offline {
  background: #fff2f0;
  color: #ff4d4f;
}

.contract-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
}

.contract-actions .el-button {
  padding: 10px 20px;
}

@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .contract-actions {
    flex-wrap: wrap;
    justify-content: stretch;
  }
  
  .contract-actions .el-button {
    flex: 1;
    min-width: 120px;
  }
}
</style>