<template>
  <div class="publish-page">
    <div class="publish-header">
      <div class="header-inner">
        <button class="back-btn" @click="router.push('/myhouses/list')">
          <i class="fa-solid fa-arrow-left"></i>
        </button>
        <div class="header-title">
          <h1>{{ pageTitle }}</h1>
          <p class="subtitle">完善房源信息，让更多租客找到您的房子</p>
        </div>
      </div>
    </div>

    <div class="publish-body">
      <div class="form-container">

        <!-- 基本信息卡片 -->
        <div class="form-card">
          <div class="card-head">
            <i class="fa-solid fa-circle-info"></i>
            <span>基本信息</span>
          </div>
          <div class="card-body">
            <template v-for="field in basicFields" :key="field.key">
              <div
                :ref="el => setItemRef(el, field.key)"
                class="form-item"
                :class="{ error: errors[field.key] }"
              >
                <label>
                  <span v-if="field.required" class="required">*</span>
                  {{ field.label }}
                </label>
                <component
                  :is="field.type === 'textarea' ? 'textarea' : 'input'"
                  :type="field.type === 'textarea' ? undefined : (field.inputType || field.type)"
                  v-model="form[field.key]"
                  :placeholder="field.placeholder"
                  :rows="field.type === 'textarea' ? 4 : undefined"
                  @input="clearError(field.key)"
                />
                <span v-if="field.unit" class="unit">{{ field.unit }}</span>
              </div>
            </template>
          </div>
        </div>

        <!-- 租金信息卡片 -->
        <div class="form-card">
          <div class="card-head">
            <i class="fa-solid fa-coins"></i>
            <span>租金信息</span>
          </div>
          <div class="card-body">
            <template v-for="field in rentFields" :key="field.key">
              <div
                :ref="el => setItemRef(el, field.key)"
                class="form-item"
                :class="{ error: errors[field.key] }"
              >
                <label>
                  <span v-if="field.required" class="required">*</span>
                  {{ field.label }}
                </label>
                <component
                  :is="'input'"
                  :type="field.inputType || 'number'"
                  v-model="form[field.key]"
                  :placeholder="field.placeholder"
                  @input="clearError(field.key)"
                />
                <span v-if="field.unit" class="unit">{{ field.unit }}</span>
              </div>
            </template>
          </div>
        </div>

        <!-- 详细信息卡片 -->
        <div class="form-card">
          <div class="card-head">
            <i class="fa-solid fa-clipboard-list"></i>
            <span>详细信息</span>
          </div>
          <div class="card-body">
            <template v-for="field in detailFields" :key="field.key">
              <div
                :ref="el => setItemRef(el, field.key)"
                class="form-item"
                :class="{ error: errors[field.key] }"
              >
                <label>
                  <span v-if="field.required" class="required">*</span>
                  {{ field.label }}
                </label>
                <component
                  :is="field.type === 'textarea' ? 'textarea' : 'input'"
                  :type="field.type === 'textarea' ? undefined : 'text'"
                  v-model="form[field.key]"
                  :placeholder="field.placeholder"
                  :rows="field.type === 'textarea' ? 4 : undefined"
                  @input="clearError(field.key)"
                />
              </div>
            </template>
          </div>
        </div>

        <!-- 房源图片卡片 -->
        <div class="form-card">
          <div class="card-head">
            <i class="fa-solid fa-images"></i>
            <span>房源图片</span>
            <span class="tip-badge">最多9张</span>
          </div>
          <div class="card-body">
            <div class="image-upload-area">
              <div v-for="(img, index) in imageList" :key="index" class="image-preview-item">
                <img :src="img.preview" alt="预览" />
                <div v-if="img.isCover" class="cover-tag">封面</div>
                <div class="image-actions">
                  <button v-if="!img.isCover" class="action-btn cover-btn" @click="setCover(index)">
                    设封面
                  </button>
                  <button class="action-btn delete-btn" @click="removeImage(index)">
                    <i class="fa-solid fa-xmark"></i>
                  </button>
                </div>
              </div>
              <div v-if="imageList.length < 9" class="upload-trigger" @click="triggerUpload">
                <input ref="fileInput" type="file" multiple accept="image/jpeg,image/png,image/webp" @change="handleFileChange" style="display:none" />
                <i class="fa-solid fa-cloud-arrow-up"></i>
                <span>点击上传</span>
                <span class="upload-hint">jpg / png / webp ≤ 5MB</span>
              </div>
            </div>
          </div>
        </div>

        <div class="submit-section">
          <button class="submit-btn" @click="handleSubmit">
            <i class="fa-solid fa-paper-plane"></i>
            {{ isEdit ? '保存修改' : '提交房源' }}
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, nextTick, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import service from '@/utils/request'
import { updateHouse, createHouse } from '@/api/house.js'
import { uploadHouseImage, deleteHouseImage } from '@/api/houseImage.js'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const isEdit = computed(() => !!route.params.id)
const houseId = computed(() => route.params.id)
const pageTitle = computed(() => isEdit.value ? '编辑房源' : '发布房源')

const basicFields = [
  { key: 'title', label: '房源标题', type: 'text', required: true, placeholder: '如：中南大学旁精装两室一厅' },
  { key: 'region', label: '所在区域', type: 'text', required: true, placeholder: '如：岳麓区、雨花区' },
  { key: 'address', label: '详细地址', type: 'text', required: true, placeholder: '请输入完整地址' },
  { key: 'community', label: '所属小区', type: 'text', required: false, placeholder: '选填' },
  { key: 'house_type', label: '户型', type: 'text', required: true, placeholder: '如：1室1厅、3室2厅' },
]

const rentFields = [
  { key: 'area', label: '面积', inputType: 'number', required: true, placeholder: '请输入面积', unit: '㎡' },
  { key: 'rent', label: '月租金', inputType: 'number', required: true, placeholder: '请输入月租', unit: '元/月' },
  { key: 'deposit', label: '押金', inputType: 'number', required: true, placeholder: '请输入押金', unit: '元' },
]

const detailFields = [
  { key: 'orientation', label: '朝向', type: 'text', required: false, placeholder: '选填，如：南、南北通透' },
  { key: 'decoration', label: '装修情况', type: 'text', required: false, placeholder: '选填，如：精装修' },
  { key: 'floor', label: '楼层', type: 'text', required: false, placeholder: '选填，如：6/18层' },
  { key: 'description', label: '房源描述', type: 'textarea', required: false, placeholder: '描述您的房源特色，如交通便利、采光好、家电齐全等' },
]

const allFields = [...basicFields, ...rentFields, ...detailFields]

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

// 图片上传
const fileInput = ref(null)
const imageList = ref([])
const MAX_IMAGES = 9
const MAX_FILE_SIZE = 5 * 1024 * 1024

const triggerUpload = () => {
  fileInput.value?.click()
}

const handleFileChange = (e) => {
  const files = Array.from(e.target.files)
  const remaining = MAX_IMAGES - imageList.value.length
  
  if (files.length > remaining) {
    ElMessage.warning(`最多还能上传${remaining}张图片`)
  }
  
  const validFiles = files.slice(0, remaining).filter(file => {
    if (file.size > MAX_FILE_SIZE) {
      ElMessage.warning(`${file.name} 超过5MB限制`)
      return false
    }
    const ext = file.name.split('.').pop().toLowerCase()
    if (!['jpg', 'jpeg', 'png', 'webp'].includes(ext)) {
      ElMessage.warning(`${file.name} 格式不支持`)
      return false
    }
    return true
  })
  
  validFiles.forEach(file => {
    const preview = URL.createObjectURL(file)
    imageList.value.push({
      file,
      preview,
      isCover: imageList.value.length === 0
    })
  })
  
  e.target.value = ''
}

const setCover = (index) => {
  imageList.value.forEach((img, i) => {
    img.isCover = (i === index)
  })
}

const removeImage = (index) => {
  const removed = imageList.value[index]
  if (removed?.preview) {
    URL.revokeObjectURL(removed.preview)
  }
  imageList.value.splice(index, 1)
  if (removed?.isCover && imageList.value.length > 0) {
    imageList.value[0].isCover = true
  }
}

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
  
  for (const field of allFields) {
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
    const houseData = {
      ...form,
      area: parseFloat(form.area) || 0,
      rent: parseFloat(form.rent) || 0,
      deposit: parseFloat(form.deposit) || 0
    }

    let houseResult;
    if (isEdit.value) {
      houseResult = await updateHouse(houseId.value, houseData)
      ElMessage.success('房源修改成功！')
    } else {
      houseResult = await createHouse(houseData)
      ElMessage.success('房源创建成功！')
    }
    
    const targetHouseId = isEdit.value ? houseId.value : houseResult.data?.id
    if (targetHouseId && imageList.value.length > 0) {
      await uploadImages(targetHouseId)
    }
    
    router.push('/myhouses/list')
  } catch (e) {
    const msg = e.response?.data?.message || (isEdit.value ? '修改失败，请重试' : '创建失败，请重试')
    ElMessage.error(msg)
  }
}

const uploadImages = async (houseId) => {
  for (const img of imageList.value) {
    const formData = new FormData()
    formData.append('file', img.file)
    if (img.isCover) {
      formData.append('is_cover', 'true')
    }
    try {
      await uploadHouseImage(houseId, formData)
    } catch (e) {
      console.error('上传图片失败:', e)
    }
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
  background: #f5f6f8;
}

.publish-header {
  background: #fff;
  border-bottom: 1px solid #eef0f3;
  padding: 0 40px;
}

.header-inner {
  max-width: 760px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  padding: 24px 0;
  position: relative;
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: #f5f6f8;
  color: #555;
  border: 1px solid #e8eaed;
  border-radius: 10px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  position: absolute;
  left: 0;
}

.header-title {
  text-align: center;
}

.back-btn:hover {
  background: #eef0f3;
  color: #333;
  border-color: #d0d4da;
}

.header-title h1 {
  font-size: 30px;
  font-weight: 700;
  color: #1a1a2e;
  line-height: 1.3;
}

.header-title .subtitle {
  font-size: 13px;
  color: #8e94a0;
  margin-top: 2px;
}

.publish-body {
  padding: 32px 40px 80px;
}

.form-container {
  max-width: 760px;
  margin: 0 auto;
}

.form-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  margin-bottom: 20px;
  overflow: hidden;
}

.card-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 24px;
  background: #fafbfc;
  border-bottom: 1px solid #f0f1f3;
  font-size: 15px;
  font-weight: 600;
  color: #1a1a2e;
}

.card-head i {
  font-size: 16px;
  color: #3072f6;
  width: 20px;
  text-align: center;
}

.tip-badge {
  margin-left: auto;
  font-size: 12px;
  font-weight: 400;
  color: #8e94a0;
  background: #f0f1f3;
  padding: 3px 10px;
  border-radius: 10px;
}

.card-body {
  padding: 8px 24px;
}

.form-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 0;
  border-bottom: 1px solid #f5f6f8;
  transition: all 0.2s;
}

.form-item:last-child {
  border-bottom: none;
}

.form-item:has(textarea) {
  align-items: flex-start;
}

.form-item:has(textarea) label {
  padding-top: 12px;
}

.form-item label {
  width: 72px;
  font-size: 13px;
  color: #555;
  font-weight: 500;
  flex-shrink: 0;
  text-align: right;
}

.required {
  color: #ff4d4f;
  margin-right: 2px;
}

.form-item input,
.form-item textarea {
  flex: 1;
  min-width: 0;
  height: 42px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 0 14px;
  font-size: 14px;
  color: #333;
  background: #fafbfc;
  outline: none;
  transition: all 0.2s;
  font-family: inherit;
}

.form-item input::placeholder,
.form-item textarea::placeholder {
  color: #b0b5bd;
}

.form-item input:hover,
.form-item textarea:hover {
  border-color: #ccd0d6;
}

.form-item input:focus,
.form-item textarea:focus {
  border-color: #3072f6;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(48, 114, 246, 0.08);
}

.form-item textarea {
  min-height: 90px;
  padding: 10px 14px;
  resize: vertical;
  line-height: 1.6;
}

.unit {
  font-size: 13px;
  color: #8e94a0;
  white-space: nowrap;
  font-weight: 500;
}

.form-item.error input,
.form-item.error textarea {
  border-color: #ff4d4f;
  background: #fff;
}

.form-item.error input:focus,
.form-item.error textarea:focus {
  border-color: #ff4d4f;
  box-shadow: 0 0 0 3px rgba(255, 77, 79, 0.08);
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-4px); }
  20%, 40%, 60%, 80% { transform: translateX(4px); }
}

.shake {
  animation: shake 0.5s ease;
}

.image-upload-area {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  padding: 4px 0;
}

.image-preview-item {
  position: relative;
  aspect-ratio: 4 / 3;
  border-radius: 10px;
  overflow: hidden;
  border: 2px solid #eef0f3;
  transition: all 0.2s;
}

.image-preview-item:hover {
  border-color: #3072f6;
}

.image-preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-tag {
  position: absolute;
  top: 10px;
  left: 10px;
  background: #3072f6;
  color: #fff;
  padding: 4px 10px;
  border-radius: 5px;
  font-size: 12px;
  font-weight: 500;
  box-shadow: 0 2px 6px rgba(48, 114, 246, 0.35);
}

.image-actions {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.6));
  opacity: 0;
  transition: opacity 0.2s;
}

.image-preview-item:hover .image-actions {
  opacity: 1;
}

.action-btn {
  padding: 4px 12px;
  border: none;
  border-radius: 5px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
}

.cover-btn {
  background: rgba(255, 255, 255, 0.92);
  color: #333;
  font-weight: 500;
}

.cover-btn:hover {
  background: #fff;
}

.delete-btn {
  background: rgba(255, 77, 79, 0.88);
  color: #fff;
  width: 26px;
  height: 26px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  margin-left: auto;
}

.delete-btn:hover {
  background: #ff4d4f;
}

.upload-trigger {
  aspect-ratio: 4 / 3;
  border: 2px dashed #d4d7de;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.2s;
  color: #b0b5bd;
  background: #fafbfc;
}

.upload-trigger:hover {
  border-color: #3072f6;
  color: #3072f6;
  background: #f0f4ff;
}

.upload-trigger i {
  font-size: 28px;
}

.upload-trigger span {
  font-size: 14px;
  font-weight: 500;
}

.upload-hint {
  font-size: 11px;
  font-weight: 400;
  color: #ccd0d6;
}

.submit-section {
  text-align: center;
  padding: 16px 0 0;
}

.submit-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 48px;
  background: linear-gradient(135deg, #3072f6 0%, #1a5be0 100%);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 14px rgba(48, 114, 246, 0.3);
}

.submit-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(48, 114, 246, 0.4);
}

.submit-btn i {
  font-size: 15px;
}
</style>