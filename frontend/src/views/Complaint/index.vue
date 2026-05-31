<template>
  <div class="complaint-page">
    <div class="page-header">
      <div class="header-left">
        <h2>投诉管理</h2>
        <p class="subtitle">提交和管理您的投诉</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showComplaintDialog">
          <i class="fa-solid fa-plus"></i> 提交投诉
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

    <div class="complaint-list">
      <div v-if="loading" class="loading">加载中...</div>
      
      <div v-else-if="filteredComplaints.length === 0" class="empty">
        <div class="empty-icon"><i class="fa-solid fa-comment-dots"></i></div>
        <p class="empty-text">暂无{{ currentTab === 'all' ? '' : tabs.find(t => t.value === currentTab)?.label }}投诉建议</p>
        <p class="empty-hint">投诉建议记录会在这里显示</p>
      </div>

      <div 
        v-for="complaint in filteredComplaints" 
        :key="complaint.id"
        class="complaint-card"
        @click="viewDetail(complaint)"
      >
        <div class="complaint-info">
          <div class="complaint-header">
            <span class="complaint-no">投诉 #{{ complaint.id }}</span>
            <span class="complaint-status" :class="complaint.status">{{ getStatusText(complaint.status) }}</span>
          </div>
          
          <div class="complaint-title">{{ complaint.description.length > 50 ? complaint.description.substring(0, 50) + '...' : complaint.description }}</div>
          
          <div class="complaint-house">
            <i class="fa-solid fa-home"></i>
            <span>合同ID：#{{ complaint.contract_id }}</span>
          </div>
          
          <div class="complaint-desc">
            <i class="fa-solid fa-file-text"></i>
            <span>{{ complaint.description }}</span>
          </div>
          
          <div class="complaint-dates">
            <div class="date-item">
              <i class="fa-solid fa-clock"></i>
              <span>提交时间：{{ formatDate(complaint.created_at) }}</span>
            </div>
            <div v-if="complaint.processed_at" class="date-item">
              <i class="fa-solid fa-check-circle"></i>
              <span>处理时间：{{ formatDate(complaint.processed_at) }}</span>
            </div>
          </div>
        </div>
        
        <div class="complaint-actions">
          <el-button link @click.stop="viewDetail(complaint)">
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

    <el-dialog
      v-model="detailDialogVisible"
      title="投诉详情"
      width="600px"
    >
      <div v-if="selectedComplaint" class="detail-content">
        <div class="detail-row">
          <span class="detail-label">投诉编号</span>
          <span class="detail-value">#{{ selectedComplaint.id }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">状态</span>
          <span :class="`complaint-status ${selectedComplaint.status}`">{{ getStatusText(selectedComplaint.status) }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">合同ID</span>
          <span class="detail-value">#{{ selectedComplaint.contract_id }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">投诉内容</span>
          <span class="detail-value" style="white-space: pre-wrap;">{{ selectedComplaint.description }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">提交时间</span>
          <span class="detail-value">{{ formatDate(selectedComplaint.created_at) }}</span>
        </div>
        <div class="detail-row" v-if="selectedComplaint.processed_at">
          <span class="detail-label">处理时间</span>
          <span class="detail-value">{{ formatDate(selectedComplaint.processed_at) }}</span>
        </div>
        <div class="detail-row" v-if="selectedComplaint.resolved_at">
          <span class="detail-label">解决时间</span>
          <span class="detail-value">{{ formatDate(selectedComplaint.resolved_at) }}</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="dialogVisible"
      title="提交投诉"
      width="500px"
    >
      <el-form :model="complaintForm" label-width="80px">
        <el-form-item label="合同">
          <el-select v-model="complaintForm.contract_id" placeholder="请选择合同" style="width: 100%">
            <el-option 
              v-for="house in myHouses" 
              :key="house.id" 
              :label="house.title" 
              :value="house.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="投诉内容">
          <el-input 
            v-model="complaintForm.description" 
            type="textarea" 
            :rows="4" 
            placeholder="请详细描述您的投诉内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitComplaint">提交</el-button>
      </template>
    </el-dialog>
    <BackToTop />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import Pagination from '@/components/Pagination.vue'
import BackToTop from '@/components/BackToTop.vue'
import { getComplaintList, createComplaint } from '@/api/complaint'
import { getContractList } from '@/api/contract'

const USE_MOCK_DATA = false

const loading = ref(false)
const currentTab = ref('all')
const pageNum = ref(1)
const pageSize = ref(10)
const total = ref(0)
const complaints = ref([])
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const selectedComplaint = ref(null)
const myHouses = ref([])

const complaintForm = ref({
  contract_id: '',
  description: ''
})

const tabs = [
  { label: '全部', value: 'all' },
  { label: '待处理', value: 'pending' },
  { label: '处理中', value: 'processing' },
  { label: '已解决', value: 'resolved' }
]

const filteredComplaints = computed(() => {
  if (currentTab.value === 'all') {
    return complaints.value
  }
  return complaints.value.filter(complaint => complaint.status === currentTab.value)
})

const getTabCount = (status) => {
  if (status === 'all') return complaints.value.length
  return complaints.value.filter(c => c.status === status).length
}

const getStatusText = (status) => {
  const map = {
    pending: '待处理',
    processing: '处理中',
    resolved: '已解决',
    closed: '已关闭',
    rejected: '已拒绝'
  }
  return map[status] || status
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch {
    return dateStr
  }
}

const fetchComplaints = async () => {
  loading.value = true
  try {
    const res = await getComplaintList({ page: pageNum.value, page_size: pageSize.value })
    if (res.code === 0) {
      complaints.value = res.data.items || res.data.list || []
      total.value = res.data.total || 0
    }
  } catch (error) {
    console.error('获取投诉列表失败', error)
    complaints.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const fetchMyHouses = async () => {
  try {
    const res = await getContractList({ page: 1, page_size: 100 })
    if (res.code === 0) {
      const contracts = res.data.items || res.data.list || []
      // 只保留已生效的合同（状态为 active）
      const activeContracts = contracts.filter(c => c.status === 'active')
      myHouses.value = activeContracts.map(c => ({
        id: c.id,
        title: c.house?.title || `合同 #${c.id}`,
        contract_no: c.contract_no
      }))
    }
  } catch (error) {
    console.error('获取合同列表失败', error)
    myHouses.value = []
  }
}

const showComplaintDialog = () => {
  complaintForm.value = {
    contract_id: '',
    type: '',
    title: '',
    description: ''
  }
  dialogVisible.value = true
}

const submitComplaint = async () => {
  if (!complaintForm.value.contract_id) {
    ElMessage.warning('请选择合同')
    return
  }
  if (!complaintForm.value.description) {
    ElMessage.warning('请输入投诉内容')
    return
  }

  try {
    const res = await createComplaint({
      contract_id: complaintForm.value.contract_id,
      description: complaintForm.value.description
    })
    if (res.code === 0) {
      dialogVisible.value = false
      ElMessage.success('投诉提交成功')
      fetchComplaints()
    } else {
      ElMessage.error(res.message || '提交失败')
    }
  } catch (error) {
    ElMessage.error('提交失败，请稍后重试')
  }
}

const viewDetail = (complaint) => {
  selectedComplaint.value = complaint
  detailDialogVisible.value = true
}

const handlePageChange = (page) => {
  pageNum.value = page
  fetchComplaints()
}

onMounted(() => {
  fetchComplaints()
  fetchMyHouses()
})
</script>

<style scoped>
.complaint-page {
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

.complaint-list {
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

.complaint-card {
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

.complaint-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transform: translateY(-3px);
}

.complaint-info {
  flex: 1;
  min-width: 0;
}

.complaint-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  gap: 12px;
}

.complaint-no {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.complaint-status {
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 20px;
}

.complaint-status.pending {
  background: #fff7e6;
  color: #fa8c16;
}

.complaint-status.processing {
  background: #e6f7ff;
  color: #1890ff;
}

.complaint-status.completed {
  background: #f6ffed;
  color: #52c41a;
}

.complaint-status.resolved {
  background: #f6ffed;
  color: #52c41a;
}

.complaint-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

.complaint-house,
.complaint-type,
.complaint-desc {
  display: flex;
  align-items: flex-start;
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.complaint-house i,
.complaint-type i,
.complaint-desc i {
  margin-right: 8px;
  color: #1890ff;
  min-width: 16px;
}

.complaint-desc {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.complaint-dates {
  display: flex;
  gap: 20px;
  margin-top: 12px;
}

.date-item {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #999;
}

.date-item i {
  margin-right: 6px;
}

.complaint-response {
  display: flex;
  align-items: flex-start;
  margin-top: 12px;
  padding: 10px;
  background: #f6ffed;
  border-radius: 6px;
  font-size: 14px;
  color: #52c41a;
}

.complaint-response i {
  margin-right: 8px;
  min-width: 16px;
}

.complaint-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-left: 20px;
}

.detail-content {
  padding: 10px;
}

.detail-row {
  display: flex;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  width: 100px;
  color: #666;
  font-weight: 500;
  flex-shrink: 0;
}

.detail-value {
  flex: 1;
  color: #333;
}
</style>