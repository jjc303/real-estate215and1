<template>
  <div class="page-wrap">
    <div class="home-container">
        <div class="home-header">
            <img src="@/assets/images/csu-logo.png" alt="中南大学logo" class="logo" />
            <div class="home-nav-wrap">
                <NavBar />
            </div>
             <div class="home-user">
                <template v-if="!isLoggedIn">
                    <button class="btn-login">
                        <i class="fa-solid fa-user"></i> <span>登录</span>
                    </button>
                    <button class="btn-register">
                        <i class="fa-solid fa-user-plus"></i> <span>注册</span>
                    </button>
                </template>
                <template v-else>
                    <span class="username">{{ userName }}</span>
                    <button class="btn-logout">
                        <i class="fa-solid fa-right-from-bracket"></i> 退出
                    </button>
                </template>
            </div>
        </div>
        <div class="home-content">
          <div class="title-small">一席定境，一生从容</div>
          <div class="title-large">来中南找房寻找真正的家</div>
          <div class="home-searchBar">
              <SearchBar />
          </div>
        </div>
    </div>
  </div>
  
  
</template>

<script setup>
import NavBar from '@/components/NavBar.vue';
import SearchBar from '@/components/SearchBar.vue';
import { ref } from 'vue';
const isLoggedIn = ref(false); // 模拟登录状态，实际项目中应根据后端返回的状态设置
const userName = ref('张三dadada');
</script>

<style>
/* 全局清除浏览器默认白边 */
* {
  margin: 0 ;
  padding: 0 ;
  box-sizing: border-box;
}
</style>

<style scoped>

.home-container {
  width: 1488px;
  height: 600px;
  margin: 0;
  padding: 0;
  background-image: url('@/assets/images/home.jpg');
  background-size: cover;
  background-position: 50% 68%;
  background-repeat: no-repeat;
  position: relative;
}

.logo {
  position: absolute;
  top: 5px;
  left: 5px;
  height: 80px;
  object-fit: contain;
}
.home-header {
  position: relative;
  height: 120px;
}
.home-nav-wrap {
  position: absolute;
  top: 40px;       /* 上下位置 */
  left: 500px;     /* 左右位置 */
  z-index: 100;    /* 保证在最上面 */

}
.home-user {
  position: absolute;
  top: 42px;
  right: 40px;
  display: flex;
  gap: 10px;
  align-items: center;
}
button {
  border: none;
  outline: none;
  cursor: pointer;
  font-family: inherit;
}
/* 登录按钮 */
.btn-login {
  padding: 10px 20px;
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
.btn-register {
  padding: 10px 20px;
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

/* 用户名 */
.username {
  font-size: 20px;
  color: #fff;
  font-weight: 500;
  margin-right: 6px;
}
.home-content {
  position: absolute;
  top: 50%;
  left: 70%;
  transform: translate(-50%, -50%);
  text-align: left;
  color: #fff;
  width: 600px;
}
.title-small {
  font-size: 32px;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.85);
  font-weight: 400;
  letter-spacing: 2px;
  font-family: "Helvetica Neue", "PingFang SC", sans-serif;
  text-transform: uppercase; /* 可选，让文字更规整 */
}

.title-large {
  font-size: 52px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: 3px;
  font-family: "Helvetica Neue", "PingFang SC", sans-serif;
  text-shadow: 0 3px 12px rgba(0, 0, 0, 0.25);
  line-height: 1.2;
  white-space: nowrap;
}
.home-searchBar {
  margin-top: 30px;
}
</style>