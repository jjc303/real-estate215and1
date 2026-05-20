<template>
  <div class="bills-page">
    <!-- 租客端视图 -->
    <template v-if="isTenant">
      <div class="page-header">
        <div class="header-left">
          <h2>我的账单</h2>
          <p class="subtitle">管理我的租金账单</p>
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
    </template>

    <!-- 房东端视图 -->
    <template v-else>
      <div class="page-header">
        <div class="header-left">
          <h2>账单管理</h2>
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
          <span v-if="getTabCount(tab.value) > 0" class="tab-badge">{{ getTabCount(tab.value) }}</span>
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
            
            <div class="bill-tenant">
              <i class="fa-solid fa-user"></i>
              <span>租客：{{ bill.tenant_name }}</span>
            </div>
            
            <div class="bill-period">
              <i class="fa-solid fa-calendar-days"></i>
              <span>账期：{{ bill.period }}</span>
            </div>
            
            <div class="bill-price">
              <span class="price-label">应收金额：</span>
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
            <el-button link @click.stop="viewDetail(bill)">
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
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import Pagination from '@/components/Pagination.vue'
import service from '@/utils/request'
import { useUserStore } from '@/stores/user'
import { mockTenantBills, mockLandlordBills } from '@/mock/bills'

const userStore = useUserStore()

const USE_MOCK_DATA = true

const loading = ref(false)
const currentTab = ref('all')
const pageNum = ref(1)
const pageSize = ref(10)
const total = ref(0)
const bills = ref([])

// 判断当前用户是否是租客
const isTenant = computed(() => userStore.userRole === 'tenant')

// 标签列表
const tabs = [
  { label: '全部', value: 'all' },
  { label: '待支付', value: 'unpaid' },
  { label: '已支付', value: 'paid' },
  { label: '已逾期', value: 'overdue' }
]

const filteredBills = computed(() => {
  if (currentTab.value === 'all') {
    return bills.value
  }
  return bills.value.filter(bill => bill.status === currentTab.value)
})

const getTabCount = (status) => {
  if (status === 'all') return bills.value.length
  return bills.value.filter(b => b.status === status).length
}

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
      // 根据角色使用不同的模拟数据
      const currentMockData = isTenant.value ? mockTenantBills : mockLandlordBills
      const start = (pageNum.value - 1) * pageSize.value
      const end = start + pageSize.value
      bills.value = currentMockData.slice(start, end)
      total.value = currentMockData.length
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
      // 根据角色使用不同的模拟数据
      const currentMockData = isTenant.value ? mockTenantBills : mockLandlordBills
      const idx = currentMockData.findIndex(b => b.id === bill.id)
      if (idx !== -1) {
        currentMockData[idx].status = 'paid'
        currentMockData[idx].paid_date = new Date().toISOString().split('T')[0]
      }
      ElMessage.success(`账单 #${bill.id} 支付成功！`)
      fetchBills()
    } else {
      const res = await service.post('/v1/payments', {
        bill_id: bill.id,
        amount: bill.amount,
        payment_method: 'mock',
        remark: '在线支付'
      })
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

.header-left {
  display: flex;
  flex-direction: column;
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

.bills-list {
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

.bill-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 15px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.bill-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
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
  display: flex;
  align-items: center;
}

.bill-actions .el-button {
  margin-left: 8px;
}
</style>