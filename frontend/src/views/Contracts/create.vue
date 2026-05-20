<template>
  <div class="contract-create-page">
    <div class="page-header">
      <div class="header-left">
        <button class="back-btn" @click="goBack">
          <i class="fa-solid fa-arrow-left"></i> 返回
        </button>
        <h2>新建合同</h2>
        <p class="subtitle">创建新的租房合同</p>
      </div>
    </div>

    <div class="contract-form">
      <el-form ref="formRef" :model="form" label-width="120px">
        <div class="form-section">
          <div class="section-title">
            <i class="fa-solid fa-calendar-check"></i> 预约关联
          </div>
          <el-form-item label="选择预约" prop="appointment_id" required>
            <el-select 
              v-model="form.appointment_id" 
              placeholder="请选择已确认的预约" 
              style="width: 100%"
              @change="onAppointmentChange"
            >
              <el-option 
                v-for="apt in confirmedAppointments" 
                :key="apt.id" 
                :label="`#${apt.id} ${apt.house?.title || ''} — 租客 #${apt.tenant_id}`" 
                :value="apt.id"
              />
            </el-select>
          </el-form-item>
          
          <div v-if="selectedAppointment" class="appointment-preview">
            <div class="preview-title">预约详情</div>
            <div class="preview-grid">
              <div class="preview-item">
                <span class="preview-label">房源</span>
                <span class="preview-value">{{ selectedAppointment.house?.title }}</span>
              </div>
              <div class="preview-item">
                <span class="preview-label">区域</span>
                <span class="preview-value">{{ selectedAppointment.house?.region }} {{ selectedAppointment.house?.address }}</span>
              </div>
              <div class="preview-item">
                <span class="preview-label">租客ID</span>
                <span class="preview-value">#{{ selectedAppointment.tenant_id }}</span>
              </div>
              <div class="preview-item">
                <span class="preview-label">预约时间</span>
                <span class="preview-value">{{ formatDateTime(selectedAppointment.appointment_time) }}</span>
              </div>
              <div class="preview-item">
                <span class="preview-label">看房备注</span>
                <span class="preview-value">{{ selectedAppointment.remark || '无' }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="form-section">
          <div class="section-title">
            <i class="fa-solid fa-calendar-days"></i> 租期信息
          </div>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="起租日期" prop="start_date" required>
                <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" placeholder="选择起租日期" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="到期日期" prop="end_date" required>
                <el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" placeholder="选择到期日期" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <div class="form-section">
          <div class="section-title">
            <i class="fa-solid fa-money-bill"></i> 费用信息
          </div>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="月租金(元)" prop="monthly_rent" required>
                <el-input-number v-model="form.monthly_rent" :min="0" placeholder="月租金" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="押金(元)" prop="deposit" required>
                <el-input-number v-model="form.deposit" :min="0" placeholder="押金金额" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <div class="form-section">
          <div class="section-title">
            <i class="fa-solid fa-file-text"></i> 备注信息
          </div>
          <el-form-item label="备注">
            <el-textarea v-model="form.remark" rows="3" placeholder="请输入备注信息（可选）" />
          </el-form-item>
        </div>

        <div class="form-actions">
          <el-button type="default" @click="goBack">取消</el-button>
          <el-button type="primary" @click="submitForm">创建合同</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import service from '@/utils/request'

const USE_MOCK_DATA = false

const formRef = ref(null)

const form = reactive({
  appointment_id: null,
  start_date: '',
  end_date: '',
  monthly_rent: 0,
  deposit: 0,
  remark: ''
})

const confirmedAppointments = ref([])
const appointmentsLoading = ref(false)

const selectedAppointment = computed(() => {
  return confirmedAppointments.value.find(a => a.id === form.appointment_id) || null
})

const formatDateTime = (datetime) => {
  if (!datetime) return ''
  const date = new Date(datetime)
  return date.toLocaleString('zh-CN')
}

const fetchConfirmedAppointments = async () => {
  appointmentsLoading.value = true
  try {
    const res = await service.get('/v1/appointments', { params: { page: 1, page_size: 100 } })
    if (res.code === 0) {
      confirmedAppointments.value = res.data.list.filter(a => a.status === 'confirmed')
    }
  } catch (e) {
    console.error('获取预约列表失败', e)
  } finally {
    appointmentsLoading.value = false
  }
}

const onAppointmentChange = (appointmentId) => {
  const apt = confirmedAppointments.value.find(a => a.id === appointmentId)
  if (apt) {
    form.monthly_rent = Number(apt.house?.rent) || 0
    form.deposit = Number(apt.house?.deposit) || 0
  }
}

const goBack = () => {
  window.history.back()
}

const submitForm = async () => {
  try {
    if (!form.appointment_id) {
      ElMessage.warning('请选择已确认的预约')
      return
    }
    if (!form.start_date) {
      ElMessage.warning('请选择起租日期')
      return
    }
    if (!form.end_date) {
      ElMessage.warning('请选择到期日期')
      return
    }
    if (form.start_date >= form.end_date) {
      ElMessage.warning('到期日期必须晚于起租日期')
      return
    }
    if (!form.monthly_rent || form.monthly_rent <= 0) {
      ElMessage.warning('月租金必须大于0')
      return
    }
    if (form.deposit < 0) {
      ElMessage.warning('押金不能为负数')
      return
    }

    await ElMessageBox.confirm(
      '确认创建合同吗？创建后合同将处于待确认状态，等待租客确认后生效。',
      '确认创建',
      {
        confirmButtonText: '创建',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    if (USE_MOCK_DATA) {
      ElMessage.success('合同创建成功！')
      setTimeout(() => {
        window.location.href = '/contracts'
      }, 1500)
    } else {
      const res = await service.post('/v1/contracts', {
        appointment_id: form.appointment_id,
        start_date: form.start_date,
        end_date: form.end_date,
        monthly_rent: form.monthly_rent,
        deposit: form.deposit,
        remark: form.remark || null
      })
      
      if (res.code === 0) {
        ElMessage.success('合同创建成功！')
        setTimeout(() => {
          window.location.href = '/contracts'
        }, 1500)
      } else {
        ElMessage.error(res.message || '创建失败')
      }
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('提交失败，请稍后重试')
      console.error(e)
    }
  }
}

onMounted(() => {
  fetchConfirmedAppointments()
})
</script>

<style scoped>
.contract-create-page {
  padding: 20px;
  max-width: 600px;
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

.contract-form {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

.form-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
}

.form-section:last-of-type {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
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

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}

.form-actions .el-button {
  padding: 10px 24px;
}

.el-form-item {
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .contract-create-page {
    padding: 12px;
  }
  
  .contract-form {
    padding: 16px;
  }
}

.appointment-preview {
  margin-top: 12px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
}

.preview-title {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e8e8e8;
}

.preview-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-label {
  font-size: 13px;
  color: #8c8c8c;
}

.preview-value {
  font-size: 13px;
  color: #262626;
  text-align: right;
}
</style>