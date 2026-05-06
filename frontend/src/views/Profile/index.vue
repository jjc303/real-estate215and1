<template>
  <div class="profile-container">
    <div class="profile-sidebar">
      <div class="user-avatar-section">
        <div class="avatar-wrapper">
          <img :src="avatarUrl" alt="头像" class="user-avatar" />
          <div class="avatar-overlay" @click="handleAvatarUpload">
            <i class="fa-solid fa-camera"></i>
            <span>更换头像</span>
          </div>
        </div>
        <input type="file" ref="avatarInput" accept="image/*" @change="handleAvatarChange" hidden />
        <h3 class="user-name">{{ userStore.userName || '用户' }}</h3>
        <p class="user-role">{{ roleLabels[userStore.userRole] }}</p>
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
        <h2 class="card-title">基本信息</h2>
        <el-form :model="basicForm" label-width="100px" class="profile-form">
          <el-form-item label="用户名">
            <el-input v-model="basicForm.username" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="昵称">
            <el-input v-model="basicForm.nickname" placeholder="请输入昵称" />
          </el-form-item>
          <el-form-item label="性别">
            <el-radio-group v-model="basicForm.gender">
              <el-radio label="male">男</el-radio>
              <el-radio label="female">女</el-radio>
              <el-radio label="other">保密</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="手机号">
            <el-input v-model="basicForm.phone" placeholder="请输入手机号" />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="basicForm.email" placeholder="请输入邮箱" />
          </el-form-item>
          <el-form-item label="个人简介">
            <el-input 
              v-model="basicForm.bio" 
              type="textarea" 
              :rows="4" 
              placeholder="介绍一下自己吧..."
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveBasicInfo">保存修改</el-button>
            <el-button @click="resetBasicForm">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="content-card" v-if="activeMenu === 'security'">
        <h2 class="card-title">账号安全</h2>
        <el-form :model="passwordForm" label-width="120px" class="profile-form">
          <el-form-item label="原密码">
            <el-input v-model="passwordForm.oldPassword" type="password" placeholder="请输入原密码" show-password />
          </el-form-item>
          <el-form-item label="新密码">
            <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" show-password />
          </el-form-item>
          <el-form-item label="确认新密码">
            <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="changePassword">修改密码</el-button>
          </el-form-item>
        </el-form>

        <div class="divider"></div>

        <h3 class="sub-title">绑定设置</h3>
        <div class="bind-item">
          <div class="bind-info">
            <i class="fa-solid fa-mobile-screen-button"></i>
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
            <i class="fa-solid fa-envelope"></i>
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

      <div class="content-card" v-if="activeMenu === 'preferences'">
        <h2 class="card-title">偏好设置</h2>
        <el-form label-width="100px" class="profile-form">
          <el-form-item label="消息通知">
            <el-switch v-model="preferences.notification" active-text="开启" inactive-text="关闭" />
          </el-form-item>
          <el-form-item label="邮件提醒">
            <el-switch v-model="preferences.emailAlert" active-text="开启" inactive-text="关闭" />
          </el-form-item>
          <el-form-item label="短信提醒">
            <el-switch v-model="preferences.smsAlert" active-text="开启" inactive-text="关闭" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="savePreferences">保存设置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useUserStore } from '@/stores/user.js'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const avatarInput = ref(null)
const activeMenu = ref('basic')

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

const basicForm = reactive({
  username: userStore.userName || '',
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

const handleAvatarUpload = () => {
  avatarInput.value.click()
}

const handleAvatarChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (event) => {
      avatarUrl.value = event.target.result
      ElMessage.success('头像上传成功')
    }
    reader.readAsDataURL(file)
  }
}

const saveBasicInfo = () => {
  if (!basicForm.username) {
    ElMessage.warning('请输入用户名')
    return
  }
  userStore.userName = basicForm.username
  ElMessage.success('基本信息保存成功')
}

const resetBasicForm = () => {
  basicForm.username = userStore.userName || ''
  basicForm.nickname = ''
  basicForm.gender = 'other'
  basicForm.phone = ''
  basicForm.email = ''
  basicForm.bio = ''
  ElMessage.info('已重置')
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
</script>

<style scoped>
.profile-container {
  display: flex;
  min-height: calc(100vh - 140px);
  background: #f5f7fa;
  padding: 40px 20px;
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
  justify-content: center;
}

.profile-sidebar {
  width: 280px;
  flex-shrink: 0;
}

.user-avatar-section {
  background: #fff;
  border-radius: 12px;
  padding: 30px 20px;
  text-align: center;
  margin-bottom: 16px;
}

.avatar-wrapper {
  position: relative;
  width: 100px;
  height: 100px;
  margin: 0 auto 16px;
}

.user-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #e8f3ff;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
  cursor: pointer;
  font-size: 12px;
  gap: 4px;
}

.avatar-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.user-name {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.user-role {
  font-size: 14px;
  color: rgb(28, 173, 226);
  background: rgba(28, 173, 226, 0.1);
  padding: 4px 12px;
  border-radius: 12px;
  display: inline-block;
}

.menu-list {
  background: #fff;
  border-radius: 12px;
  padding: 8px 0;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 24px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 15px;
  color: #666;
}

.menu-item:hover {
  background: #f5f7fa;
  color: rgb(28, 173, 226);
}

.menu-item.active {
  background: rgba(28, 173, 226, 0.1);
  color: rgb(28, 173, 226);
  border-right: 3px solid rgb(28, 173, 226);
}

.menu-item i {
  width: 20px;
  font-size: 16px;
}

.profile-content {
  flex: 0 1 700px;
  min-width: 500px;
}

.content-card {
  background: #fff;
  border-radius: 12px;
  padding: 30px;
}

.card-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
  text-align: center;
}

.sub-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
  text-align: center;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

.profile-form {
  max-width: 500px;
  margin: 0 auto;
}

.divider {
  height: 1px;
  background: #eee;
  margin: 30px auto;
  max-width: 500px;
}

.bind-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: #f9fafb;
  border-radius: 8px;
  margin-bottom: 12px;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

.bind-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bind-info i {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e8f3ff;
  border-radius: 8px;
  color: rgb(28, 173, 226);
  font-size: 18px;
}

.bind-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.bind-label {
  font-size: 15px;
  color: #333;
  font-weight: 500;
}

.bind-status {
  font-size: 13px;
}

.bind-status.bound {
  color: #52c41a;
}

.bind-status.unbound {
  color: #fa8c16;
}
</style>
