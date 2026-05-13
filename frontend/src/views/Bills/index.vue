<template>
  <div class="bills-page">
    <div class="page-header">
      <div class="header-left">
        <h2>租金监控</h2>
        <p class="subtitle">管理您的租金账单</p>
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

    <div class="bills-list">
      <div v-if="loading" class="loading">加载中...</div>
      
      <div v-else-if="filteredBills.length === 0" class="empty">
        暂无{{ currentTab === 'all' ? '' : tabs.find(t => t.value === currentTab)?.label }}账单
      </div>

      <div 
        v-for="bill in filteredBills" 
        :key="bill.id"
        class="bill-card"
        @click="viewDetail(bill)"
      >
        <div class="bill-info">
          <div class="bill-header">
            <span class="bill-no">账单 #{{ bill.id }}</span>
            <span class="bill-status" :class="bill.status">{{ getStatusText(bill.status) }}</span>
          </div>
          
          <div class="bill-title">{{ bill.house?.title }}</div>
          
          <div class="bill-period">
            <i class="fa-solid fa-calendar-days"></i>
            <span>账期：{{ bill.period }}</span>
          </div>
          
          <div class="bill-price">
            <span class="price-label">应付金额：</span>
            <span class="price-value">¥{{ bill.amount }}</span>
          </div>
          
          <div class="bill-dates">
            <div class="date-item">
              <i class="fa-solid fa-clock"></i>
              <span>到期时间：{{ bill.due_date }}</span>
            </div>
            <div v-if="bill.paid_date" class="date-item">
              <i class="fa-solid fa-check-circle"></i>
              <span>支付时间：{{ bill.paid_date }}</span>
            </div>
          </div>
        </div>
        
        <div class="bill-actions">
          <el-button 
            v-if="bill.status === 'unpaid'" 
            type="primary" 
            size="small"
            @click.stop="payBill(bill)"
          >
            <i class="fa-solid fa-credit-card"></i> 立即支付
          </el-button>
          <el-button 
            v-if="bill.status === 'paid'" 
            type="success" 
            size="small"
            disabled
          >
            <i class="fa-solid fa-check"></i> 已支付
          </el-button>
          <el-button 
            v-if="bill.status === 'overdue'" 
            type="danger" 
            size="small"
            @click.stop="payBill(bill)"
          >
            <i class="fa-solid fa-exclamation-circle"></i> 逾期支付
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
const bills = ref([])

const tabs = [
  { label: '全部', value: 'all' },
  { label: '待支付', value: 'unpaid' },
  { label: '已支付', value: 'paid' },
  { label: '已逾期', value: 'overdue' }
]

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
      address: '麓山南路100号'
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
      address: '麓山南路100号'
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
      address: '天马小区3栋'
    }
  },
  {
    id: 4,
    contract_id: 3,
    house_id: 3,
    tenant_id: 6,
    landlord_id: 7,
    period: '2024年1月',
    amount: '2800.00',
    status: 'paid',
    due_date: '2024-01-08',
    paid_date: '2024-01-06',
    created_at: '2024-01-01T00:00:00',
    updated_at: '2024-01-06T15:00:00',
    house: {
      id: 3,
      title: '左家垅小区',
      region: '岳麓区',
      address: '左家垅小区'
    }
  },
  {
    id: 5,
    contract_id: 4,
    house_id: 4,
    tenant_id: 8,
    landlord_id: 9,
    period: '2024年2月',
    amount: '4200.00',
    status: 'unpaid',
    due_date: '2024-02-12',
    paid_date: null,
    created_at: '2024-02-01T00:00:00',
    updated_at: '2024-02-01T00:00:00',
    house: {
      id: 4,
      title: '阳光公寓A座',
      region: '雨花区',
      address: '阳光公寓A座'
    }
  },
  {
    id: 6,
    contract_id: 2,
    house_id: 2,
    tenant_id: 4,
    landlord_id: 5,
    period: '2024年2月',
    amount: '3500.00',
    status: 'unpaid',
    due_date: '2024-02-15',
    paid_date: null,
    created_at: '2024-02-01T00:00:00',
    updated_at: '2024-02-01T00:00:00',
    house: {
      id: 2,
      title: '天马小区3栋',
      region: '岳麓区',
      address: '天马小区3栋'
    }
  }
]

const filteredBills = computed(() => {
  if (currentTab.value === 'all') {
    return bills.value
  }
  return bills.value.filter(bill => bill.status === currentTab.value)
})

const getStatusText = (status) => {
  const map = {
    unpaid: '待支付',
    paid: '已支付',
    overdue: '已逾期'
  }
  return map[status] || status
}

const fetchBills = async () => {
  loading.value = true
  try {
    if (USE_MOCK_DATA) {
      const start = (pageNum.value - 1) * pageSize.value
      const end = start + pageSize.value
      bills.value = mockBills.slice(start, end)
      total.value = mockBills.length
    } else {
      const params = {
        page: pageNum.value,
        page_size: pageSize.value
      }
      const res = await service.get('/v1/bills', { params })
      if (res.code === 0) {
        bills.value = res.data.list
        total.value = res.data.total
      }
    }
  } catch (e) {
    ElMessage.error('加载账单列表失败')
    console.error(e)
  } finally {
    loading.value = false
  }
}

const viewDetail = (bill) => {
  window.location.href = `/bills/detail/${bill.id}`
}

const payBill = async (bill) => {
  try {
    await ElMessageBox.confirm(
      `确定要支付账单吗？\n账单 #${bill.id}\n房源：${bill.house?.title}\n金额：¥${bill.amount}`,
      '确认支付',
      {
        confirmButtonText: '确认支付',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    if (USE_MOCK_DATA) {
      const idx = mockBills.findIndex(b => b.id === bill.id)
      if (idx !== -1) {
        mockBills[idx].status = 'paid'
        mockBills[idx].paid_date = new Date().toISOString().split('T')[0]
      }
      ElMessage.success(`账单 #${bill.id} 支付成功！`)
      fetchBills()
    } else {
      const res = await service.patch(`/v1/bills/${bill.id}/pay`)
      if (res.code === 0) {
        ElMessage.success(`账单 #${bill.id} 支付成功！`)
        fetchBills()
      }
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('支付失败，请稍后重试')
      console.error(e)
    }
  }
}

const handlePageChange = (newPage) => {
  pageNum.value = newPage
  fetchBills()
}

onMounted(() => {
  fetchBills()
})
</script>

<style scoped>
.bills-page {
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

.header-left {
  display: flex;
  flex-direction: column;
}

.page-header h2 {
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

.bills-list {
  display: flex;
  flex-direction: column;
}

.loading, .empty {
  text-align: center;
  padding: 40px;
  color: #8c8c8c;
}

.bill-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  margin-bottom: 12px;
  transition: all 0.2s;
  cursor: pointer;
}

.bill-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.bill-info {
  flex: 1;
}

.bill-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.bill-no {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
}

.bill-status {
  font-size: 12px;
  padding: 2px 8px;
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

.bill-title {
  font-size: 16px;
  font-weight: 500;
  color: #262626;
  margin-bottom: 8px;
}

.bill-period {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #595959;
  margin-bottom: 8px;
}

.bill-period i {
  color: #94a3b8;
}

.bill-price {
  margin-bottom: 8px;
}

.price-label {
  font-size: 14px;
  color: #595959;
}

.price-value {
  font-size: 18px;
  font-weight: 600;
  color: #1890ff;
}

.bill-dates {
  display: flex;
  gap: 20px;
}

.date-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #8c8c8c;
}

.date-item i {
  color: #94a3b8;
}

.bill-actions {
  flex-shrink: 0;
}

.bill-actions .el-button {
  margin-left: 8px;
}
</style>