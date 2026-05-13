<template>
  <div class="bill-detail-page">
    <div class="page-header">
      <div class="header-left">
        <button class="back-btn" @click="goBack">
          <i class="fa-solid fa-arrow-left"></i> 返回
        </button>
        <h2>账单详情</h2>
        <p class="subtitle">查看账单详细信息</p>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <span>加载中...</span>
    </div>
    
    <div v-else class="bill-content">
      <div class="bill-header-card">
        <div class="bill-title-row">
          <span class="bill-no">账单 #{{ bill.id }}</span>
          <span class="bill-status" :class="bill.status">{{ getStatusText(bill.status) }}</span>
        </div>
        <div class="house-title">{{ bill.house?.title }}</div>
        <div class="house-address">{{ bill.house?.region }} - {{ bill.house?.address }}</div>
      </div>

      <div class="bill-info-section">
        <div class="section-title">
          <i class="fa-solid fa-file-invoice"></i> 账单信息
        </div>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">账期</span>
            <span class="info-value">{{ bill.period }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">应付金额</span>
            <span class="info-value highlight">¥{{ bill.amount }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">到期时间</span>
            <span class="info-value">{{ bill.due_date }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">支付时间</span>
            <span class="info-value">{{ bill.paid_date || '-' }}</span>
          </div>
        </div>
      </div>

      <div class="bill-info-section">
        <div class="section-title">
          <i class="fa-solid fa-home"></i> 房源信息
        </div>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">房源名称</span>
            <span class="info-value">{{ bill.house?.title }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">所在区域</span>
            <span class="info-value">{{ bill.house?.region }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">详细地址</span>
            <span class="info-value">{{ bill.house?.address }}</span>
          </div>
        </div>
      </div>

      <div class="bill-info-section">
        <div class="section-title">
          <i class="fa-solid fa-file-signature"></i> 关联信息
        </div>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">合同编号</span>
            <span class="info-value">合同 #{{ bill.contract_id }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">创建时间</span>
            <span class="info-value">{{ formatDateTime(bill.created_at) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">更新时间</span>
            <span class="info-value">{{ formatDateTime(bill.updated_at) }}</span>
          </div>
        </div>
      </div>

      <div class="bill-actions">
        <el-button 
          v-if="bill.status === 'unpaid'" 
          type="primary" 
          size="large"
          @click="payBill"
        >
          <i class="fa-solid fa-credit-card"></i> 立即支付
        </el-button>
        <el-button 
          v-if="bill.status === 'overdue'" 
          type="danger" 
          size="large"
          @click="payBill"
        >
          <i class="fa-solid fa-exclamation-circle"></i> 逾期支付
        </el-button>
        <el-button 
          v-if="bill.status === 'paid'" 
          type="success" 
          size="large"
          disabled
        >
          <i class="fa-solid fa-check"></i> 已支付
        </el-button>
        <el-button size="large" @click="goBack">
          <i class="fa-solid fa-arrow-left"></i> 返回列表
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import service from '@/utils/request'

const USE_MOCK_DATA = true

const loading = ref(true)
const bill = ref({})

const mockBills = [
  {
    id: 1,
    contract_id: 1,
    house_id: 1,
    tenant_id: 2,
    landlord_id: 3,
    period: '2024年1月',
    amount: '5000.00',
    status: 'paid',
    due_date: '2024-01-10',
    paid_date: '2024-01-05',
    created_at: '2024-01-01T00:00:00',
    updated_at: '2024-01-05T10:00:00',
    house: {
      id: 1,
      title: '麓山南精装两室',
      region: '岳麓区',
      address: '麓山南路100号',
      house_type: '两室一厅',
      area: '85.00',
      rent: '5000.00'
    }
  },
  {
    id: 2,
    contract_id: 1,
    house_id: 1,
    tenant_id: 2,
    landlord_id: 3,
    period: '2024年2月',
    amount: '5000.00',
    status: 'unpaid',
    due_date: '2024-02-10',
    paid_date: null,
    created_at: '2024-02-01T00:00:00',
    updated_at: '2024-02-01T00:00:00',
    house: {
      id: 1,
      title: '麓山南精装两室',
      region: '岳麓区',
      address: '麓山南路100号',
      house_type: '两室一厅',
      area: '85.00',
      rent: '5000.00'
    }
  },
  {
    id: 3,
    contract_id: 2,
    house_id: 2,
    tenant_id: 4,
    landlord_id: 5,
    period: '2024年1月',
    amount: '3500.00',
    status: 'overdue',
    due_date: '2024-01-15',
    paid_date: null,
    created_at: '2024-01-01T00:00:00',
    updated_at: '2024-01-01T00:00:00',
    house: {
      id: 2,
      title: '天马小区3栋',
      region: '岳麓区',
      address: '天马小区3栋',
      house_type: '一室一厅',
      area: '50.00',
      rent: '3500.00'
    }
  }
]

const getStatusText = (status) => {
  const map = {
    unpaid: '待支付',
    paid: '已支付',
    overdue: '已逾期'
  }
  return map[status] || status
}

const formatDateTime = (dateTime) => {
  if (!dateTime) return '-'
  const date = new Date(dateTime)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const fetchBillDetail = async () => {
  loading.value = true
  try {
    const billId = window.location.pathname.split('/').pop()
    
    if (USE_MOCK_DATA) {
      bill.value = mockBills.find(b => b.id == billId) || {}
    } else {
      const res = await service.get(`/v1/bills/${billId}`)
      if (res.code === 0) {
        bill.value = res.data
      }
    }
  } catch (e) {
    ElMessage.error('加载账单详情失败')
    console.error(e)
  } finally {
    loading.value = false
  }
}

const payBill = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要支付账单吗？\n账单 #${bill.value.id}\n房源：${bill.value.house?.title}\n金额：¥${bill.value.amount}`,
      '确认支付',
      {
        confirmButtonText: '确认支付',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    if (USE_MOCK_DATA) {
      bill.value.status = 'paid'
      bill.value.paid_date = new Date().toISOString().split('T')[0]
      ElMessage.success(`账单 #${bill.value.id} 支付成功！`)
    } else {
      const res = await service.patch(`/v1/bills/${bill.value.id}/pay`)
      if (res.code === 0) {
        bill.value.status = 'paid'
        bill.value.paid_date = new Date().toISOString().split('T')[0]
        ElMessage.success(`账单 #${bill.value.id} 支付成功！`)
      }
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('支付失败，请稍后重试')
      console.error(e)
    }
  }
}

const goBack = () => {
  window.history.back()
}

onMounted(() => {
  fetchBillDetail()
})
</script>

<style scoped>
.bill-detail-page {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  background: #fff;
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
  to { transform: rotate(360deg); }
}

.bill-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.bill-header-card {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 24px;
  border-radius: 8px;
}

.bill-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.bill-no {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.bill-status {
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 4px;
}

.bill-status.unpaid {
  background: #fff7e6;
  color: #fa8c16;
}

.bill-status.paid {
  background: #f6ffed;
  color: #52c41a;
}

.bill-status.overdue {
  background: #fff2f0;
  color: #ff4d4f;
}

.house-title {
  font-size: 20px;
  font-weight: 500;
  color: #262626;
  margin-bottom: 4px;
}

.house-address {
  font-size: 14px;
  color: #8c8c8c;
}

.bill-info-section {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
  color: #262626;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.section-title i {
  color: #94a3b8;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 13px;
  color: #8c8c8c;
}

.info-value {
  font-size: 14px;
  color: #262626;
}

.info-value.highlight {
  font-size: 18px;
  font-weight: 600;
  color: #1890ff;
}

.bill-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 16px;
}

.bill-actions .el-button {
  padding: 10px 24px;
}
</style>