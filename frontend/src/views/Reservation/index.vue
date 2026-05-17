<template>
  <div class="reservation-page">
    <!-- 租客端视图 -->
    <template v-if="isTenant">
      <div class="page-header">
        <div class="header-left">
          <h2>我的预约</h2>
          <p class="subtitle">管理我的看房预约</p>
        </div>
        <div class="header-right">
          <el-button type="primary" @click="showCreateDialog">
            <i class="fa-solid fa-plus"></i> 发起预约
          </el-button>
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

      <div class="reservation-list">
        <div v-if="loading" class="loading">加载中...</div>
        
        <div v-else-if="filteredReservations.length === 0" class="empty">
          暂无{{ currentTab === 'all' ? '' : tenantTabs.find(t => t.value === currentTab)?.label }}预约
        </div>

        <div 
          v-for="reservation in filteredReservations" 
          :key="reservation.id"
          class="reservation-card"
        >
          <div class="reservation-info">
            <div class="reservation-title">
              <span class="house-title">{{ reservation.house_title }}</span>
              <span class="reservation-status" :class="reservation.status">{{ getStatusText(reservation.status) }}</span>
            </div>
            
            <div class="reservation-details">
              <div class="detail-item">
                <i class="fa-solid fa-home"></i>
                <span>{{ reservation.house_address }}</span>
              </div>
              <div class="detail-item">
                <i class="fa-solid fa-user"></i>
                <span>房东：{{ reservation.landlord_name }}</span>
              </div>
              <div class="detail-item">
                <i class="fa-solid fa-phone"></i>
                <span>{{ reservation.landlord_phone }}</span>
              </div>
              <div class="detail-item">
                <i class="fa-solid fa-calendar"></i>
                <span>{{ reservation.reservation_date }}</span>
              </div>
              <div class="detail-item">
                <i class="fa-solid fa-clock"></i>
                <span>{{ reservation.reservation_time }}</span>
              </div>
            </div>
            
            <div class="reservation-remark" v-if="reservation.remark">
              <i class="fa-solid fa-message-circle"></i>
              <span>{{ reservation.remark }}</span>
            </div>
          </div>
          
          <div class="reservation-actions">
            <el-button 
              v-if="reservation.status === 'pending'"
              type="danger"
              size="small"
              @click="cancelReservation(reservation)"
            >
              <i class="fa-solid fa-xmark"></i> 取消预约
            </el-button>
            <el-button 
              type="primary"
              size="small"
              @click="viewDetail(reservation)"
            >
              <i class="fa-solid fa-eye"></i> 查看详情
            </el-button>
          </div>
        </div>
      </div>
    </template>

    <!-- 房东端视图 -->
    <template v-else>
      <div class="page-header">
        <div class="header-left">
          <h2>预约管理</h2>
          <p class="subtitle">管理看房预约</p>
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

      <div class="reservation-list">
        <div v-if="loading" class="loading">加载中...</div>
        
        <div v-else-if="filteredReservations.length === 0" class="empty">
          暂无{{ currentTab === 'all' ? '' : landlordTabs.find(t => t.value === currentTab)?.label }}预约
        </div>

        <div 
          v-for="reservation in filteredReservations" 
          :key="reservation.id"
          class="reservation-card"
        >
          <div class="reservation-info">
            <div class="reservation-title">
              <span class="house-title">{{ reservation.house_title }}</span>
              <span class="reservation-status" :class="reservation.status">{{ getStatusText(reservation.status) }}</span>
            </div>
            
            <div class="reservation-details">
              <div class="detail-item">
                <i class="fa-solid fa-user"></i>
                <span>{{ reservation.tenant_name }}</span>
              </div>
              <div class="detail-item">
                <i class="fa-solid fa-phone"></i>
                <span>{{ reservation.phone }}</span>
              </div>
              <div class="detail-item">
                <i class="fa-solid fa-calendar"></i>
                <span>{{ reservation.reservation_date }}</span>
              </div>
              <div class="detail-item">
                <i class="fa-solid fa-clock"></i>
                <span>{{ reservation.reservation_time }}</span>
              </div>
            </div>
            
            <div class="reservation-remark" v-if="reservation.remark">
              <i class="fa-solid fa-message-circle"></i>
              <span>{{ reservation.remark }}</span>
            </div>
          </div>
          
          <div class="reservation-actions">
            <el-button 
              v-if="reservation.status === 'pending'"
              type="success"
              size="small"
              @click="confirmReservation(reservation)"
            >
              <i class="fa-solid fa-check"></i> 确认预约
            </el-button>
            <el-button 
              v-if="reservation.status === 'pending'"
              type="danger"
              size="small"
              @click="rejectReservation(reservation)"
            >
              <i class="fa-solid fa-times"></i> 拒绝预约
            </el-button>
            <el-button 
              type="primary"
              size="small"
              @click="viewDetail(reservation)"
            >
              <i class="fa-solid fa-eye"></i> 查看详情
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

    <!-- 发起预约对话框 -->
    <el-dialog
      v-if="isTenant"
      title="发起预约"
      :visible.sync="dialogVisible"
      width="500px"
    >
      <el-form :model="reservationForm" label-width="80px">
        <el-form-item label="选择房源">
          <el-select v-model="reservationForm.house_id" placeholder="请选择房源" style="width: 100%">
            <el-option 
              v-for="house in availableHouses" 
              :key="house.id" 
              :label="house.title" 
              :value="house.id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="预约日期">
          <el-date-picker 
            v-model="reservationForm.appointment_date" 
            type="date" 
            placeholder="请选择日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="预约时间">
          <el-time-picker 
            v-model="reservationForm.appointment_time" 
            placeholder="请选择时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input 
            v-model="reservationForm.remark" 
            type="textarea" 
            placeholder="请输入备注（可选）"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReservation">提交预约</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import Pagination from '@/components/Pagination.vue'
import service from '@/utils/request'
import { useUserStore } from '@/stores/user'
import { mockTenantReservations, mockLandlordReservations } from '@/mock/reservation'

const userStore = useUserStore()

// 是否开启模拟数据
const USE_MOCK_DATA = true

const loading = ref(false)
const currentTab = ref('all')
const pageNum = ref(1)
const pageSize = ref(10)
const total = ref(0)
const reservations = ref([])

// 发起预约相关
const dialogVisible = ref(false)
const availableHouses = ref([])
const reservationForm = ref({
  house_id: '',
  appointment_date: '',
  appointment_time: '',
  remark: ''
})

// 判断当前用户是否是租客
const isTenant = computed(() => userStore.userRole === 'tenant')

// 租客端标签
const tenantTabs = [
  { label: '全部', value: 'all' },
  { label: '待确认', value: 'pending' },
  { label: '已确认', value: 'confirmed' },
  { label: '已取消', value: 'cancelled' },
  { label: '已完成', value: 'completed' }
]

// 房东端标签
const landlordTabs = [
  { label: '全部', value: 'all' },
  { label: '待确认', value: 'pending' },
  { label: '已确认', value: 'confirmed' },
  { label: '已拒绝', value: 'rejected' },
  { label: '已完成', value: 'completed' }
]

// 当前使用的标签列表
const currentTabs = computed(() => isTenant.value ? tenantTabs : landlordTabs)

const filteredReservations = computed(() => {
  if (currentTab.value === 'all') {
    return reservations.value
  }
  return reservations.value.filter(r => r.status === currentTab.value)
})

const getTabCount = (status) => {
  if (status === 'all') return reservations.value.length
  return reservations.value.filter(r => r.status === status).length
}

const getStatusText = (status) => {
  const map = {
    pending: '待确认',
    confirmed: '已确认',
    rejected: '已拒绝',
    cancelled: '已取消',
    completed: '已完成'
  }
  return map[status] || status
}

const fetchReservations = async () => {
  loading.value = true
  
  try {
    if (USE_MOCK_DATA) {
      // 根据角色使用不同的模拟数据
      const currentMockData = isTenant.value ? mockTenantReservations : mockLandlordReservations
      const start = (pageNum.value - 1) * pageSize.value
      const end = start + pageSize.value
      reservations.value = currentMockData.slice(start, end)
      total.value = currentMockData.length
    } else {
      const params = {
        page: pageNum.value,
        page_size: pageSize.value
      }
      
      const res = await service.get('/v1/appointments', { params })
      
      if (res.code === 0) {
        reservations.value = res.data.list
        total.value = res.data.total
      }
    }
  } catch (e) {
    ElMessage.error('加载预约列表失败')
    console.error(e)
  } finally {
    loading.value = false
  }
}

const confirmReservation = async (reservation) => {
  try {
    if (USE_MOCK_DATA) {
      // 模拟确认预约 - 使用房东端数据
      const idx = mockLandlordReservations.findIndex(r => r.id === reservation.id)
      if (idx !== -1) {
        mockLandlordReservations[idx].status = 'confirmed'
      }
      ElMessage({
        type: 'success',
        message: `预约确认成功！\n租客：${reservation.tenant_name}\n时间：${reservation.reservation_date} ${reservation.reservation_time}`,
        duration: 3000
      })
      fetchReservations()
    } else {
      const res = await service.patch(`/v1/appointments/${reservation.id}/confirm`)
      if (res.code === 0) {
        ElMessage({
          type: 'success',
          message: `预约确认成功！\n租客：${reservation.tenant_name}\n时间：${reservation.reservation_date} ${reservation.reservation_time}`,
          duration: 3000
        })
        fetchReservations()
      }
    }
  } catch (e) {
    ElMessage.error('确认失败，请稍后重试')
    console.error(e)
  }
}

const rejectReservation = async (reservation) => {
  try {
    await ElMessageBox.confirm(
      `确定要拒绝 ${reservation.tenant_name} 的预约吗？\n房源：${reservation.house_title}\n时间：${reservation.reservation_date} ${reservation.reservation_time}`,
      '确认拒绝',
      {
        confirmButtonText: '拒绝预约',
        cancelButtonText: '再想想',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    if (USE_MOCK_DATA) {
      // 模拟拒绝预约 - 使用房东端数据
      const idx = mockLandlordReservations.findIndex(r => r.id === reservation.id)
      if (idx !== -1) {
        mockLandlordReservations[idx].status = 'rejected'
      }
      ElMessage({
        type: 'info',
        message: `已拒绝 ${reservation.tenant_name} 的预约申请`,
        duration: 2500
      })
      fetchReservations()
    } else {
      const res = await service.patch(`/v1/appointments/${reservation.id}/reject`)
      if (res.code === 0) {
        ElMessage({
          type: 'info',
          message: `已拒绝 ${reservation.tenant_name} 的预约申请`,
          duration: 2500
        })
        fetchReservations()
      }
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('操作失败，请稍后重试')
      console.error(e)
    }
  }
}

const cancelReservation = async (reservation) => {
  try {
    await ElMessageBox.confirm(
      `确定要取消预约吗？\n房源：${reservation.house_title}\n时间：${reservation.reservation_date} ${reservation.reservation_time}`,
      '确认取消',
      {
        confirmButtonText: '取消预约',
        cancelButtonText: '再想想',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    if (USE_MOCK_DATA) {
      // 模拟取消预约 - 使用租客端数据
      const idx = mockTenantReservations.findIndex(r => r.id === reservation.id)
      if (idx !== -1) {
        mockTenantReservations[idx].status = 'cancelled'
      }
      ElMessage({
        type: 'info',
        message: '预约已取消',
        duration: 2500
      })
      fetchReservations()
    } else {
      const res = await service.patch(`/v1/appointments/${reservation.id}/cancel`)
      if (res.code === 0) {
        ElMessage({
          type: 'info',
          message: '预约已取消',
          duration: 2500
        })
        fetchReservations()
      }
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('操作失败，请稍后重试')
      console.error(e)
    }
  }
}

const viewDetail = (reservation) => {
  // 可以跳转到详情页
  console.log('查看详情:', reservation)
}

const handlePageChange = (newPage) => {
  pageNum.value = newPage
  fetchReservations()
}

// 模拟房源数据
const mockHouses = [
  { id: 1, title: '中南大学14舍' },
  { id: 2, title: '麓山南路88号' },
  { id: 3, title: '天马小区3栋' },
  { id: 4, title: '阳光公寓A座' },
  { id: 5, title: '河西王府井小区' }
]

const fetchAvailableHouses = async () => {
  if (USE_MOCK_DATA) {
    availableHouses.value = mockHouses
  } else {
    try {
      const res = await service.get('/v1/houses', { params: { page: 1, page_size: 20 } })
      if (res.code === 0) {
        availableHouses.value = res.data.list.map(h => ({ id: h.id, title: h.title }))
      }
    } catch (e) {
      console.error('获取房源列表失败', e)
      availableHouses.value = mockHouses
    }
  }
}

const showCreateDialog = () => {
  fetchAvailableHouses()
  reservationForm.value = {
    house_id: '',
    appointment_date: '',
    appointment_time: '',
    remark: ''
  }
  dialogVisible.value = true
}

const submitReservation = async () => {
  if (!reservationForm.value.house_id) {
    ElMessage.warning('请选择房源')
    return
  }
  if (!reservationForm.value.appointment_date) {
    ElMessage.warning('请选择预约日期')
    return
  }
  if (!reservationForm.value.appointment_time) {
    ElMessage.warning('请选择预约时间')
    return
  }

  try {
    if (USE_MOCK_DATA) {
      const newReservation = {
        id: mockTenantReservations.length + 1,
        house_id: reservationForm.value.house_id,
        house_title: availableHouses.value.find(h => h.id === reservationForm.value.house_id)?.title || '',
        house_address: '测试地址',
        landlord_name: '测试房东',
        landlord_phone: '13800138000',
        reservation_date: reservationForm.value.appointment_date,
        reservation_time: reservationForm.value.appointment_time,
        remark: reservationForm.value.remark,
        status: 'pending',
        created_at: new Date().toLocaleString()
      }
      mockTenantReservations.unshift(newReservation)
      dialogVisible.value = false
      ElMessage.success('预约发起成功！请等待房东确认')
      fetchReservations()
    } else {
      const appointmentTime = `${reservationForm.value.appointment_date}T${reservationForm.value.appointment_time}`
      const res = await service.post('/v1/appointments', {
        house_id: reservationForm.value.house_id,
        appointment_time: appointmentTime,
        remark: reservationForm.value.remark || null
      })
      if (res.code === 0) {
        dialogVisible.value = false
        ElMessage.success('预约发起成功！请等待房东确认')
        fetchReservations()
      }
    }
  } catch (e) {
    ElMessage.error('发起预约失败，请稍后重试')
    console.error(e)
  }
}

onMounted(() => {
  fetchReservations()
})
</script>

<style scoped>
.reservation-page {
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

.reservation-list {
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

.reservation-card {
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

.reservation-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.reservation-info {
  flex: 1;
  min-width: 0;
}

.reservation-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.house-title {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
}

.reservation-status {
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 3px;
}

.reservation-status.pending {
  background: #fff7e6;
  color: #fa8c16;
}

.reservation-status.confirmed {
  background: #f6ffed;
  color: #52c41a;
}

.reservation-status.rejected {
  background: #fff2f0;
  color: #ff4d4f;
}

.reservation-status.completed {
  background: #f5f5f5;
  color: #8c8c8c;
}

.reservation-status.cancelled {
  background: #e6f7ff;
  color: #1890ff;
}

.reservation-details {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 10px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #595959;
}

.detail-item i {
  color: #8c8c8c;
  width: 16px;
  text-align: center;
}

.reservation-remark {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 14px;
  color: #8c8c8c;
  padding-top: 10px;
  border-top: 1px dashed #f0f0f0;
}

.reservation-remark i {
  margin-top: 2px;
}

.reservation-actions {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: 20px;
}

.reservation-actions .el-button {
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: normal;
}

.reservation-actions .el-button--success {
  background: #69c0ff !important;
  border-color: #69c0ff !important;
  color: #fff !important;
}

.reservation-actions .el-button--danger {
  background: #ff7875 !important;
  border-color: #ff7875 !important;
  color: #fff !important;
}

.reservation-actions .el-button--primary {
  background: #f5f5f5 !important;
  border-color: #d9d9d9 !important;
  color: #666 !important;
}

.reservation-actions .el-button--primary:hover {
  background: #e8e8e8 !important;
}

@media (max-width: 768px) {
  .reservation-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .reservation-actions {
    margin-left: 0;
    width: 100%;
    justify-content: flex-end;
  }
  
  .reservation-details {
    gap: 12px;
  }
}
</style>
