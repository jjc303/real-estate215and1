<template>
<template v-if="!userStore.isLoggedIn">
  <button class="btn-login" @click="userStore.openLoginModal">
    <i class="fa-solid fa-user"></i> <span>登录</span>
  </button>
  <button class="btn-register" @click="userStore.openRegisterModal">
    <i class="fa-solid fa-user-plus"></i> <span>注册</span>
  </button>
</template>
<template v-else>
  <button class="btn-notification" @click="showChatPopup = true">
    <i class="fa-solid fa-bell"></i>
    <span class="notification-badge" v-if="unreadCount > 0">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
  </button>
  
  <div class="username">
    <router-link to="/profile" class="profile-link">
      <i class="fa-solid fa-user-shield"></i>
      <span>{{ userStore.userName }}</span>
    </router-link>
  </div>
  
  <button class="btn-logout" @click="userStore.logout">
    <i class="fa-solid fa-right-from-bracket"></i> 退出
  </button>
  
  <ChatPopup v-model:visible="showChatPopup" @update:unread-count="updateUnreadCount" />
</template>
</template>


<script setup>
import { ref, onMounted, watch } from 'vue';
import { useUserStore } from '@/stores/user.js';
import ChatPopup from '@/components/ChatPopup.vue';
import { getConversationList } from '@/api/conversation';

const userStore = useUserStore();
const showChatPopup = ref(false);
const unreadCount = ref(0);

const fetchUnreadCount = async () => {
  try {
    const res = await getConversationList();
    if (res.code === 0 && res.data) {
      const list = res.data.list || [];
      unreadCount.value = list.reduce((sum, item) => sum + (item.unread_count || 0), 0);
    }
  } catch (error) {
    console.error('获取未读消息数失败:', error);
  }
};

const updateUnreadCount = (count) => {
  // 直接使用传入的计数值
  unreadCount.value = count;
};

// 监听聊天窗口打开，重新获取未读消息数
watch(() => showChatPopup.value, async (newVal) => {
  if (newVal) {
    // 打开聊天窗口时重新获取未读消息数
    await fetchUnreadCount();
  }
});

onMounted(() => {
  if (userStore.isLoggedIn) {
    fetchUnreadCount();
  }
});
</script>
<style scoped>

button {
  border: none;
  outline: none;
  cursor: pointer;
  font-family: inherit;
}

.btn-notification {
  position: relative;
  width: 40px;
  height: 40px;
  background: transparent;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 20px;
  transition: all 0.2s ease;
  padding: 0;
  margin: 0;
  line-height: 1;
}

.btn-notification:hover {
  background: rgba(255, 255, 255, 0.15);
}

.notification-badge {
  position: absolute;
  top: -2px;
  right: -2px;
  min-width: 18px;
  height: 18px;
  background: #ff4d4f;
  color: #fff;
  font-size: 12px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
}
/* 登录按钮 */
.btn-login {
  padding: 10px 15px;
  font-size: 18px;
  color: #fff;
  background: transparent;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.25s ease;
}
.btn-login:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-1px);
}

/* 注册按钮（主按钮） */

.btn-register{
  padding: 10px 15px;
  font-size: 18px;
  color: #fff;
  background: transparent;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.25s ease;
}
.btn-register:hover {
  background: #0753ab;
  transform: translateY(-1px);
}

/* 退出按钮 */
.btn-logout {
  padding: 8px 16px;
  font-size: 18px;
  color: #ff4d4f;
  background: transparent;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: color 0.2s ease;
}
.btn-logout:hover {
  color: #d9363e;
}
.username{
  display: flex;
  align-items: center;
}
/* 用户名 */
.username .profile-link {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  color: #fff;
  font-weight: 500;
  margin-right: 0px;
  text-decoration: none;
  padding: 6px 12px;
  border-radius: 6px;
  transition: all 0.2s ease;
}
.username .profile-link:hover {
  background: rgba(255, 255, 255, 0.15);
}
.username .profile-link i {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e0f2fe 0%, #7dd3fc 100%);
  color: #0369a1;
  border-radius: 50%;
  font-size: 18px;
  box-shadow: 0 4px 12px rgba(125, 211, 252, 0.4);
  transition: all 0.3s ease;
}

.username .profile-link:hover i {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(125, 211, 252, 0.6);
}
</style>