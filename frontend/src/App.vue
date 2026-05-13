<template>
  <Header v-if="!route?.meta?.hideHeader" />

  <router-view />
  
</template>

<script setup>
import { onMounted } from 'vue';
import { useRoute } from 'vue-router';
import Header from '@/components/Header.vue';
import { useUserStore } from '@/stores/user.js';

const route = useRoute()
const userStore = useUserStore()

// 刷新页面时恢复登录状态
onMounted(async () => {
  const token = localStorage.getItem('token')
  // 如果有 token 但状态显示未登录，则恢复登录状态
  if (token && !userStore.isLoggedIn) {
    try {
      await userStore.fetchCurrentUser()
    } catch (e) {
      // token 可能过期了，清除无效 token
      localStorage.removeItem('token')
    }
  }
})

</script>

<style>
/* 美化 Element Plus 消息提示 */
:root {
  --el-message-success-bg-color: #f0fdf4;
  --el-message-success-border-color: #86efac;
  --el-message-warning-bg-color: #fffbeb;
  --el-message-warning-border-color: #fcd34d;
  --el-message-error-bg-color: #fef2f2;
  --el-message-error-border-color: #fca5a5;
}

.el-message {
  border-radius: 12px !important;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12) !important;
  border: 1px solid;
  padding: 16px 24px !important;
  backdrop-filter: blur(10px);
}

.el-message--success {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%) !important;
  border-color: #86efac !important;
}

.el-message--warning {
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%) !important;
  border-color: #fcd34d !important;
}

.el-message--error {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%) !important;
  border-color: #fca5a5 !important;
}

.el-message .el-message__content {
  font-weight: 500;
  font-size: 14px;
}
</style>
