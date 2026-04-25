import {defineStore} from 'pinia';
import { ref } from 'vue';
export const useUserStore = defineStore('user', () => {
    const isLoggedIn = ref(false);
    const userName = ref('');

    const showLogin=ref(false);//登录模态框显示状态
    const showRegister=ref(false);//注册模态框显示状态

    const activeTab=ref('password'); //记录验证方式
    const countdown=ref(0);//短信验证码倒计时
    const emailCountdown=ref(0);//邮箱验证码倒计时
    //登录表单数据
    const loginForm = ref({
        phone: '',//手机号就是账号
        code: '',//短信验证码
        password: '',//密码
        email: '',//邮箱
        emailCode: '',//邮箱验证码
        role: 'tenant', // 默认选择租客
    })
    //注册表单数据
    const registerForm = ref({
        id: '',//账号
        phone: '',//密码
        password: '',//密码
        role: 'tenant', // 默认选择租客
    })

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
    //邮箱验证函数
    const checkEmail=(email)=>{
        const emailRegex=/^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
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
    //邮箱获取验证码函数//邮箱获取验证码函数
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
    //登录提交函数
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
        userName.value=loginForm.value.phone;//或可使用加密的手机号
        closeAllModal();
    }
    //注册提交函数
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
    // 退出登录
    const logout = () => {
        isLoggedIn.value = false
        userName.value = ''
        // 清空表单
        loginForm.value = { phone: '', code: '', password: '', email: '', emailCode: '', role: 'tenant' }
        registerForm.value = { phone: '', code: '', password: '', role: 'tenant' }
    }    

    return {
        // 状态
        isLoggedIn,
        userName,
        showLogin,
        showRegister,
        loginForm,
        registerForm,
        activeTab,
        countdown,
        emailCountdown,

        // 方法
        closeAllModal,
        openLoginModal,
        openRegisterModal,
        getSmsCode,
        getEmailCode,
        submitLogin,
        submitRegister,
        logout
  }
});