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
          <div class="empty-icon"><i class="fa-solid fa-file-invoice-dollar"></i></div>
          <p class="empty-text">暂无{{ currentTab === 'all' ? '' : tabs.find(t => t.value === currentTab)?.label }}账单</p>
          <p class="empty-hint">租金账单会在这里显示</p>
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
        <div class="header-right">
          <el-button type="primary" @click="openCreateDialog">
            <i class="fa-solid fa-plus"></i> 创建账单
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

      <div class="bills-list">
        <div v-if="loading" class="loading">加载中...</div>
        
        <div v-else-if="filteredBills.length === 0" class="empty">
          <div class="empty-icon"><i class="fa-solid fa-file-invoice-dollar"></i></div>
          <p class="empty-text">暂无{{ currentTab === 'all' ? '' : tabs.find(t => t.value === currentTab)?.label }}账单</p>
          <p class="empty-hint">租金账单会在这里显示</p>
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
            <el-button
              v-if="bill.status === 'unpaid'"
              type="danger"
              size="small"
              @click.stop="cancelBill(bill)"
            >
              <i class="fa-solid fa-ban"></i> 取消
            </el-button>
            <el-button
              v-if="bill.status === 'unpaid'"
              type="warning"
              size="small"
              @click.stop="markOverdue(bill)"
            >
              <i class="fa-solid fa-clock"></i> 标记逾期
            </el-button>
          </div>
        </div>
      </div>

      <Pagination 
        
        :pageNum="pageNum"
        :pageSize="pageSize"
        :total="total"
        @change="handlePageChange"
      />
    </template>

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="账单详情"
      width="520px"
    >
      <div v-if="detailBill" class="detail-content">
        <div class="detail-section">
          <div class="detail-section-title">
            <i class="fa-solid fa-file-invoice"></i> 账单信息
          </div>
          <div class="detail-grid">
            <div class="detail-item-row">
              <span class="detail-label">账单编号</span>
              <span class="detail-value">#{{ detailBill.id }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">账单状态</span>
              <span class="detail-value">
                <span class="bill-status" :class="detailBill.status">{{ getStatusText(detailBill.status) }}</span>
              </span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">账单账期</span>
              <span class="detail-value">{{ detailBill.period }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">应付金额</span>
              <span class="detail-value price">¥{{ detailBill.amount }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">到期时间</span>
              <span class="detail-value">{{ detailBill.due_date }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">支付时间</span>
              <span class="detail-value">{{ detailBill.paid_date || '-' }}</span>
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
              <span class="detail-value">{{ detailBill.house?.title }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">所在区域</span>
              <span class="detail-value">{{ detailBill.house?.region }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">详细地址</span>
              <span class="detail-value">{{ detailBill.house?.address }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <div class="detail-section-title">
            <i class="fa-solid fa-file-signature"></i> 关联信息
          </div>
          <div class="detail-grid">
            <div class="detail-item-row">
              <span class="detail-label">合同编号</span>
              <span class="detail-value">合同 #{{ detailBill.contract_id }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">{{ isTenant ? '房东' : '租客' }}</span>
              <span class="detail-value">{{ isTenant ? (detailBill.landlord_name || '未知') : detailBill.tenant_name }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">创建时间</span>
              <span class="detail-value">{{ formatDateTime(detailBill.created_at) }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">更新时间</span>
              <span class="detail-value">{{ formatDateTime(detailBill.updated_at) }}</span>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="createDialogVisible"
      title="创建账单"
      width="500px"
    >
      <el-form :model="createForm" label-width="90px">
        <el-form-item label="关联合同" required>
          <el-select
            v-model="createForm.contract_id"
            placeholder="请选择已生效的合同"
            style="width: 100%"
            @change="onContractChange"
          >
            <el-option
              v-for="c in activeContracts"
              :key="c.id"
              :label="`合同 #${c.id} ${c.house?.title || ''} — 租客ID:${c.tenant_id}`"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="账单类型" required>
          <el-select v-model="createForm.bill_type" placeholder="请选择账单类型" style="width: 100%">
            <el-option label="租金" value="rent" />
            <el-option label="押金" value="deposit" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="金额(元)" required>
          <el-input-number v-model="createForm.amount" :min="1" :precision="2" placeholder="请输入金额" style="width: 100%" />
        </el-form-item>
        <el-form-item label="到期日期" required>
          <el-date-picker v-model="createForm.due_date" type="date" value-format="YYYY-MM-DD" placeholder="选择到期日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="createForm.remark" type="textarea" :rows="2" placeholder="备注信息（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCreateBill">创建</el-button>
      </template>
    </el-dialog>

    <BackToTop />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import Pagination from '@/components/Pagination.vue'
import BackToTop from '@/components/BackToTop.vue'
import service from '@/utils/request'
import { useUserStore } from '@/stores/user'
import { mockTenantBills, mockLandlordBills } from '@/mock/bills'

const userStore = useUserStore()

const USE_MOCK_DATA = false

const loading = ref(false)
const currentTab = ref('all')
const pageNum = ref(1)
const pageSize = ref(10)
const total = ref(0)
const bills = ref([])

// 查看详情相关
const detailDialogVisible = ref(false)
const detailBill = ref(null)

// 创建账单相关
const createDialogVisible = ref(false)
const activeContracts = ref([])
const contractsLoading = ref(false)

const createForm = reactive({
  contract_id: null,
  bill_type: 'rent',
  amount: null,
  due_date: '',
  remark: ''
})

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

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  const date = new Date(datetime)
  return date.toLocaleString('zh-CN')
}

const formatPeriod = (dateStr) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return `${d.getFullYear()}年${d.getMonth() + 1}月`
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
        bills.value = res.data.list.map(item => ({
          ...item,
          house: {
            title: `房源 #${item.house_id}`,
            region: '-',
            address: '-'
          },
          period: formatPeriod(item.due_date || item.created_at),
          paid_date: null,
          tenant_name: `租客 #${item.tenant_id}`,
          landlord_name: `房东 #${item.landlord_id}`
        }))
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
  detailBill.value = bill
  detailDialogVisible.value = true
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
      } else {
        ElMessage.error(res.message || '支付失败')
      }
    }
  } catch (e) {
    if (e !== 'cancel' && e !== 'close') {
      ElMessage.error(e.response?.data?.message || '支付失败，请稍后重试')
      console.error(e)
    }
  }
}

const cancelBill = async (bill) => {
  try {
    await ElMessageBox.confirm(
      `确定要取消账单 #${bill.id} 吗？`,
      '确认取消',
      { confirmButtonText: '确认', cancelButtonText: '取消', type: 'warning' }
    )
    const res = await service.patch(`/v1/bills/${bill.id}/cancel`)
    if (res.code === 0) {
      ElMessage.success('账单已取消')
      fetchBills()
    } else {
      ElMessage.error(res.message || '取消失败')
    }
  } catch (e) {
    if (e !== 'cancel' && e !== 'close') {
      ElMessage.error(e.response?.data?.message || '取消失败，请稍后重试')
      console.error(e)
    }
  }
}

const markOverdue = async (bill) => {
  try {
    await ElMessageBox.confirm(
      `确定将账单 #${bill.id} 标记为逾期吗？`,
      '确认标记逾期',
      { confirmButtonText: '确认', cancelButtonText: '取消', type: 'warning' }
    )
    const res = await service.patch(`/v1/bills/${bill.id}/mark-overdue`)
    if (res.code === 0) {
      ElMessage.success('已标记为逾期')
      fetchBills()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch (e) {
    if (e !== 'cancel' && e !== 'close') {
      ElMessage.error(e.response?.data?.message || '操作失败，请稍后重试')
      console.error(e)
    }
  }
}

const handlePageChange = (newPage) => {
  pageNum.value = newPage
  fetchBills()
}

const fetchActiveContracts = async () => {
  contractsLoading.value = true
  try {
    const res = await service.get('/v1/contracts', { params: { page: 1, page_size: 100 } })
    if (res.code === 0) {
      activeContracts.value = res.data.list.filter(c => c.status === 'active' && c.landlord_id === userStore.userId)
    }
  } catch (e) {
    console.error('获取合同列表失败', e)
  } finally {
    contractsLoading.value = false
  }
}

const openCreateDialog = () => {
  createForm.contract_id = null
  createForm.bill_type = 'rent'
  createForm.amount = null
  createForm.due_date = ''
  createForm.remark = ''
  fetchActiveContracts()
  createDialogVisible.value = true
}

const onContractChange = (contractId) => {
  const contract = activeContracts.value.find(c => c.id === contractId)
  if (contract) {
    if (!createForm.amount) {
      createForm.amount = Number(contract.monthly_rent) || 0
    }
  }
}

const submitCreateBill = async () => {
  if (!createForm.contract_id) {
    ElMessage.warning('请选择关联合同')
    return
  }
  if (!createForm.bill_type) {
    ElMessage.warning('请选择账单类型')
    return
  }
  if (!createForm.amount || createForm.amount <= 0) {
    ElMessage.warning('请输入有效的金额')
    return
  }
  if (!createForm.due_date) {
    ElMessage.warning('请选择到期日期')
    return
  }

  try {
    const res = await service.post('/v1/bills', {
      contract_id: createForm.contract_id,
      bill_type: createForm.bill_type,
      amount: createForm.amount,
      due_date: createForm.due_date,
      remark: createForm.remark || null
    })
    if (res.code === 0) {
      ElMessage.success('账单创建成功')
      createDialogVisible.value = false
      pageNum.value = 1
      fetchBills()
    } else {
      ElMessage.error(res.message || '创建失败')
    }
  } catch (e) {
    console.error('创建账单失败', e)
    ElMessage.error(e.response?.data?.message || '创建失败，请稍后重试')
  }
}

onMounted(() => {
  fetchBills()
})
</script>

<style scoped>
.bills-page {
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
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transform: translateY(-3px);
}

.bill-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.bill-header {
  display: flex;
  align-items: center;
  gap: 12px;
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
}

.bill-period {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #595959;
}

.bill-tenant {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #595959;
}

.bill-tenant i {
  color: #94a3b8;
}

.bill-period i {
  color: #94a3b8;
}

.bill-price {
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
  font-size: 18px;
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