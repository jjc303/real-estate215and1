<template>
  <div class="publish-page">
    <div class="publish-title">
      <h1>创建出租房源</h1>
      <p>清风雅居 · 城隅美宅 · 恬静闲舍</p>
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
      <button class="submit-btn" @click="handleSubmit">提交委托</button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import service from '@/utils/request'
import { useRouter } from 'vue-router'

const router = useRouter()

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

    const res = await service.post('/v1/houses', houseData)

    if (res.code === 0) {
      ElMessage.success('房源创建成功！')
      
      // 3. 可选：自动发布房源
      // await service.patch(`/v1/houses/${res.data.id}/publish`)
      // ElMessage.success('房源已发布！')
      
      // 4. 跳转到我的房源列表
      router.push('/myhouses/list')
    }
  } catch (e) {
    const msg = e.response?.data?.message || '创建失败，请重试'
    ElMessage.error(msg)
    console.error('发布房源错误详情：', e.response?.data)
  }
}
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
  text-align: center;
  padding: 40px 0 30px;
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