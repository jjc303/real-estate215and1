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
          <el-form-item label="预约ID" prop="appointment_id" required>
            <el-input-number v-model="form.appointment_id" :min="1" placeholder="请输入预约ID" />
          </el-form-item>
        </div>

        <div class="form-section">
          <div class="section-title">
            <i class="fa-solid fa-calendar-days"></i> 租期信息
          </div>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="起租日期" prop="start_date" required>
                <el-date-picker v-model="form.start_date" type="date" placeholder="选择起租日期" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="到期日期" prop="end_date" required>
                <el-date-picker v-model="form.end_date" type="date" placeholder="选择到期日期" />
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
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import service from '@/utils/request'

const USE_MOCK_DATA = true

const formRef = ref(null)

const form = reactive({
  appointment_id: 0,
  start_date: '',
  end_date: '',
  monthly_rent: 0,
  deposit: 0,
  remark: ''
})

const goBack = () => {
  window.history.back()
}

const submitForm = async () => {
  try {
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
</script>

<style scoped>
.contract-create-page {
  padding: 20px;
  max-width: 600px;
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
</style>