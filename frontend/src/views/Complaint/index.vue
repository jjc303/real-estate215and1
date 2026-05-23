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
          
          <div class="complaint-title">{{ complaint.title }}</div>
          
          <div class="complaint-house">
            <i class="fa-solid fa-home"></i>
            <span>房源：{{ complaint.house?.title }}</span>
          </div>
          
          <div class="complaint-type">
            <i class="fa-solid fa-tag"></i>
            <span>类型：{{ getTypeText(complaint.type) }}</span>
          </div>
          
          <div class="complaint-desc">
            <i class="fa-solid fa-file-text"></i>
            <span>{{ complaint.description }}</span>
          </div>
          
          <div class="complaint-dates">
            <div class="date-item">
              <i class="fa-solid fa-clock"></i>
              <span>提交时间：{{ complaint.created_at }}</span>
            </div>
            <div v-if="complaint.processed_at" class="date-item">
              <i class="fa-solid fa-check-circle"></i>
              <span>处理时间：{{ complaint.processed_at }}</span>
            </div>
          </div>
          
          <div v-if="complaint.response" class="complaint-response">
            <i class="fa-solid fa-reply"></i>
            <span>回复：{{ complaint.response }}</span>
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
        <el-form-item label="投诉类型">
          <el-select v-model="complaintForm.type" placeholder="请选择类型" style="width: 100%">
            <el-option label="服务态度" value="service" />
            <el-option label="房屋问题" value="house" />
            <el-option label="合同纠纷" value="contract" />
            <el-option label="费用问题" value="fee" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="投诉标题">
          <el-input v-model="complaintForm.title" placeholder="请输入投诉标题" />
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
import { mockComplaints, mockMyHouses } from '@/mock/complaints'
import { getComplaintList, createComplaint } from '@/api/complaint'

const USE_MOCK_DATA = true

const loading = ref(false)
const currentTab = ref('all')
const pageNum = ref(1)
const pageSize = ref(10)
const total = ref(0)
const complaints = ref([])
const dialogVisible = ref(false)
const myHouses = ref([])

const complaintForm = ref({
  contract_id: '',
  type: '',
  title: '',
  description: ''
})

const tabs = [
  { label: '全部', value: 'all' },
  { label: '待处理', value: 'pending' },
  { label: '处理中', value: 'processing' },
  { label: '已完成', value: 'completed' }
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
    completed: '已完成'
  }
  return map[status] || status
}

const getTypeText = (type) => {
  const map = {
    service: '服务态度',
    house: '房屋问题',
    contract: '合同纠纷',
    fee: '费用问题',
    other: '其他'
  }
  return map[type] || type
}

const fetchComplaints = async () => {
  loading.value = true
  try {
    if (USE_MOCK_DATA) {
      const start = (pageNum.value - 1) * pageSize.value
      const end = start + pageSize.value
      complaints.value = mockComplaints.slice(start, end)
      total.value = mockComplaints.length
    } else {
      const res = await getComplaintList({ page: pageNum.value, page_size: pageSize.value })
      if (res.code === 0) {
        complaints.value = res.data.list
        total.value = res.data.total
      }
    }
  } catch (error) {
    console.error('获取投诉列表失败', error)
    complaints.value = []
  } finally {
    loading.value = false
  }
}

const fetchMyHouses = async () => {
  if (USE_MOCK_DATA) {
    myHouses.value = mockMyHouses
  } else {
    // 真实API调用
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
  if (!complaintForm.value.type) {
    ElMessage.warning('请选择投诉类型')
    return
  }
  if (!complaintForm.value.title) {
    ElMessage.warning('请输入投诉标题')
    return
  }
  if (!complaintForm.value.description) {
    ElMessage.warning('请输入投诉内容')
    return
  }

  try {
    if (USE_MOCK_DATA) {
      const newComplaint = {
        id: complaints.value.length + 1,
        contract_id: complaintForm.value.contract_id,
        house: myHouses.value.find(h => h.id === complaintForm.value.contract_id),
        type: complaintForm.value.type,
        title: complaintForm.value.title,
        description: complaintForm.value.description,
        status: 'pending',
        created_at: new Date().toLocaleString(),
        processed_at: null,
        response: null
      }
      complaints.value.unshift(newComplaint)
      total.value++
      dialogVisible.value = false
      ElMessage.success('投诉提交成功')
    } else {
      const res = await createComplaint({
        contract_id: complaintForm.value.contract_id,
        description: complaintForm.value.description
      })
      if (res.code === 0) {
        dialogVisible.value = false
        ElMessage.success('投诉提交成功')
        fetchComplaints()
      }
    }
  } catch (error) {
    ElMessage.error('提交失败，请稍后重试')
  }
}

const viewDetail = (complaint) => {
  ElMessage.info(`查看投诉详情: ${complaint.title}`)
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
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
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
</style>