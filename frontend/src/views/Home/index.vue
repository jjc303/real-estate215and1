<template>
  <div class="page-wrap">
    <div class="home-container">
        <div class="home-header">
            <img src="@/assets/images/csu-logo.png" alt="中南大学logo" class="csu-logo" />
            <img src="@/assets/images/csu-name.png" alt="中南大学logo" class="csu-name" />
            <div class="home-nav-wrap">
                <NavBar />
            </div>
             <div class="home-user">
                <template v-if="!isLoggedIn">
                    <button class="home-btn-login" @click="openLoginModal">
                        <i class="fa-solid fa-user"></i> <span>登录</span>
                    </button>
                    <button class="home-btn-register" @click="openRegisterModal">
                        <i class="fa-solid fa-user-plus"></i> <span>注册</span>
                    </button>
                </template>
                <template v-else>
                    <span class="username">{{ userName }}</span>
                    <button class="home-btn-logout" @click="goLogout">
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
  
  <div class="modal-overlap" v-if="showLogin" @click.self="closeAllModal">
    <div class="modal-box">
      <div class="close-btn-wrap">
        <button class="close-btn" @click="closeAllModal">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>
      <div class="modal-content-wrap">
        <div class="modal-header">
          <span
            @click="activeTab='sms'"
            :class="{'active-tab': activeTab === 'sms'}"
          >
            短信验证
          </span>
          <span
            @click="activeTab='password'"
            :class="{'active-tab': activeTab === 'password'}"
          >
            密码验证
          </span>
          <span
            @click="activeTab='email'"
            :class="{'active-tab': activeTab === 'email'}"
          >
            邮箱验证
          </span>
        </div>
        <div class="modal-login-content">
          <div v-if="activeTab === 'sms'">
             <input v-model="loginForm.phone" type="text" placeholder="请输入手机号" />
             <div class="code-row"> 
                <input v-model="loginForm.code" placeholder="请输入验证码" />
                <button class="get-code-btn" @click="getSmsCode" :disabled="countdown>0">
                  {{ countdown>0?`${countdown}s后重试`:'获取验证码' }}
                </button>
              </div>
          </div>
          <div v-if="activeTab === 'password'">
             <input v-model="loginForm.phone" type="text" placeholder="请输入手机号" />
             <input v-model="loginForm.password" type="password" placeholder="请输入密码" />
          </div>
          <div v-if="activeTab === 'email'">
             <input v-model="loginForm.email" type="text" placeholder="请输入邮箱" />
             <div class="code-row">
                <input v-model="loginForm.emailCode" type="text" placeholder="请输入验证码" />
                <button class="get-code-btn" @click="getEmailCode" :disabled="emailCountdown>0">
                  {{ emailCountdown>0?`${emailCountdown}s后重试`:'获取验证码' }}
                </button>
             </div>
          </div>
          <button class="modal-btn" @click="submitLogin">登录</button>
        </div>
        <div class="to-register">
          <span>没有账号？</span>
          <span class="to-other" @click="goToRegister">前往注册</span>
        </div>
      </div>
      <div class="role-group">
        <div class="role-title">请选择身份</div>
        <div class="role-buttons">
          <button 
          type="button"
          class="role-btn" 
          :class="{ active: loginForm.role === 'tenant' }"
          @click="loginForm.role = 'tenant'"
          >
          租客
          </button>
          <button 
            type="button"
            class="role-btn" 
            :class="{ active: loginForm.role === 'landlord' }"
            @click="loginForm.role = 'landlord'"
          > 
          房东
          </button>
          <button 
            type="button"
            class="role-btn" 
            :class="{ active: loginForm.role === 'admin' }"
            @click="loginForm.role = 'admin'"
          >
          管理员 
          </button>
        </div>
      </div>
    </div>
  </div>
  <div class="modal-overlap" v-if="showRegister" @click.self="closeAllModal">
    <div class="modal-box">
      <div class="close-btn-wrap">
        <button class="close-btn" @click="closeAllModal">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>
      <div class="modal-content-wrap">
        <div class="modal-header">
          <span>
            注册账号
          </span>
        </div>
        <div class="modal-register-content">
          <input v-model="registerForm.phone" type="text" placeholder="请输入手机号" />
          <div class="code-row"> 
                <input v-model="registerForm.code" placeholder="请输入验证码" />
                <button class="get-code-btn" @click="getSmsCode" :disabled="countdown>0">
                  {{ countdown>0?`${countdown}s后重试`:'获取验证码' }}
                </button>
              </div>
          <input v-model="registerForm.password" type="password" placeholder="请输入密码" />
          <button class="modal-btn" @click="submitRegister">注册</button>
        </div>
        <div class="to-register">
          <span>已有账号？</span>
          <span class="to-other" @click="goToLogin">前往登录</span>
        </div>
      </div>
      <div class="role-group">
        <div class="role-title">请选择身份</div>
        <div class="role-buttons">
          <button 
          type="button"
          class="role-btn" 
          :class="{ active: registerForm.role === 'tenant' }"
          @click="registerForm.role = 'tenant'"
          >
          租客
          </button>
          <button 
            type="button"
            class="role-btn" 
            :class="{ active: registerForm.role === 'landlord' }"
            @click="registerForm.role = 'landlord'"
          > 
          房东
          </button>
          <button 
            type="button"
            class="role-btn" 
            :class="{ active: registerForm.role === 'admin' }"
            @click="registerForm.role = 'admin'"
          >
          管理员 
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue';
import SearchBar from '@/components/SearchBar.vue';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router =useRouter();

const goLogout=()=>{
  // 这里可以添加实际的退出逻辑，例如清除用户信息、调用后端接口等
  alert('退出登录成功！');
  isLoggedIn.value = false; // 模拟退出登录状态
  router.push('/'); // 退出后返回首页
}
const isLoggedIn = ref(false); // 模拟登录状态，实际项目中应根据后端返回的状态设置
const userName = ref('张三dadada');

const showLogin=ref(false);
const showRegister=ref(false);
const activeTab=ref('password'); //记录验证方式
const loginForm = ref({
  phone: '',//手机号就是账号
  code: '',//短信验证码
  password: '',//密码
  email: '',//邮箱
  emailCode: '',//邮箱验证码
  role: 'tenant', // 默认选择租客
})
const registerForm = ref({
  id: '',//账号
  phone: '',//密码
  password: '',//密码
  role: 'tenant', // 默认选择租客
})
const countdown=ref(0);//短信验证码倒计时
const emailCountdown=ref(0);//邮箱验证码倒计时


const closeAllModal=()=>{
  showLogin.value=false;
  showRegister.value=false;
}
const openLoginModal=()=>{
  showLogin.value=true;
  showRegister.value=false;
}
const openRegisterModal=()=>{
  showLogin.value=false;
  showRegister.value=true;
}
const goToLogin=()=>{
  openLoginModal();
}
const goToRegister=()=>{
  openRegisterModal();
}
//手机号验证函数
const checkPhone=(phone)=>{
  const phoneRegex=/^1[3-9]\d{9}$/;
  return phoneRegex.test(phone);
}
//短信获取验证码函数
const getSmsCode=()=>{
  if(!loginForm.value.phone){
    alert('请输入手机号');
    return;
  }
  if(!checkPhone(loginForm.value.phone)){
    alert('请输入正确的手机号');
    return;
  }
  // 这里可以添加实际的获取验证码逻辑，例如调用后端接口等
  alert('验证码已发送！');
  countdown.value=60;//开始60秒倒计时
  const timer=setInterval(()=>{
    countdown.value--;
    if(countdown.value<=0){
      clearInterval(timer);
    }
  },1000);
}
//邮箱验证函数
const checkEmail=(email)=>{
  const emailRegex=/^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}
//邮箱获取验证码函数
const getEmailCode=()=>{
  if(!loginForm.value.email){
    alert('请输入邮箱');
    return;
  }
  if(!checkEmail(loginForm.value.email)){
    alert('请输入正确的邮箱地址');
    return;
  }
  // 这里可以添加实际的获取验证码逻辑，例如调用后端接口等
  alert('验证码已发送！');
  emailCountdown.value=60;
  const timer=setInterval(()=>{
    emailCountdown.value--;
    if(emailCountdown.value<=0){
      clearInterval(timer);
    }
  },1000);
}
const submitLogin=()=>{
  //获取验证方式
  const type=activeTab.value;
  if(type==='sms'){
    if(!loginForm.value.phone){
      alert('请输入手机号');
      return;
    }
    if(!checkPhone(loginForm.value.phone)){
      alert('请输入正确的手机号');
      return;
    }
    if(!loginForm.value.code){
      alert('请输入验证码');
      return;
    }
  }
  else if(type=='password'){
    if(!loginForm.value.phone){
      alert('请输入手机号');
      return;
    }
    if(!checkPhone(loginForm.value.phone)){
      alert('请输入正确的手机号');
      return;
    }
    if(!loginForm.value.password){
      alert('请输入密码');
      return;
    }
  }
  else if(type=='email'){
    if(!loginForm.value.email){
      alert('请输入邮箱');
      return;
    }
    if(!checkEmail(loginForm.value.email)){
      alert('请输入正确的邮箱地址');
      return;
    }
    if(!loginForm.value.emailCode){
      alert('请输入邮箱验证码');
      return;
    }
  }
  // 这里可以添加实际的登录逻辑，例如调用后端接口等
  alert(`登录成功！角色：${loginForm.value.role}`);
  isLoggedIn.value=true;
  userName.value='张三';//或可使用加密的手机号
  closeAllModal();
}
const submitRegister=()=>{
  if(!registerForm.value.phone){
    alert('请输入手机号');
    return;
  }
  if(!checkPhone(registerForm.value.phone)){
    alert('请输入正确的手机号');
    return;
  }
  if(!registerForm.value.password){
    alert('请输入密码');
    return;
  }
  if(!registerForm.value.code){
    alert('请输入验证码');
    return;
  }
  // 这里可以添加实际的注册逻辑，例如调用后端接口等
  alert(`注册成功！角色：${registerForm.value.role}`);
  //自动跳转登录
  goToLogin();
}
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

.csu-logo {
  position: absolute;
  top: 32px;
  left: 270px;
  height: 80px;
  object-fit: contain;
}

.csu-name {
  position: absolute;
  top: 44px;
  left: 350px;
  height: 50px;
  background: transparent;
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
.home-btn-login {
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
.home-btn-login:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-1px);
}

/* 注册按钮（主按钮） */

.home-btn-register{
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
.home-btn-register:hover {
  background: #0753ab;
  transform: translateY(-1px);
}

/* 退出按钮 */
.home-btn-logout {
  padding: 8px 16px;
  font-size: 18px;
  color: #ff4d4f;
  background: transparent;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: color 0.2s ease;
}
.home-btn-logout:hover {
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
.modal-login-content {
  display:flex;
  flex-direction:column;
  margin-top:25px;
}
.modal-login-content input {
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
/* 注册表单样式 */
.modal-register-content {
  display:flex;
  flex-direction:column;
}
.modal-register-content input {
  width:100%;
  height:40px;
  padding:12px 15px;
  border:1px solid #ddd;
  margin-bottom:20px;
  border-radius:6px;
  font-size:16px;
  font-weight:300;
}
</style>