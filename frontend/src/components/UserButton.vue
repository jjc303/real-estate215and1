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
  <div class="username">
    <span>{{ userStore.userName }}</span>
  </div>
  
  <button class="btn-logout" @click="userStore.logout">
    <i class="fa-solid fa-right-from-bracket"></i> 退出
  </button>
</template>
</template>


<script setup>
import { useUserStore } from '@/stores/user.js';
const userStore = useUserStore();
</script>
<style scoped>

button {
  border: none;
  outline: none;
  cursor: pointer;
  font-family: inherit;
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
.username span{
  font-size: 20px;
  color: #fff;
  font-weight: 500;
  margin-right: 6px;
}
</style>