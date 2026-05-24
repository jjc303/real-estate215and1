<template>
  <div class="profile-container">
    <div class="profile-inner">
      <div class="welcome-banner">
        <div class="welcome-content">
          <h1 class="welcome-title">欢迎回来，{{ userStore.userRole === 'landlord' ? '房东' : '租客' }}先生/女士</h1>
          <p class="welcome-desc">管理您的账户信息</p>
        </div>
      </div>

      <div class="profile-main">
        <div class="profile-sidebar">
          <div class="user-card">
          <div class="user-avatar-section">
            <div class="avatar-wrapper">
              <img :src="avatarUrl" alt="头像" class="user-avatar" />
              <div class="avatar-overlay" @click="handleAvatarUpload">
                <i class="fa-solid fa-camera"></i>
              </div>
            </div>
            <input type="file" ref="avatarInput" accept="image/*" @change="handleAvatarChange" hidden />
            
            <div class="user-info">
              <div class="user-name-row">
                <h3 class="user-name">{{ userStore.userName || '用户' }}</h3>
                <div v-if="userStore.userRole === 'landlord'" class="landlord-badge">
                  <i class="fa-solid fa-home"></i>
                  <span>房东</span>
                </div>
                <div v-else-if="userStore.userRole === 'tenant'" class="tenant-badge">
                  <i class="fa-solid fa-user"></i>
                  <span>租客</span>
                </div>
              </div>
              <p class="user-role">{{ roleLabels[userStore.userRole] }}</p>
            </div>
          </div>

          <div class="stats-row">
            <div class="stat-item">
              <span class="stat-value">{{ userStore.userRole === 'landlord' ? stats.houses : collections.length }}</span>
              <span class="stat-label">{{ userStore.userRole === 'landlord' ? '已发布房源' : '收藏房源' }}</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-value">{{ stats.inquiries }}</span>
              <span class="stat-label">{{ userStore.userRole === 'landlord' ? '本月咨询' : '预约成功数' }}</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-value">{{ stats.contracts }}</span>
              <span class="stat-label">{{ userStore.userRole === 'landlord' ? '已签合同' : '已租房屋' }}</span>
            </div>
          </div>
        </div>

        <div class="menu-list">
          <div 
            v-for="item in menuItems" 
            :key="item.key"
            class="menu-item"
            :class="{ active: activeMenu === item.key }"
            @click="activeMenu = item.key"
          >
            <span class="menu-indicator"></span>
            <i :class="item.icon"></i>
            <span>{{ item.label }}</span>
          </div>
        </div>
        </div>

        <div class="profile-content">
          <transition name="fade-slide" mode="out-in">
            <template v-if="activeMenu === 'basic'" :key="'basic'">
              <div class="content-card">
                <div class="card-header">
                  <div class="card-icon basic-icon">
                    <i class="fa-solid fa-user"></i>
                  </div>
                  <div class="card-title-wrap">
                    <h2 class="card-title">账户信息</h2>
                    <p class="card-desc">管理您的基本个人信息</p>
                  </div>
                </div>
                
                <div class="form-section">
                  <div class="form-group">
                    <div class="form-item">
                      <label class="form-label">
                        <i class="fa-solid fa-user"></i>
                        <span>用户名</span>
                      </label>
                      <el-input v-model="basicForm.username" placeholder="用户名不可修改" disabled />
                    </div>
                    <div class="form-item">
                      <label class="form-label">
                        <i class="fa-solid fa-user-check"></i>
                        <span>真实姓名</span>
                      </label>
                      <el-input v-model="basicForm.nickname" placeholder="请输入真实姓名" />
                    </div>
                  </div>
                </div>

                <div class="card-divider"></div>

                <div class="form-section">
                  <h3 class="section-title">联系方式</h3>
                  <div class="form-group">
                    <div class="form-item">
                      <label class="form-label">
                        <i class="fa-solid fa-phone"></i>
                        <span>手机号</span>
                      </label>
                      <el-input v-model="basicForm.phone" placeholder="请输入手机号" />
                    </div>
                    <div class="form-item">
                      <label class="form-label">
                        <i class="fa-solid fa-envelope"></i>
                        <span>邮箱</span>
                      </label>
                      <el-input v-model="basicForm.email" placeholder="请输入邮箱" />
                    </div>
                  </div>
                </div>

                <div class="form-actions">
                  <el-button type="primary" @click="saveBasicInfo">保存更改</el-button>
                  <el-button @click="resetBasicForm">取消</el-button>
                </div>
              </div>
            </template>

            <template v-else-if="activeMenu === 'security'" :key="'security'">
              <div class="content-card">
                <div class="card-header">
                  <div class="card-icon security-icon">
                    <i class="fa-solid fa-shield-halved"></i>
                  </div>
                  <div class="card-title-wrap">
                    <h2 class="card-title">安全设置</h2>
                    <p class="card-desc">保护您的账户安全</p>
                  </div>
                </div>

                <div class="form-section">
                  <h3 class="section-title">修改密码</h3>
                  <div class="form-group">
                    <div class="form-item">
                      <label class="form-label">
                        <i class="fa-solid fa-key"></i>
                        <span>原密码</span>
                      </label>
                      <el-input v-model="passwordForm.oldPassword" type="password" placeholder="请输入原密码" show-password />
                    </div>
                    <div class="form-item">
                      <label class="form-label">
                        <i class="fa-solid fa-lock"></i>
                        <span>新密码</span>
                      </label>
                      <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" show-password />
                    </div>
                    <div class="form-item">
                      <label class="form-label">
                        <i class="fa-solid fa-lock-open"></i>
                        <span>确认新密码</span>
                      </label>
                      <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
                    </div>
                  </div>
                  <div class="form-actions">
                    <el-button type="primary" @click="changePassword">修改密码</el-button>
                  </div>
                </div>
              </div>
            </template>

            <!-- 我的租房 -->
            <template v-else-if="activeMenu === 'rentals'" :key="'rentals'">
              <div class="content-card">
                <div class="card-header">
                  <div class="card-icon rentals-icon">
                    <i class="fa-solid fa-home"></i>
                  </div>
                  <div class="card-title-wrap">
                    <h2 class="card-title">我的租房</h2>
                    <p class="card-desc">生效合同的房源信息</p>
                  </div>
                </div>

                <div class="form-section">
                  <div v-if="rentals.length === 0" class="empty-state">
                    <i class="fa-solid fa-home"></i>
                    <p>暂无生效的租房合同</p>
                  </div>
                  <div v-else class="rental-list">
                    <div v-for="item in rentals" :key="item.id" class="rental-item" @click="goToHouseDetail(item.houseId)">
                      <div class="rental-info">
                        <div class="rental-header">
                          <h4 class="rental-title">{{ item.title }}</h4>
                          <p class="rental-price">{{ item.price }}</p>
                        </div>
                        <div class="rental-meta">
                          <span><i class="fa-solid fa-map-marker"></i>{{ item.district }}</span>
                          <span><i class="fa-solid fa-home"></i>{{ item.houseType }}</span>
                          <span><i class="fa-solid fa-maximize"></i>{{ item.area }}㎡</span>
                        </div>
                        <div class="rental-address">
                          <i class="fa-solid fa-location-dot"></i>{{ item.address }}
                        </div>
                        <div class="rental-period">
                          <i class="fa-solid fa-calendar-days"></i>租期：{{ item.startDate }} 至 {{ item.endDate }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </template>

            <!-- 我的收藏 -->
            <template v-else-if="activeMenu === 'collections'" :key="'collections'">
              <div class="content-card">
                <div class="card-header">
                  <div class="card-icon collections-icon">
                    <i class="fa-solid fa-heart"></i>
                  </div>
                  <div class="card-title-wrap">
                    <h2 class="card-title">我的收藏</h2>
                    <p class="card-desc">收藏的房源信息</p>
                  </div>
                </div>

                <div class="form-section">
                  <div v-if="collections.length === 0" class="empty-state">
                    <i class="fa-solid fa-heart-broken"></i>
                    <p>暂无收藏的房源</p>
                  </div>
                  <div v-else class="collection-list">
                    <div v-for="item in collections" :key="item.id" class="rental-item" @click="goToHouseDetail(item.id)">
                      <div class="rental-info">
                        <h4 class="rental-title">{{ item.title }}</h4>
                        <div class="rental-meta">
                          <span><i class="fa-solid fa-map-marker"></i>{{ item.district }}</span>
                          <span><i class="fa-solid fa-home"></i>{{ item.houseType }}</span>
                          <span><i class="fa-solid fa-maximize"></i>{{ item.area }}㎡</span>
                        </div>
                        <div class="rental-address">
                          <i class="fa-solid fa-location-dot"></i>{{ item.address }}
                        </div>
                      </div>
                      <div class="collection-right">
                        <p class="rental-price">{{ item.price }}</p>
                        <button class="uncollect-btn" @click.stop="removeCollection(item.id)">
                          <i class="fa-solid fa-heart-crack"></i>
                          <span>取消收藏</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user.js'
import { ElMessage } from 'element-plus'
import { computed } from 'vue';
import { useRouter } from 'vue-router'
import { getFavoriteList, removeFavorite } from '@/api/favorite.js'
import { getContractList } from '@/api/contract.js'
import { getHouseDetail } from '@/api/house.js'
import { mockFavorites } from '@/mock/favorites'
import service from '@/utils/request'

// 是否使用模拟数据
const USE_MOCK_DATA = false

const userStore = useUserStore()
const router = useRouter()
const avatarInput = ref(null)
const activeMenu = ref('basic')
const loading = ref(false)

const roleLabels = {
  tenant: '租客',
  landlord: '房东',
  admin: '管理员'
}

const menuItems = computed(() => {
  const items = [
    { key: 'basic', label: '基本信息', icon: 'fa-solid fa-user' },
    { key: 'security', label: '账号安全', icon: 'fa-solid fa-shield-halved' }
  ]
  // 租客端显示我的租房和收藏
  if (userStore.userRole === 'tenant') {
    items.push({ key: 'rentals', label: '我的租房', icon: 'fa-solid fa-home' })
    items.push({ key: 'collections', label: '我的收藏', icon: 'fa-solid fa-heart' })
  } else {
    // 房东端只显示收藏
    items.push({ key: 'collections', label: '我的收藏', icon: 'fa-solid fa-heart' })
  }
  return items
})

const avatarUrl = ref('https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png')

const stats = reactive({
  houses: 3,
  inquiries: 12,
  contracts: 1
})

const basicForm = reactive({
  username: '',
  nickname: '',
  gender: 'other',
  phone: '',
  email: '',
  bio: ''
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 租房列表（生效合同的房源）
const rentals = ref([])

const loadRentals = async () => {
  try {
    const res = await getContractList({
      page: 1,
      page_size: 100
    })
    console.log('合同列表API响应:', res)
    
    // 放宽响应结构验证
    const items = res && res.data 
      ? (Array.isArray(res.data) ? res.data : (res.data.items || res.data.list || []))
      : []
    console.log('合同列表items:', items)
    
    // 过滤出生效状态的合同（支持多种状态值）
    const activeContracts = items.filter(item => 
      item.status === 'active' || item.status === '生效' || item.status === 1
    )
    console.log('生效合同数量:', activeContracts.length)
    console.log('生效合同详情:', activeContracts)
    
    // 批量获取房源信息
    const rentalList = []
    for (const contract of activeContracts) {
      try {
        const houseRes = await getHouseDetail(contract.house_id)
        console.log(`获取房源${contract.house_id}详情:`, houseRes)
        
        if (houseRes && (houseRes.code === 0 || houseRes.data)) {
          const houseData = houseRes.data || {}
          rentalList.push({
            id: contract.id,
            houseId: contract.house_id,
            title: houseData.title || contract.house?.title || '未知房源',
            price: contract.monthly_rent || houseData.rent || 0,
            district: houseData.region || contract.house?.region || '',
            houseType: houseData.house_type || contract.house?.house_type || '',
            area: parseFloat(houseData.area) || parseFloat(contract.house?.area) || 0,
            address: houseData.address || contract.house?.address || '',
            startDate: contract.start_date || '',
            endDate: contract.end_date || '',
            image: houseData.images?.[0] || ''
          })
        } else {
          // 如果获取房源详情失败，使用合同中的房源信息
          rentalList.push({
            id: contract.id,
            houseId: contract.house_id,
            title: contract.house?.title || '未知房源',
            price: contract.monthly_rent || 0,
            district: contract.house?.region || '',
            houseType: contract.house?.house_type || '',
            area: parseFloat(contract.house?.area) || 0,
            address: contract.house?.address || '',
            startDate: contract.start_date || '',
            endDate: contract.end_date || '',
            image: ''
          })
        }
      } catch (error) {
        console.error(`获取房源${contract.house_id}详情失败:`, error)
        // 获取房源详情失败，使用合同中的房源信息
        rentalList.push({
          id: contract.id,
          houseId: contract.house_id,
          title: contract.house?.title || '未知房源',
          price: contract.monthly_rent || 0,
          district: contract.house?.region || '',
          houseType: contract.house?.house_type || '',
          area: parseFloat(contract.house?.area) || 0,
          address: contract.house?.address || '',
          startDate: contract.start_date || '',
          endDate: contract.end_date || '',
          image: ''
        })
      }
    }
    console.log('最终租房列表:', rentalList)
    rentals.value = rentalList
  } catch (error) {
    console.error('加载租房列表失败', error)
    // 使用模拟数据
    rentals.value = [
      {
        id: 1,
        houseId: 1,
        title: '温馨三居室',
        price: 3500,
        district: '朝阳区',
        houseType: '三室两厅',
        area: 120,
        address: '朝阳区幸福路88号',
        startDate: '2024-01-01',
        endDate: '2025-01-01',
        image: '/images/house1.jpg'
      }
    ]
  }
}

// 收藏列表（房源收藏）
const collections = ref([])

const loadCollections = async () => {
  try {
    if (USE_MOCK_DATA) {
      // 使用模拟数据
      collections.value = mockFavorites.map(item => ({
        id: item.house_id,
        title: item.house?.title || '',
        price: item.house?.rent || '',
        district: item.house?.region || '',
        area: item.house?.area || '',
        address: item.house?.address || '',
        houseType: item.house?.house_type || '',
        createdAt: item.favorite_created_at || ''
      }))
    } else {
      // 使用真实API
      const res = await getFavoriteList()
      if (res.code === 0 && res.data) {
        // 确保 res.data 是数组
        const dataArray = Array.isArray(res.data) ? res.data : (res.data.list || [])
        // 后端返回的结构是 { house_id, house: {...} }
        collections.value = dataArray.map(item => ({
          id: item.house_id,
          title: item.house?.title || '',
          price: item.house?.rent || '',
          district: item.house?.region || '',
          area: item.house?.area || '',
          address: item.house?.address || '',
          houseType: item.house?.house_type || '',
          createdAt: item.favorite_created_at || ''
        }))
      } else {
        collections.value = []
      }
    }
  } catch (error) {
    console.error('加载收藏列表失败', error)
    collections.value = []
  }
}

const removeCollection = async (houseId) => {
  try {
    if (USE_MOCK_DATA) {
      // 使用模拟数据，直接删除
      collections.value = collections.value.filter(item => item.id !== houseId)
      ElMessage.success('已取消收藏')
    } else {
      // 使用真实API
      const res = await removeFavorite(houseId)
      if (res.code === 0) {
        collections.value = collections.value.filter(item => item.id !== houseId)
        ElMessage.success('已取消收藏')
      } else {
        ElMessage.error(res.message || '取消收藏失败')
      }
    }
  } catch (error) {
    console.error('取消收藏失败', error)
    ElMessage.error('取消收藏失败')
  }
}

// 跳转至房源详情
const goToHouseDetail = (houseId) => {
  router.push(`/houseDetail/${houseId}`)
}

const loadUserInfo = async () => {
  loading.value = true
  try {
    await userStore.fetchCurrentUser()
    if (userStore.userInfo) {
      basicForm.username = userStore.userInfo.username || ''
      basicForm.nickname = userStore.userInfo.real_name || ''
      basicForm.phone = userStore.userInfo.phone || ''
      basicForm.email = userStore.userInfo.email || ''
      avatarUrl.value = userStore.userAvatar || 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
    }
  } catch (e) {
    console.error('加载用户信息失败', e)
  } finally {
    loading.value = false
  }
}

const handleAvatarUpload = () => {
  avatarInput.value.click()
}

const handleAvatarChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = async (event) => {
      avatarUrl.value = event.target.result
      
      const avatarBase64 = event.target.result
      if (avatarBase64.length > 255) {
        ElMessage.warning('头像链接超过255字符限制，请使用短链接头像')
        console.warn('头像base64长度超过限制:', avatarBase64.length, '字符')
        return
      }
      
      try {
        await userStore.updateCurrentUser({ avatar: avatarBase64 })
        await loadUserInfo()
      } catch (err) {
        console.error('头像更新失败', err)
      }
    }
    reader.readAsDataURL(file)
  }
}

const validatePhone = (phone) => {
  if (!phone) return true
  const phoneRegex = /^1[3-9]\d{9}$/
  return phoneRegex.test(phone)
}

const validateEmail = (email) => {
  if (!email) return true
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const saveBasicInfo = async () => {
  try {
    if (basicForm.phone && !validatePhone(basicForm.phone)) {
      ElMessage.warning('请输入正确的手机号')
      return
    }
    
    if (basicForm.email && !validateEmail(basicForm.email)) {
      ElMessage.warning('请输入正确的邮箱地址')
      return
    }
    
    const payload = {}
    
    const trimmedRealName = basicForm.nickname?.trim()
    const trimmedPhone = basicForm.phone?.trim()
    const trimmedEmail = basicForm.email?.trim()
    
    if (trimmedRealName) {
      payload.real_name = trimmedRealName
    }
    
    if (trimmedPhone) {
      payload.phone = trimmedPhone
    }
    
    if (trimmedEmail) {
      payload.email = trimmedEmail
    }
    
    if (Object.keys(payload).length === 0) {
      ElMessage.info('没有需要修改的信息')
      return
    }
    
    await userStore.updateCurrentUser(payload)
    await loadUserInfo()
    ElMessage.success('信息保存成功')
  } catch (err) {
    console.error('保存失败', err)
    ElMessage.error('保存失败，请稍后重试')
  }
}

const resetBasicForm = async () => {
  await loadUserInfo()
  ElMessage.info('已取消修改')
}

const changePassword = async () => {
  if (!passwordForm.oldPassword) {
    ElMessage.warning('请输入原密码')
    return
  }
  if (!passwordForm.newPassword) {
    ElMessage.warning('请输入新密码')
    return
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  if (passwordForm.newPassword.length < 6) {
    ElMessage.warning('密码长度至少6位')
    return
  }

  try {
    await service.put('/v1/users/me', { password: passwordForm.newPassword })
    ElMessage.success('密码修改成功')
    passwordForm.oldPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
  } catch (err) {
    console.error('密码修改失败', err)
    ElMessage.error(err.response?.data?.message || '密码修改失败，请稍后重试')
  }
}

onMounted(() => {
  loadUserInfo()
  loadRentals()
  loadCollections()
})
</script>

<style scoped>
.profile-container {
  width: 100vw;
  min-height: calc(100vh - 140px);
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  position: relative;
  left: 50%;
  right: 50%;
  margin-left: -50vw;
  margin-right: -50vw;
}

.profile-inner {
  display: flex;
  flex-direction: column;
  padding: 0 20px;
  gap: 24px;
  max-width: 1300px;
  margin: 0 auto;
}

.welcome-banner {
  padding: 32px 40px;
  background: linear-gradient(135deg, #64748b 0%, #94a3b8 50%, #64748b 100%);
  border-radius: 20px;
  margin-top: 24px;
  box-shadow: 0 8px 32px rgba(100, 116, 139, 0.25);
}

.welcome-content {
  color: white;
}

.welcome-title {
  font-size: 26px;
  font-weight: 600;
  margin: 0 0 8px;
}

.welcome-desc {
  font-size: 15px;
  opacity: 0.9;
  margin: 0;
}

.profile-main {
  display: flex;
  gap: 32px;
  justify-content: center;
}

.profile-sidebar {
  width: 280px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.user-card {
  background: #ffffff;
  border-radius: 20px;
  padding: 32px 24px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.user-avatar-section {
  text-align: center;
  padding-bottom: 28px;
  border-bottom: 1px solid #f1f5f9;
}

.avatar-wrapper {
  position: relative;
  width: 100px;
  height: 100px;
  margin: 0 auto 20px;
}

.user-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #fff;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.3s ease;
  cursor: pointer;
  font-size: 20px;
}

.avatar-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.avatar-wrapper:hover .user-avatar {
  transform: scale(1.02);
}

.avatar-tip {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

.user-info {
  margin-top: 24px;
}

.user-name-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.user-name {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.landlord-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  color: #92400e;
}

.tenant-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  color: #ffffff;
}

.user-role {
  font-size: 14px;
  color: #64748b;
  margin: 12px 0 0;
}

.stats-row {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 28px 0 8px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #64748b;
}

.stat-label {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: #e2e8f0;
}

.menu-list {
  background: #ffffff;
  border-radius: 20px;
  padding: 8px 0;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  margin-bottom:50px;
}

.menu-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 24px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 15px;
  color: #64748b;
  overflow: hidden;
}

.menu-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, rgba(148, 163, 184, 0.1) 0%, rgba(148, 163, 184, 0.05) 100%);
  opacity: 0;
  transform: translateX(-100%);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.menu-item:hover::before {
  opacity: 1;
  transform: translateX(0);
}

.menu-item:hover {
  color: #475569;
  transform: translateX(4px);
}

.menu-item.active {
  color: #475569;
}

.menu-indicator {
  position: absolute;
  left: 0;
  top: 50%;
  width: 4px;
  height: 24px;
  background: linear-gradient(180deg, #64748b 0%, #94a3b8 100%);
  border-radius: 0 2px 2px 0;
  transform: translateY(-50%) scaleY(0);
  opacity: 0;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.menu-item.active .menu-indicator {
  transform: translateY(-50%) scaleY(1);
  opacity: 1;
}

.menu-item.active::before {
  opacity: 1;
  transform: translateX(0);
}

.menu-item i {
  width: 20px;
  font-size: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.menu-item.active i {
  transform: scale(1.1);
  color: #64748b;
}

.profile-content {
  flex: 1;
  min-width: 500px;
  max-width: 800px;
}

.content-card {
  background: #ffffff;
  border-radius: 20px;
  padding: 0;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px 32px;
  border-bottom: 1px solid #f5f5f5;
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: white;
}

.basic-icon {
  background: linear-gradient(135deg, #64748b 0%, #94a3b8 100%);
}

.security-icon {
  background: linear-gradient(135deg, #64748b 0%, #94a3b8 100%);
}

.preferences-icon {
  background: linear-gradient(135deg, #64748b 0%, #94a3b8 100%);
}

.card-title-wrap {
  display: flex;
  flex-direction: column;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.card-desc {
  font-size: 13px;
  color: #94a3b8;
  margin: 4px 0 0;
}

.card-divider {
  height: 8px;
  background: #f8fafc;
}

.form-section {
  padding: 24px 32px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #475569;
  margin: 0 0 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #475569;
  width: 120px;
  flex-shrink: 0;
}

.form-label i {
  color: #94a3b8;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 24px 32px;
}

.form-actions .el-button {
  padding: 10px 24px;
  border-radius: 10px;
  font-weight: 500;
}

.form-actions .el-button--primary {
  background: linear-gradient(135deg, #64748b 0%, #94a3b8 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(100, 116, 139, 0.3);
}

.form-actions .el-button--primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(100, 116, 139, 0.4);
}

.form-item :deep(.el-input__wrapper) {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.form-item :deep(.el-input__wrapper:hover) {
  border-color: #cbd5e1;
}

.form-item :deep(.el-input__wrapper.is-focus) {
  border-color: #94a3b8;
  box-shadow: 0 0 0 3px rgba(148, 163, 184, 0.2);
}

.form-item :deep(.el-input__inner) {
  padding: 12px 16px;
  font-size: 15px;
}

.switch-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.switch-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: #f8fafc;
  border-radius: 12px;
}

.switch-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.switch-info i {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e2e8f0;
  color: #64748b;
  font-size: 18px;
}

.switch-text {
  display: flex;
  flex-direction: column;
}

.switch-label {
  font-size: 15px;
  font-weight: 500;
  color: #334155;
}

.switch-desc {
  font-size: 13px;
  color: #94a3b8;
}

.bind-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bind-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: #fafbfc;
  border-radius: 14px;
  border: 1px solid #f1f5f9;
}

.bind-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.bind-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.phone-icon {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #2563eb;
}

.email-icon {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
}

.bind-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.bind-label {
  font-size: 15px;
  color: #1e293b;
  font-weight: 500;
}

.bind-status {
  font-size: 13px;
}

.bind-status.bound {
  color: #10b981;
}

.bind-status.unbound {
  color: #f59e0b;
}

/* 收藏相关样式 */
.collections-icon {
  background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%);
}

.rentals-icon {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
}

/* 租房列表样式 */
.rental-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.rental-item {
  display: flex;
  align-items: stretch;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.rental-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  border-color: #3b82f6;
}

.rental-info {
  flex: 1;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.rental-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.rental-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
  line-height: 1.4;
  flex: 1;
}

.rental-price {
  font-size: 24px;
  font-weight: 700;
  color: #f56c6c;
  margin: 0;
  line-height: 1;
  white-space: nowrap;
}

.rental-price::before {
  content: '¥';
  font-size: 16px;
  font-weight: 500;
  margin-right: 2px;
}

.rental-price::after {
  content: '/月';
  font-size: 14px;
  font-weight: 400;
  margin-left: 2px;
}

.rental-meta {
  font-size: 14px;
  color: #64748b;
  margin: 0;
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.rental-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.rental-meta i {
  font-size: 12px;
}

.rental-address {
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 4px;
}

.rental-address i {
  font-size: 12px;
}

.rental-period {
  font-size: 13px;
  color: #64748b;
  margin: 0;
  padding-top: 10px;
  border-top: 1px solid #f1f5f9;
  display: flex;
  align-items: center;
  gap: 4px;
}

.rental-period i {
  font-size: 12px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #94a3b8;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 15px;
}

.collection-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.collection-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: center;
  gap: 12px;
  padding: 0 20px;
}

.uncollect-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: transparent;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  color: #64748b;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.uncollect-btn:hover {
  background: #f8fafc;
  border-color: #f87171;
  color: #f87171;
}

.uncollect-btn i {
  font-size: 14px;
}

/* 内容切换动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>
