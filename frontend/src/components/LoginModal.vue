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
                <button class="get-code-btn" @click="userStore.getSmsCode" :disabled="userStore.loginCountdown>0">
                  {{ userStore.loginCountdown>0?`${userStore.loginCountdown}s后重试`:'获取验证码' }}
                </button>
              </div>
          </div>
          <div v-if="userStore.activeTab === 'password'">
             <input v-model="userStore.loginForm.username" type="text" placeholder="请输入账号" />
             <input v-model="userStore.loginForm.password" type="password" placeholder="请输入密码" />
          </div>
          <div v-if="userStore.activeTab === 'email'">
             <input v-model="userStore.loginForm.email" type="text" placeholder="请输入邮箱" />
             <div class="code-row">
                <input v-model="userStore.loginForm.emailCode" type="text" placeholder="请输入验证码" />
                <button class="get-code-btn" @click="userStore.getEmailCode('login')" :disabled="userStore.loginEmailCountdown>0">
                  {{ userStore.loginEmailCountdown>0?`${userStore.loginEmailCountdown}s后重试`:'获取验证码' }}
                </button>
             </div>
          </div>
        </div>
        <button type="button" class="modal-btn" @click="userStore.submitLogin">登录</button>
        <div class="to-register">
          <span>没有账号？</span>
          <span class="to-other" @click="userStore.openRegisterModal">前往注册</span>
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
          <span
            @click="userStore.registerType='password'"
            :class="{'active-tab': userStore.registerType === 'password'}"
          >
            账号注册
          </span>
          <span
            @click="userStore.registerType='email'"
            :class="{'active-tab': userStore.registerType === 'email'}"
          >
            邮箱注册
          </span>
        </div>
        <div class="modal-content">
          <div v-if="userStore.registerType==='password'">
            <input v-model="userStore.registerForm.username" type="text" placeholder="请输入账号" />
            <input v-model="userStore.registerForm.password" type="password" placeholder="请输入密码" />
          </div>
          <div v-if="userStore.registerType==='email'">
              <input v-model="userStore.registerForm.email" type="text" placeholder="请输入邮箱" />
              <div class="code-row">
                <input v-model="userStore.registerForm.emailCode" type="text" placeholder="请输入验证码" />
                <button class="get-code-btn" @click="userStore.getEmailCode('register')" :disabled="userStore.registerEmailCountdown>0">
                  {{ userStore.registerEmailCountdown>0?`${userStore.registerEmailCountdown}s后重试`:'获取验证码' }}
                </button>
              </div>
          </div>
        </div>
        <button type="button" class="modal-btn" @click="userStore.submitRegister">注册</button>
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
  background:rgba(0, 0, 0, 0.45);
  display:flex;
  align-items:center;
  justify-content:center;
  z-index:9999;
}
.modal-box{
  width:380px;
  min-height: 380px;
  max-height: 520px;
  background:#fff;
  border-radius:16px;
  position:relative;
  padding-bottom: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
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
  height:48px;
  padding:12px 15px;
  border:1px solid #e0e0e0;
  margin-bottom:18px;
  border-radius:10px;
  font-size:15px;
  font-weight:400;
  transition: all 0.3s ease;
  box-sizing: border-box;
}
.modal-content input:focus {
  outline: none;
  border-color: rgb(28, 173, 226);
  box-shadow: 0 0 0 3px rgba(28, 173, 226, 0.1);
}
.modal-content input::placeholder {
  color: #999;
}
.modal-btn {
  width:100%;
  height:44px;
  display: flex;
  align-items: center;     /* 垂直居中 */
  justify-content: center; /* 水平居中 */
  padding: 0 15px;        /* 只有左右 padding */
  background: linear-gradient(135deg, rgb(28, 173, 226) 0%, rgb(26, 156, 209) 100%);
  color:#fff;
  font-size:16px;
  font-weight:500;
  line-height: 17px;
  border:none;
  border-radius:10px;
  cursor:pointer;
  transition: all 0.3s ease;
}
.modal-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(28, 173, 226, 0.3);
}
.modal-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(28, 173, 226, 0.2);
}
/* 验证码输入行 */
.code-row {
  position: relative;
  width: 100%;
  height: 48px;
  margin-bottom: 18px;
}
.code-row input {
  width: 100%;
  height: 100%;
  padding-right: 125px !important;
  box-sizing: border-box;
}
.get-code-btn {
  position: absolute;
  right: 6px;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(28, 173, 226, 0.1);
  color: rgb(28, 173, 226);
  border: 1px solid rgba(28, 173, 226, 0.3);
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.3s ease;
  line-height: 1.4;
}
.get-code-btn:hover:not(:disabled) {
  background: rgba(28, 173, 226, 0.15);
  border-color: rgba(28, 173, 226, 0.5);
}
.get-code-btn:disabled {
  background: #f5f5f5;
  color: #999;
  border-color: #e0e0e0;
  cursor: not-allowed;
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
  padding: 0 40px 20px;
  border-top: 1px solid #f0f0f0;
}
.role-title {
  text-align: center;
  font-size: 14px;
  color: #666;
  margin-top: 16px;
  font-weight: 400;
}
.role-buttons {
  display: flex;
  justify-content: center;
  gap: 12px;
  padding-top: 16px;
  
}
.role-btn {
  width: 95px;
  height: 38px;
  border-radius: 10px;
  border: 2px solid #e0e0e0;
  background: #fff;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}
.role-btn.active {
  background: linear-gradient(135deg, rgba(28, 173, 226, 0.1) 0%, rgba(26, 156, 209, 0.1) 100%);
  color: rgb(28, 173, 226);
  border-color: rgb(28, 173, 226);
}
.role-btn:hover:not(.active) {
  border-color: rgba(28, 173, 226, 0.5);
  color: rgb(28, 173, 226);
}

</style>