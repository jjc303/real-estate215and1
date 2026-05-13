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
              </div>
              <p class="user-role">{{ roleLabels[userStore.userRole] }}</p>
            </div>
          </div>

          <div class="stats-row">
            <div class="stat-item">
              <span class="stat-value">{{ stats.houses }}</span>
              <span class="stat-label">已发布房源</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-value">{{ stats.inquiries }}</span>
              <span class="stat-label">本月咨询</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-value">{{ stats.contracts }}</span>
              <span class="stat-label">已签合同</span>
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
            <i :class="item.icon"></i>
            <span>{{ item.label }}</span>
          </div>
        </div>
        </div>

        <div class="profile-content">
        <div class="content-card" v-if="activeMenu === 'basic'">
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

        <div class="content-card" v-if="activeMenu === 'security'">
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

          <div class="card-divider"></div>

          <div class="form-section">
            <h3 class="section-title">绑定设置</h3>
            <div class="bind-list">
              <div class="bind-item">
                <div class="bind-info">
                  <div class="bind-icon phone-icon">
                    <i class="fa-solid fa-mobile-screen-button"></i>
                  </div>
                  <div class="bind-text">
                    <span class="bind-label">手机号绑定</span>
                    <span class="bind-status" :class="basicForm.phone ? 'bound' : 'unbound'">
                      {{ basicForm.phone ? '已绑定' : '未绑定' }}
                    </span>
                  </div>
                </div>
                <el-button size="small" :type="basicForm.phone ? '' : 'primary'">
                  {{ basicForm.phone ? '更换' : '绑定' }}
                </el-button>
              </div>

              <div class="bind-item">
                <div class="bind-info">
                  <div class="bind-icon email-icon">
                    <i class="fa-solid fa-envelope"></i>
                  </div>
                  <div class="bind-text">
                    <span class="bind-label">邮箱绑定</span>
                    <span class="bind-status" :class="basicForm.email ? 'bound' : 'unbound'">
                      {{ basicForm.email ? '已绑定' : '未绑定' }}
                    </span>
                  </div>
                </div>
                <el-button size="small" :type="basicForm.email ? '' : 'primary'">
                  {{ basicForm.email ? '更换' : '绑定' }}
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <div class="content-card" v-if="activeMenu === 'preferences'">
          <div class="card-header">
            <div class="card-icon preferences-icon">
              <i class="fa-solid fa-gear"></i>
            </div>
            <div class="card-title-wrap">
              <h2 class="card-title">偏好设置</h2>
              <p class="card-desc">自定义您的通知偏好</p>
            </div>
          </div>

          <div class="form-section">
            <div class="switch-list">
              <div class="switch-item">
                <div class="switch-info">
                  <i class="fa-solid fa-bell"></i>
                  <div class="switch-text">
                    <span class="switch-label">消息通知</span>
                    <span class="switch-desc">接收站内消息提醒</span>
                  </div>
                </div>
                <el-switch v-model="preferences.notification" active-text="开启" inactive-text="关闭" />
              </div>
              <div class="switch-item">
                <div class="switch-info">
                  <i class="fa-solid fa-envelope"></i>
                  <div class="switch-text">
                    <span class="switch-label">邮件提醒</span>
                    <span class="switch-desc">接收邮件通知</span>
                  </div>
                </div>
                <el-switch v-model="preferences.emailAlert" active-text="开启" inactive-text="关闭" />
              </div>
              <div class="switch-item">
                <div class="switch-info">
                  <i class="fa-solid fa-sms"></i>
                  <div class="switch-text">
                    <span class="switch-label">短信提醒</span>
                    <span class="switch-desc">接收重要短信通知</span>
                  </div>
                </div>
                <el-switch v-model="preferences.smsAlert" active-text="开启" inactive-text="关闭" />
              </div>
            </div>
          </div>

          <div class="form-actions">
            <el-button type="primary" @click="savePreferences">保存设置</el-button>
          </div>
        </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user.js'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const avatarInput = ref(null)
const activeMenu = ref('basic')
const loading = ref(false)

const roleLabels = {
  tenant: '租客',
  landlord: '房东',
  admin: '管理员'
}

const menuItems = [
  { key: 'basic', label: '基本信息', icon: 'fa-solid fa-user' },
  { key: 'security', label: '账号安全', icon: 'fa-solid fa-shield-halved' },
  { key: 'preferences', label: '偏好设置', icon: 'fa-solid fa-gear' }
]

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

const preferences = reactive({
  notification: true,
  emailAlert: true,
  smsAlert: false
})

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

const changePassword = () => {
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
  
  ElMessage.success('密码修改成功，请重新登录')
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
}

const savePreferences = () => {
  ElMessage.success('偏好设置保存成功')
}

onMounted(() => {
  loadUserInfo()
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
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 24px;
  cursor: pointer;
  transition: all 0.25s ease;
  font-size: 15px;
  color: #64748b;
}

.menu-item:hover {
  background: #e2e8f0;
  color: #64748b;
}

.menu-item.active {
  background: linear-gradient(90deg, #e2e8f0 0%, #f1f5f9 100%);
  color: #475569;
  border-right: 3px solid #64748b;
}

.menu-item i {
  width: 20px;
  font-size: 16px;
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
</style>
