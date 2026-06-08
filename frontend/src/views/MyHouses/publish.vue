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

      <div class="form-item image-form-item">
        <label><span class="required">*</span>房源图片</label>
        <div class="image-upload-wrap">
          <div 
            class="image-upload-area"
            :class="{ dragging: isDragging }"
            @dragover.prevent="handleDragOver"
            @dragleave.prevent="handleDragLeave"
            @drop.prevent="handleDrop"
          >
            <div v-for="(img, index) in imageList" :key="index" class="image-preview-item">
              <img :src="img.preview" alt="预览" />
              <div v-if="img.isCover" class="cover-tag">封面</div>
              <div class="image-actions">
                <button v-if="!img.isCover" class="action-btn cover-btn" @click="setCover(index)">设封面</button>
                <button class="action-btn delete-btn" @click="removeImage(index)">
                  <i class="fa-solid fa-xmark"></i>
                </button>
              </div>
            </div>
            <div v-if="imageList.length < 9" class="upload-trigger" @click="triggerUpload">
              <input ref="fileInput" type="file" multiple accept="image/jpeg,image/png,image/webp" @change="handleFileChange" style="display:none" />
              <i class="fa-solid fa-plus"></i>
              <span>{{ isDragging ? '释放以上传' : '上传图片' }}</span>
            </div>
          </div>
          <p class="image-tip">支持 jpg / jpeg / png / webp，单张不超过 5MB，最多 9 张</p>
        </div>
      </div>

      <div class="form-item image-form-item">
        <label>房源视频</label>
        <div class="video-upload-wrap">
          <div class="video-list">
            <div v-for="(video, index) in videoList" :key="index" class="video-preview-item">
              <video :src="video.preview" controls></video>
              <div class="video-actions">
                <span class="video-name">{{ video.name }}</span>
                <button class="action-btn delete-btn" @click="removeVideo(index)">
                  <i class="fa-solid fa-xmark"></i>
                </button>
              </div>
            </div>
          </div>
          <div v-if="videoList.length < maxVideos" class="upload-trigger" @click="triggerVideoUpload">
            <input ref="videoInput" type="file" accept="video/mp4" @change="handleVideoChange" style="display:none" />
            <i class="fa-solid fa-video"></i>
            <span>上传视频</span>
          </div>
          <p class="image-tip">支持 mp4 格式，单个不超过 200MB，最多 {{ maxVideos }} 个</p>
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
import { uploadHouseImage, deleteHouseImage, updateHouseImage } from '@/api/houseImage.js'
import { uploadHouseVideo, getHouseVideos, deleteHouseVideo } from '@/api/houseVideo.js'
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

// 图片上传
const fileInput = ref(null)
const imageList = ref([])
const isDragging = ref(false)
const MAX_IMAGES = 9
const MAX_FILE_SIZE = 5 * 1024 * 1024

const triggerUpload = () => {
  fileInput.value?.click()
}

const handleFileChange = (e) => {
  processFiles(Array.from(e.target.files))
  e.target.value = ''
}

const handleDragOver = (e) => {
  isDragging.value = true
}

const handleDragLeave = (e) => {
  const rect = e.currentTarget.getBoundingClientRect()
  if (
    e.clientX <= rect.left ||
    e.clientX >= rect.right ||
    e.clientY <= rect.top ||
    e.clientY >= rect.bottom
  ) {
    isDragging.value = false
  }
}

const handleDrop = (e) => {
  isDragging.value = false
  const files = Array.from(e.dataTransfer.files).filter(file => 
    file.type.startsWith('image/')
  )
  processFiles(files)
}

const processFiles = (files) => {
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
}

const setCover = async (index) => {
  const img = imageList.value[index]
  if (!img) return
  
  imageList.value.forEach((item, i) => {
    item.isCover = (i === index)
  })
  
  if (img.id && isEdit.value) {
    try {
      await updateHouseImage(houseId.value, img.id, { is_cover: true })
    } catch (e) {
      ElMessage.error('设置封面失败')
      console.error(e)
    }
  }
}

const removeImage = async (index) => {
  const removed = imageList.value[index]
  if (!removed) return
  
  if (removed.id && isEdit.value) {
    try {
      await deleteHouseImage(houseId.value, removed.id)
    } catch (e) {
      ElMessage.error('删除图片失败')
      console.error(e)
      return
    }
  }
  
  if (removed?.preview && !removed.id) {
    URL.revokeObjectURL(removed.preview)
  }
  imageList.value.splice(index, 1)
  if (removed?.isCover && imageList.value.length > 0) {
    imageList.value[0].isCover = true
    if (imageList.value[0].id && isEdit.value) {
      try {
        await updateHouseImage(houseId.value, imageList.value[0].id, { is_cover: true })
      } catch (e) {
        console.error(e)
      }
    }
  }
}

// 视频上传
const videoInput = ref(null)
const videoList = ref([])
const maxVideos = 5
const MAX_VIDEO_SIZE = 200 * 1024 * 1024

const triggerVideoUpload = () => {
  videoInput.value?.click()
}

const handleVideoChange = (e) => {
  const files = Array.from(e.target.files)
  e.target.value = ''

  const remaining = maxVideos - videoList.value.length

  files.slice(0, remaining).forEach(file => {
    if (file.size > MAX_VIDEO_SIZE) {
      ElMessage.warning(`${file.name} 超过200MB限制`)
      return
    }
    const ext = file.name.split('.').pop().toLowerCase()
    if (ext !== 'mp4') {
      ElMessage.warning(`${file.name} 格式不支持，仅支持mp4`)
      return
    }
    const preview = URL.createObjectURL(file)
    videoList.value.push({
      file,
      preview,
      name: file.name
    })
  })

  if (files.length > remaining) {
    ElMessage.warning(`最多还能上传${remaining}个视频`)
  }
}

const removeVideo = (index) => {
  const removed = videoList.value[index]
  if (!removed) return

  if (removed.id) {
    deleteHouseVideo(houseId.value, removed.id).catch(e => {
      ElMessage.error('删除视频失败')
      console.error(e)
    })
  }

  if (removed?.preview && !removed.id) {
    URL.revokeObjectURL(removed.preview)
  }
  videoList.value.splice(index, 1)
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
      
      // 预填图片（从详情接口获取的图片列表）
      if (data.images && data.images.length > 0) {
        imageList.value = data.images.map((img, index) => ({
          preview: img,
          isCover: index === 0 || img === data.cover_image_url
        }))
      }
      
      // 如果是编辑模式，尝试从专门的图片列表接口获取完整信息
      if (isEdit.value) {
        try {
          const imagesRes = await service.get(`/v1/houses/${houseId.value}/images`)
          if (imagesRes.code === 0 && imagesRes.data.length > 0) {
            imageList.value = imagesRes.data.map(img => ({
              id: img.id,
              preview: img.url,
              isCover: img.is_cover
            }))
          }
        } catch (e) {
          console.error('获取图片列表失败:', e)
        }

        // 加载已有视频
        try {
          const videosRes = await getHouseVideos(houseId.value)
          if (videosRes.code === 0 && videosRes.data.length > 0) {
            videoList.value = videosRes.data.map(v => ({
              id: v.id,
              preview: v.url,
              name: v.url.split('/').pop()
            }))
          }
        } catch (e) {
          console.error('获取视频列表失败:', e)
        }
      }
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
    if (targetHouseId && videoList.value.length > 0) {
      await uploadVideos(targetHouseId)
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

const uploadVideos = async (houseId) => {
  for (const video of videoList.value) {
    if (video.id) continue // 已上传过的跳过
    const formData = new FormData()
    formData.append('file', video.file)
    try {
      await uploadHouseVideo(houseId, formData)
    } catch (e) {
      console.error('上传视频失败:', e)
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

.image-form-item {
  align-items: flex-start;
}

.image-form-item label {
  padding-top: 10px;
}

.image-upload-wrap {
  flex: 1;
}

.image-tip {
  margin: 8px 0 0;
  color: #9399a5;
  font-size: 12px;
}

.image-upload-area {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  min-height: 120px;
  padding: 16px;
  border-radius: 8px;
  transition: all 0.2s;
}

.image-upload-area.dragging {
  background: #f0f7ff;
  border: 2px dashed #3072f6;
}

.image-preview-item {
  position: relative;
  aspect-ratio: 16 / 11;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e0e0e0;
}

.image-preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-tag {
  position: absolute;
  top: 8px;
  left: 8px;
  background: #3072f6;
  color: #fff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.image-actions {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: flex-end;
  padding: 6px;
  background: transparent;
}

.action-btn {
  padding: 4px 10px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
}

.cover-btn {
  background: rgba(255, 255, 255, 0.9);
  color: #333;
}

.delete-btn {
  background: rgba(255, 77, 79, 0.9);
  color: #fff;
  width: 24px;
  height: 24px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  margin-left: auto;
}

.upload-trigger {
  aspect-ratio: 4 / 3;
  border: 2px dashed #d0d0d0;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s;
  color: #999;
}

.upload-trigger:hover {
  border-color: #3072f6;
  color: #3072f6;
  background: #f8faff;
}

.upload-trigger i {
  font-size: 28px;
}

.upload-trigger span {
  font-size: 14px;
}

/* 视频上传 */
.video-upload-wrap {
  flex: 1;
}

.video-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
}

.video-preview-item {
  width: 260px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.video-preview-item video {
  width: 100%;
  max-height: 160px;
  object-fit: cover;
  display: block;
}

.video-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  background: #fafafa;
}

.video-name {
  font-size: 12px;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  margin-right: 8px;
}

.video-upload-wrap .upload-trigger {
  width: 260px;
  aspect-ratio: 16 / 9;
}
</style>