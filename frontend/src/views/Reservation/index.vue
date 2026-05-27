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
          <div class="empty-icon"><i class="fa-solid fa-calendar-check"></i></div>
          <p class="empty-text">暂无{{ currentTab === 'all' ? '' : tenantTabs.find(t => t.value === currentTab)?.label }}预约</p>
          <p class="empty-hint">看房预约会在这里显示</p>
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
          <div class="empty-icon"><i class="fa-solid fa-calendar-check"></i></div>
          <p class="empty-text">暂无{{ currentTab === 'all' ? '' : landlordTabs.find(t => t.value === currentTab)?.label }}预约</p>
          <p class="empty-hint">看房预约会在这里显示</p>
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
              v-if="reservation.status === 'confirmed'"
              type="primary"
              size="small"
              @click="createContract(reservation)"
            >
              <i class="fa-solid fa-file-signature"></i> 创建合同
            </el-button>
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
      v-model="dialogVisible"
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

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="预约详情"
      width="520px"
    >
      <div v-if="detailReservation" class="detail-content">
        <div class="detail-section">
          <div class="detail-section-title">
            <i class="fa-solid fa-home"></i> 房源信息
          </div>
          <div class="detail-grid">
            <div class="detail-item-row">
              <span class="detail-label">房源名称</span>
              <span class="detail-value">{{ detailReservation.house_title }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">房源地址</span>
              <span class="detail-value">{{ detailReservation.house_address }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <div class="detail-section-title">
            <i class="fa-solid fa-calendar-check"></i> 预约信息
          </div>
          <div class="detail-grid">
            <div class="detail-item-row">
              <span class="detail-label">预约日期</span>
              <span class="detail-value">{{ detailReservation.reservation_date }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">预约时间</span>
              <span class="detail-value">{{ detailReservation.reservation_time }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">预约状态</span>
              <span class="detail-value">
                <span class="reservation-status" :class="detailReservation.status">{{ getStatusText(detailReservation.status) }}</span>
              </span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <div class="detail-section-title">
            <i class="fa-solid fa-user"></i> 联系信息
          </div>
          <div class="detail-grid">
            <div class="detail-item-row">
              <span class="detail-label">{{ isTenant ? '房东姓名' : '租客姓名' }}</span>
              <span class="detail-value">{{ isTenant ? detailReservation.landlord_name : detailReservation.tenant_name }}</span>
            </div>
            <div class="detail-item-row">
              <span class="detail-label">{{ isTenant ? '房东电话' : '租客电话' }}</span>
              <span class="detail-value">{{ isTenant ? detailReservation.landlord_phone : detailReservation.phone }}</span>
            </div>
          </div>
        </div>

        <div v-if="detailReservation.remark" class="detail-section">
          <div class="detail-section-title">
            <i class="fa-solid fa-message-circle"></i> 备注信息
          </div>
          <div class="detail-remark">{{ detailReservation.remark }}</div>
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
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import Pagination from '@/components/Pagination.vue'
import BackToTop from '@/components/BackToTop.vue'
import service from '@/utils/request'
import { useUserStore } from '@/stores/user'
import { mockTenantReservations, mockLandlordReservations } from '@/mock/reservation'

const userStore = useUserStore()
const router = useRouter()

// 是否开启模拟数据
const USE_MOCK_DATA = false // 停止使用模拟数据

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

// 查看详情相关
const detailDialogVisible = ref(false)
const detailReservation = ref(null)

// 格式化日期为 YYYY-MM-DD
const formatDate = (date) => {
  if (!date) return ''
  if (date instanceof Date) {
    return date.toISOString().split('T')[0]
  }
  // 如果是字符串，尝试解析
  const d = new Date(date)
  if (!isNaN(d.getTime())) {
    return d.toISOString().split('T')[0]
  }
  return date
}

// 格式化时间为 HH:MM:SS
const formatTime = (time) => {
  if (!time) return ''
  if (time instanceof Date) {
    return time.toTimeString().split(' ')[0]
  }
  // 如果是字符串，尝试解析
  const d = new Date(`1970-01-01T${time}`)
  if (!isNaN(d.getTime())) {
    return d.toTimeString().split(' ')[0]
  }
  return time
}

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
      
      console.log('===== 预约列表响应 =====')
      console.log('响应数据:', res)
      
      if (res.code === 0) {
        // 将后端返回的数据结构转换为前端期望的格式
        reservations.value = res.data.list.map(item => ({
          id: item.id,
          house_id: item.house_id,
          house_title: item.house?.title || '未知房源',
          house_address: item.house?.address || '未知地址',
          landlord_name: item.landlord_name || item.landlord_id || '未知房东',
          landlord_phone: item.landlord_phone || '未知电话',
          tenant_name: item.tenant_name || item.tenant_id || '未知租客',
          phone: item.tenant_phone || '未知电话',
          remark: item.remark || '',
          status: item.status,
          // 将 appointment_time 拆分为日期和时间
          reservation_date: formatDate(item.appointment_time),
          reservation_time: formatTime(item.appointment_time)
        }))
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
      ElMessage.success('预约确认成功！')
      fetchReservations()
    } else {
      const res = await service.patch(`/v1/appointments/${reservation.id}/confirm`)
      if (res.code === 0) {
        ElMessage.success('预约确认成功！')
        fetchReservations()
      }
    }
  } catch (e) {
    ElMessage.error('确认失败，请稍后重试')
    console.error(e)
  }
}

const createContract = (reservation) => {
  router.push({
    path: '/contracts',
    query: { create: '1', appointment_id: reservation.id }
  })
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
  detailReservation.value = reservation
  detailDialogVisible.value = true
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
      // 正确格式化日期和时间
      const dateStr = formatDate(reservationForm.value.appointment_date)
      const timeStr = formatTime(reservationForm.value.appointment_time)
      const appointmentTime = `${dateStr}T${timeStr}`
      
      // 调试信息
      console.log('===== 发起预约请求 =====')
      console.log('house_id:', reservationForm.value.house_id)
      console.log('appointment_date:', reservationForm.value.appointment_date)
      console.log('appointment_time:', appointmentTime)
      console.log('remark:', reservationForm.value.remark)
      
      const res = await service.post('/v1/appointments', {
        house_id: parseInt(reservationForm.value.house_id),
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

.reservation-list {
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
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transform: translateY(-3px);
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

.detail-remark {
  font-size: 14px;
  color: #595959;
  line-height: 1.6;
  padding: 10px 12px;
  background: #fafafa;
  border-radius: 6px;
}
</style>
