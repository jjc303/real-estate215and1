<template>

<!-- 登录模态框 -->
  <div class="modal-overlap" v-if="userStore.showLogin" @click.self="userStore.closeAllModal">
    <div class="modal-box">
      <div class="close-btn-wrap">
        <button class="close-btn" @click="userStore.closeAllModal">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>
      <div class="modal-content-wrap">
        <div class="modal-header">
          <span
            @click="userStore.activeTab='sms'"
            :class="{'active-tab': userStore.activeTab === 'sms'}"
          >
            短信验证
          </span>
          <span
            @click="userStore.activeTab='password'"
            :class="{'active-tab': userStore.activeTab === 'password'}"
          >
            密码验证
          </span>
          <span
            @click="userStore.activeTab='email'"
            :class="{'active-tab': userStore.activeTab === 'email'}"
          >
            邮箱验证
          </span>
        </div>
        <div class="modal-content">
          <div v-if="userStore.activeTab === 'sms'">
             <input v-model="userStore.loginForm.phone" type="text" placeholder="请输入手机号" />
             <div class="code-row"> 
                <input v-model="userStore.loginForm.code" placeholder="请输入验证码" />
                <button class="get-code-btn" @click="userStore.getSmsCode" :disabled="userStore.countdown>0">
                  {{ userStore.countdown>0?`${userStore.countdown}s后重试`:'获取验证码' }}
                </button>
              </div>
          </div>
          <div v-if="userStore.activeTab === 'password'">
             <input v-model="userStore.loginForm.phone" type="text" placeholder="请输入手机号" />
             <input v-model="userStore.loginForm.password" type="password" placeholder="请输入密码" />
          </div>
          <div v-if="userStore.activeTab === 'email'">
             <input v-model="userStore.loginForm.email" type="text" placeholder="请输入邮箱" />
             <div class="code-row">
                <input v-model="userStore.loginForm.emailCode" type="text" placeholder="请输入验证码" />
                <button class="get-code-btn" @click="userStore.getEmailCode" :disabled="userStore.emailCountdown>0">
                  {{ userStore.emailCountdown>0?`${userStore.emailCountdown}s后重试`:'获取验证码' }}
                </button>
             </div>
          </div>
          <button type="button" class="modal-btn" @click="userStore.submitLogin">登录</button>
        </div>
        <div class="to-register">
          <span>没有账号？</span>
          <span class="to-other" @click="userStore.openRegisterModal">前往注册</span>
        </div>
      </div>
      <div class="role-group">
        <div class="role-title">请选择身份</div>
        <div class="role-buttons">
          <button 
          type="button"
          class="role-btn" 
          :class="{ active: userStore.loginForm.role === 'tenant' }"
          @click="userStore.loginForm.role = 'tenant'"
          >
          租客
          </button>
          <button 
            type="button"
            class="role-btn" 
            :class="{ active: userStore.loginForm.role === 'landlord' }"
            @click="userStore.loginForm.role = 'landlord'"
          > 
          房东
          </button>
          <button 
            type="button"
            class="role-btn" 
            :class="{ active: userStore.loginForm.role === 'admin' }"
            @click="userStore.loginForm.role = 'admin'"
          >
          管理员 
          </button>
        </div>
      </div>
    </div>
  </div>
  <!-- 注册模态框 -->
  <div class="modal-overlap" v-if="userStore.showRegister" @click.self="userStore.closeAllModal">
    <div class="modal-box">
      <div class="close-btn-wrap">
        <button class="close-btn" @click="userStore.closeAllModal">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>
      <div class="modal-content-wrap">
        <div class="modal-header">
          <span>
            注册账号
          </span>
        </div>
        <div class="modal-content">
          <input v-model="userStore.registerForm.phone" type="text" placeholder="请输入手机号" />
          <input v-model="userStore.registerForm.password" type="password" placeholder="请输入密码" />
          <button type="button" class="modal-btn" @click="userStore.submitRegister">注册</button>
        </div>
        <div class="to-register">
          <span>已有账号？</span>
          <span class="to-other" @click="userStore.openLoginModal">前往登录</span>
        </div>
      </div>
      <div class="role-group">
        <div class="role-title">请选择身份</div>
        <div class="role-buttons">
          <button 
          type="button"
          class="role-btn" 
          :class="{ active: userStore.registerForm.role === 'tenant' }"
          @click="userStore.registerForm.role = 'tenant'"
          >
          租客
          </button>
          <button 
            type="button"
            class="role-btn" 
            :class="{ active: userStore.registerForm.role === 'landlord' }"
            @click="userStore.registerForm.role = 'landlord'"
          > 
          房东
          </button>
          <button 
            type="button"
            class="role-btn" 
            :class="{ active: userStore.registerForm.role === 'admin' }"
            @click="userStore.registerForm.role = 'admin'"
          >
          管理员 
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { useUserStore } from '@/stores/user.js';
const userStore = useUserStore();

</script>
<style scoped>
/* 模态框样式 */
.modal-overlap{
  position:fixed;
  top:0;
  left:0;
  width:100%;
  height:100%;
  background:rgba(0, 0, 0, 0.3);
  display:flex;
  align-items:center;
  justify-content:center;
  z-index:9999;
}
.modal-box{
  width:380px;
  height:460px;
  background:#fff;
  border-radius:10px;
  position:relative;
}
.modal-content-wrap {
  display:flex;
  flex-direction:column;
  max-height:400px;
  margin:5px 40px;
}
.modal-header{
  display:flex;
  justify-content:space-between;
  font-size:17px;
  font-weight:600;
  margin-bottom:20px;
  justify-content: center;
  gap: 47px;
}
.modal-header span.active-tab {
  color: rgb(28, 173, 226);
  border-bottom: 2px solid rgb(28, 173, 226);
}
.close-btn-wrap {
  width:100%;
  display:flex;
  justify-content:flex-end;
  padding: 10px;
}
.close-btn {
  background:none;
  border:none;
  font-size:16px;
  cursor:pointer;
  color: #999;
}
/* 登录表单样式 */
.modal-content {
  display:flex;
  flex-direction:column;
  margin-top:25px;
}
.modal-content input {
  width:100%;
  height:50px;
  padding:12px 15px;
  border:1px solid #ddd;
  margin-bottom:20px;
  border-radius:6px;
  font-size:16px;
  font-weight:300;
}
.modal-btn {
  width:100%;
  height:40px;
  display: flex;
  align-items: center;     /* 垂直居中 */
  justify-content: center; /* 水平居中 */
  padding: 0 15px;        /* 只有左右 padding */
  background:rgb(28, 173, 226);
  color:#fff;
  font-size:16px;
  line-height: 17px;
  border:none;
  border-radius:6px;
  cursor:pointer;
}
/* 验证码输入行 */
.code-row {
  position: relative;
  width: 100%;
}
.code-row input {
  width: 100%;
  padding-right: 110px !important;
}
.get-code-btn {
  position: absolute;
  right:0px;
  top: 34%;
  transform: translateY(-50%);
  background:transparent;
  color: rgb(28, 173, 226);
  border: none;
  border-radius: 4px;
  padding: 6px 8px;
  font-size: 14px;
  white-space: nowrap;
}
.get-code-btn:disabled {
  background: #ccc;
}
.to-register {
  font-size: 14px;
  color: #666;
  text-align: right;
}
.to-other {
  color: rgb(28, 173, 226);
  cursor: pointer;
  margin-left: 4px;
}
.to-other:hover {
  text-decoration: underline;
}
/* 角色选择 */
.role-group {
  margin-top: 15px;
  padding: 0 40px 30px;
  border-top: 1px solid rgba(160, 160, 160, 0.4);
}
.role-title {
  text-align: center;
  font-size: 15px;
  color: #333;
  margin-top: 13px;
}
.role-buttons {
  display: flex;
  justify-content: center;
  gap: 14px;
  padding-top: 15px;
  
}
.role-btn {
  width: 90px;
  height: 36px;
  border-radius: 6px;
  border: 1px solid #ddd;
  background: #fff;
  font-size: 15px;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}
.role-btn.active {
  background: rgb(28, 173, 226);
  color: #fff;
  border-color: rgb(28, 173, 226);
}
.role-btn:hover:not(.active) {
  border-color: rgb(28, 173, 226);
  color: rgb(28, 173, 226);
}

</style>