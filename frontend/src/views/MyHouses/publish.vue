<template>
  <div class="publish-page">
    <div class="publish-title">
      <div class="title-row">
        <button class="back-btn" @click="router.push('/myhouses/list')">
          <i class="fa-solid fa-arrow-left"></i>
          <span>返回</span>
        </button>
      </div>
      <div class="title-text">
        <h1>{{ pageTitle }}</h1>
        <p class="subtitle">{{ pageTitle === '发布新房源' ? '发布您的优质房源' : '编辑房源信息' }}</p>
      </div>
    </div>

    <div class="publish-form">
      <div 
        v-for="field in formFields" 
        :key="field.key"
        :ref="el => setItemRef(el, field.key)"
        class="form-item"
        :class="{ 'error': errors[field.key] }"
      >
        <label>
          <span v-if="field.required" class="required">*</span>
          {{ field.label }}
        </label>
        
        <!-- 输入框 -->
        <input 
          v-if="field.type === 'text' || field.type === 'number'"
          :type="field.type"
          v-model="form[field.key]"
          :placeholder="field.placeholder"
          @input="clearError(field.key)"
        />
        
        <!-- 文本域 -->
        <textarea 
          v-else-if="field.type === 'textarea'"
          v-model="form[field.key]"
          :placeholder="field.placeholder"
          :rows="field.rows || 3"
          @input="clearError(field.key)"
        />
        
        <!-- 带单位的输入 -->
        <div v-else-if="field.type === 'unit'" class="input-wrap">
          <input 
            :type="field.inputType || 'number'"
            v-model="form[field.key]"
            :placeholder="field.placeholder"
            @input="clearError(field.key)"
          />
          <span class="unit">{{ field.unit }}</span>
        </div>
        
      </div>
    </div>

    <div class="submit-section">
      <button class="submit-btn" @click="handleSubmit">{{ isEdit ? '保存修改' : '提交委托' }}</button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, nextTick, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import service from '@/utils/request'
import { updateHouse, createHouse } from '@/api/house.js'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const isEdit = computed(() => !!route.params.id)
const houseId = computed(() => route.params.id)
const pageTitle = computed(() => isEdit.value ? '编辑出租房源' : '创建出租房源')

// 表单字段配置
const formFields = [
  { key: 'title', label: '房源标题', type: 'text', required: true, placeholder: '如：中南大学旁精装两室一厅' },
  { key: 'region', label: '所在区域', type: 'text', required: true, placeholder: '如：岳麓区、雨花区' },
  { key: 'address', label: '详细地址', type: 'text', required: true, placeholder: '请输入完整地址' },
  { key: 'community', label: '小区', type: 'text', required: false, placeholder: '选填' },
  { key: 'house_type', label: '户型', type: 'text', required: true, placeholder: '如:1室1厅、3室2厅' },
  { key: 'area', label: '面积', type: 'unit', required: true, placeholder: '请输入面积', unit: '㎡' },
  { key: 'rent', label: '月租金', type: 'unit', required: true, placeholder: '请输入月租', unit: '元/月' },
  { key: 'deposit', label: '押金', type: 'unit', required: true, placeholder: '请输入押金', unit: '元' },
  { key: 'orientation', label: '朝向', type: 'text', required: false, placeholder: '选填,如：南、南北通透' },
  { key: 'decoration', label: '装修情况', type: 'text', required: false, placeholder: '选填，如：精装修' },
  { key: 'floor', label: '楼层', type: 'text', required: false, placeholder: '选填,如:6/18' },
  { key: 'description', label: '房源描述', type: 'textarea', required: false, placeholder: '选填，简要描述您的房子' }
]

// 表单数据
const form = reactive({
  title: '',
  region: '',
  address: '',
  community: '',
  house_type: '',
  area: '',
  rent: '',
  deposit: '',
  orientation: '',
  decoration: '',
  floor: '',
  description: ''
})

// 错误状态
const errors = reactive({})

// 元素引用
const itemRefs = {}

const setItemRef = (el, key) => {
  if (el) itemRefs[key] = el
}

// 清除错误
const clearError = (key) => {
  errors[key] = false
}

const fetchHouseDetail = async () => {
  try {
    const res = await service.get(`/v1/houses/${houseId.value}`)
    if (res.code === 0) {
      const data = res.data
      Object.assign(form, {
        title: data.title || '',
        region: data.region || '',
        address: data.address || '',
        community: data.community || '',
        house_type: data.house_type || '',
        area: data.area || '',
        rent: data.rent || '',
        deposit: data.deposit || '',
        orientation: data.orientation || '',
        decoration: data.decoration || '',
        floor: data.floor || '',
        description: data.description || ''
      })
    }
  } catch (e) {
    ElMessage.error('加载房源详情失败')
  }
}

// 验证并提交
const handleSubmit = async () => {
  // 清空错误
  Object.keys(errors).forEach(k => errors[k] = false)
  
  // 检查必填
  let firstErrorKey = null
  
  for (const field of formFields) {
    if (!field.required) continue
    
    const isEmpty = !form[field.key]
    
    if (isEmpty) {
      errors[field.key] = true
      if (!firstErrorKey) firstErrorKey = field.key
    }
  }
  
  // 有错误：滚动到第一个并标红
  if (firstErrorKey) {
    await nextTick()
    const el = itemRefs[firstErrorKey]
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      // 添加抖动动画
      el.classList.add('shake')
      setTimeout(() => el.classList.remove('shake'), 500)
    }
    return
  }
  
  // 通过验证，提交
  try {
    // 数字类型转换
    const houseData = {
      ...form,
      area: parseFloat(form.area) || 0,
      rent: parseFloat(form.rent) || 0,
      deposit: parseFloat(form.deposit) || 0
    }

    if (isEdit.value) {
      await updateHouse(houseId.value, houseData)
      ElMessage.success('房源修改成功！')
    } else {
      await createHouse(houseData)
      ElMessage.success('房源创建成功！')
    }
    
    router.push('/myhouses/list')
  } catch (e) {
    const msg = e.response?.data?.message || (isEdit.value ? '修改失败，请重试' : '创建失败，请重试')
    ElMessage.error(msg)
  }
}

onMounted(() => {
  if (isEdit.value) {
    fetchHouseDetail()
  }
})
</script>
<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.publish-page {
  min-height: 100vh;
  padding-bottom: 60px;
}

/* 标题 */
.publish-title {
  background: #f5f5f5;
  padding: 40px 0 30px;
  text-align: center;
}

.title-row {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding-left: calc((100vw - 700px) / 2 - 10px);
  
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: #fff;
  color: #64748b;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: #e2e8f0;
  color: #475569;
  border-color: #cbd5e1;
}

.title-text {
  text-align: center;
}

.publish-title h1 {
  font-size: 32px;
  font-weight: 600;
  color: #101d37;
  margin-bottom: 12px;
}

.publish-title p {
  font-size: 14px;
  color: #9399a5;
}

/* 表单 */
.publish-form {
  width: 700px;
  margin: 0 auto;
  background: #fff;
  padding: 0px 60px;
  border-radius: 4px;
}

.form-item {
  display: flex;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
  gap: 20px;
  transition: all 0.3s;
}

.form-item:last-child {
  border-bottom: none;
}

.form-item:has(textarea) {
  align-items: flex-start;
}

.form-item:has(textarea) label {
  padding-top: 10px;
}

/* 错误状态：标红 */
.form-item.error input,
.form-item.error textarea {
  border-color: #ff4d4f;
  background: #fff;
}

.form-item.error input:focus,
.form-item.error textarea:focus {
  border-color: #ff4d4f;
  box-shadow: 0 0 0 2px rgba(255, 77, 79, 0.2);
}

/* 抖动动画 */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

.shake {
  animation: shake 0.5s ease;
}

/* label */
.form-item label {
  width: 80px;
  font-size: 14px;
  color: #101d37;
  font-weight: 500;
  flex-shrink: 0;
  text-align: end;
}

.required {
  color: #ff4d4f;
  margin-right: 4px;
}

/* 输入框 */
.form-item input,
.form-item textarea {
  flex: 1;
  min-width: 0;
  height: 40px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 0 12px;
  font-size: 14px;
  color: #333;
  background: #f5f5f5;
  outline: none;
  transition: all 0.2s;
}

.form-item input:focus,
.form-item textarea:focus {
  border-color: #3072f6;
  background: #fff;
}

.form-item input::placeholder,
.form-item textarea::placeholder {
  color: #999;
}

.form-item textarea {
  min-height: 80px;
  padding: 10px 12px;
  resize: vertical;
  line-height: 1.5;
}

/* 输入框包装 */
.input-wrap {
  flex: 1;
  display: flex;
  gap: 12px;
  min-width: 0;
}

.input-wrap input {
  flex: 1;
  min-width: 0;
}

.unit {
  font-size: 14px;
  color: #666;
  white-space: nowrap;
}

/* 提交 */
.submit-section {
  width: 700px;
  margin: 30px auto 0;
  text-align: center;
}

.submit-btn {
  width: 240px;
  height: 48px;
  background: #3072f6;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.submit-btn:hover {
  background: #2860d6;
}
</style>