<template>
  <div class="reservation-page">
    <div class="page-header">
      <h2>预约管理</h2>
      <p class="subtitle">管理看房预约</p>
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

    <div class="reservation-list">
      <div v-if="loading" class="loading">加载中...</div>
      
      <div v-else-if="filteredReservations.length === 0" class="empty">
        暂无{{ currentTab === 'all' ? '' : tabs.find(t => t.value === currentTab)?.label }}预约
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
            v-if="reservation.status !== 'pending'"
            type="primary"
            size="small"
            @click="viewDetail(reservation)"
          >
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import Pagination from '@/components/Pagination.vue'
import service from '@/utils/request'

// 是否开启模拟数据
const USE_MOCK_DATA = true

const loading = ref(false)
const currentTab = ref('all')
const pageNum = ref(1)
const pageSize = ref(10)
const total = ref(0)
const reservations = ref([])

// 模拟数据
const mockReservations = [
  {
    id: 1,
    house_title: '中南大学14舍',
    tenant_name: '张三',
    phone: '138****1234',
    reservation_date: '2024-01-15',
    reservation_time: '14:00-16:00',
    remark: '想下午看房，希望能详细介绍一下周边环境',
    status: 'pending'
  },
  {
    id: 2,
    house_title: '麓山南路88号',
    tenant_name: '李四',
    phone: '139****5678',
    reservation_date: '2024-01-16',
    reservation_time: '10:00-12:00',
    remark: '',
    status: 'pending'
  },
  {
    id: 3,
    house_title: '天马小区3栋',
    tenant_name: '王五',
    phone: '137****9012',
    reservation_date: '2024-01-14',
    reservation_time: '09:00-11:00',
    remark: '已确认看房时间',
    status: 'confirmed'
  },
  {
    id: 4,
    house_title: '阳光公寓A座',
    tenant_name: '赵六',
    phone: '136****3456',
    reservation_date: '2024-01-13',
    reservation_time: '15:00-17:00',
    remark: '租客临时有事取消',
    status: 'rejected'
  },
  {
    id: 5,
    house_title: '望月湖小区',
    tenant_name: '钱七',
    phone: '135****7890',
    reservation_date: '2024-01-10',
    reservation_time: '14:00-16:00',
    remark: '',
    status: 'completed'
  },
  {
    id: 6,
    house_title: '溁湾镇地铁口',
    tenant_name: '孙八',
    phone: '134****2345',
    reservation_date: '2024-01-17',
    reservation_time: '11:00-13:00',
    remark: '周末有空，希望能尽快安排',
    status: 'pending'
  },
  {
    id: 7,
    house_title: '左家垅小区',
    tenant_name: '周九',
    phone: '133****6789',
    reservation_date: '2024-01-12',
    reservation_time: '16:00-18:00',
    remark: '',
    status: 'completed'
  },
  {
    id: 8,
    house_title: '王家湾步步高',
    tenant_name: '吴十',
    phone: '132****0123',
    reservation_date: '2024-01-18',
    reservation_time: '10:00-12:00',
    remark: '想看看房子的采光情况',
    status: 'pending'
  }
]

const tabs = [
  { label: '全部', value: 'all' },
  { label: '待确认', value: 'pending' },
  { label: '已确认', value: 'confirmed' },
  { label: '已拒绝', value: 'rejected' },
  { label: '已完成', value: 'completed' }
]

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
    completed: '已完成'
  }
  return map[status] || status
}

const fetchReservations = async () => {
  loading.value = true
  
  try {
    if (USE_MOCK_DATA) {
      // 使用模拟数据
      const start = (pageNum.value - 1) * pageSize.value
      const end = start + pageSize.value
      reservations.value = mockReservations.slice(start, end)
      total.value = mockReservations.length
    } else {
      const params = {
        page: pageNum.value,
        page_size: pageSize.value
      }
      
      const res = await service.get('/v1/reservations', { params })
      
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
      // 模拟确认预约
      const idx = mockReservations.findIndex(r => r.id === reservation.id)
      if (idx !== -1) {
        mockReservations[idx].status = 'confirmed'
      }
      ElMessage({
        type: 'success',
        message: `预约确认成功！\n租客：${reservation.tenant_name}\n时间：${reservation.reservation_date} ${reservation.reservation_time}`,
        duration: 3000
      })
      fetchReservations()
    } else {
      const res = await service.patch(`/v1/reservations/${reservation.id}/confirm`)
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
      // 模拟拒绝预约
      const idx = mockReservations.findIndex(r => r.id === reservation.id)
      if (idx !== -1) {
        mockReservations[idx].status = 'rejected'
      }
      ElMessage({
        type: 'info',
        message: `已拒绝 ${reservation.tenant_name} 的预约申请`,
        duration: 2500
      })
      fetchReservations()
    } else {
      const res = await service.patch(`/v1/reservations/${reservation.id}/reject`)
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

const viewDetail = (reservation) => {
  // 可以跳转到详情页
  console.log('查看详情:', reservation)
}

const handlePageChange = (newPage) => {
  pageNum.value = newPage
  fetchReservations()
}

onMounted(() => {
  fetchReservations()
})
</script>

<style scoped>
.reservation-page {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
  background: #fff;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
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

.reservation-list {
  display: flex;
  flex-direction: column;
}

.loading, .empty {
  text-align: center;
  padding: 60px;
  color: #8c8c8c;
}

.reservation-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #fff;
  margin-bottom: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  border-radius: 8px;
  border: 1px solid #f0f0f0;
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
