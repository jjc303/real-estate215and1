import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { ElMessage } from 'element-plus';
import service from '@/utils/request';
import { menus } from '@/config/menus.js';
import { useRouter } from 'vue-router';
export const useUserStore = defineStore('user', () => {
    const router = useRouter()
    // 从 localStorage 恢复状态
    const isLoggedIn = ref(!!localStorage.getItem('token'));
    const userName = ref(localStorage.getItem('userName') || '');
    const userRole = ref(localStorage.getItem('userRole') || 'tenant')
    const showLogin = ref(false);//登录模态框显示状态
    const showRegister = ref(false);//注册模态框显示状态

    const activeTab = ref('password');
    const registerType = ref('password');
    // 登录倒计时
    const loginCountdown = ref(0);
    const loginEmailCountdown = ref(0);
    const loginSmsTimer = ref(null);
    const loginEmailTimer = ref(null);
    // 注册倒计时
    const registerCountdown = ref(0);
    const registerEmailCountdown = ref(0);
    const registerSmsTimer = ref(null);
    const registerEmailTimer = ref(null);
    //登录表单数据
    const loginForm = ref({
        username: '',//账号
        phone: '',//手机号（用于短信登录）
        code: '',//短信验证码
        password: '',//密码
        email: '',//邮箱
        emailCode: '',//邮箱验证码
    })
    //注册表单数据
    const registerForm = ref({
        username: '',//账号
        password: '',//密码
        email: '',//邮箱
        emailCode: '',//邮箱验证码
        role: 'tenant', // 默认选择租客
    })
    //根据角色返回对应表单
    const currentMenus = computed(() => {
        return menus[userRole.value] || menus.guest
    })
    const closeAllModal = () => {
        showLogin.value = false;
        showRegister.value = false;
        // 清理登录定时器
        if (loginSmsTimer.value) {
            clearInterval(loginSmsTimer.value);
            loginSmsTimer.value = null;
        }
        if (loginEmailTimer.value) {
            clearInterval(loginEmailTimer.value);
            loginEmailTimer.value = null;
        }
        // 清理注册定时器
        if (registerSmsTimer.value) {
            clearInterval(registerSmsTimer.value);
            registerSmsTimer.value = null;
        }
        if (registerEmailTimer.value) {
            clearInterval(registerEmailTimer.value);
            registerEmailTimer.value = null;
        }
        // 重置所有倒计时
        loginCountdown.value = 0;
        loginEmailCountdown.value = 0;
        registerCountdown.value = 0;
        registerEmailCountdown.value = 0;
    }
    const openLoginModal = () => {
        showLogin.value = true;
        showRegister.value = false;
        activeTab.value = 'password';
        loginForm.value = { username: '', phone: '', code: '', password: '', email: '', emailCode: '' };
    }
    const openRegisterModal = () => {
        showLogin.value = false;
        showRegister.value = true;
        registerType.value = 'password';
        registerForm.value = { username: '', password: '', email: '', emailCode: '', role: 'tenant' };
    }
    const goToLogin = () => {
        openLoginModal();
    }
    const goToRegister = () => {
        openRegisterModal();
    }

    const handleError = (error, defaultMsg = '操作失败') => {
        const status = error.response?.status
        const response = error.response?.data

        // 优先用后端返回的message
        if (response?.message || response?.msg) {
            ElMessage.error(response.message || response.msg)
            return
        }

        // 处理 Pydantic 验证错误详情
        if (response?.detail) {
            const detailMsg = Array.isArray(response.detail)
                ? response.detail.map(d => d.msg).join('; ')
                : response.detail
            ElMessage.error(detailMsg || '请求参数错误')
            return
        }

        // 根据HTTP状态码做友好提示
        const statusMessages = {
            400: '参数错误，请检查输入',
            401: '登录已过期，请重新登录',
            403: '没有权限执行此操作',
            404: '请求的资源不存在',
            409: '数据已存在，请重试',
            429: '操作太频繁，请稍后再试',
            500: '服务器开小差了，请稍后重试',
            502: '服务暂时不可用',
            503: '服务维护中，请稍后再试'
        }

        if (status && statusMessages[status]) {
            ElMessage.error(statusMessages[status])
            return
        }

        // 网络错误
        if (!status) {
            ElMessage.error('网络连接失败，请检查网络')
            return
        }

        // 兜底默认提示
        ElMessage.error(defaultMsg)
    }
    //手机号验证函数
    const checkPhone = (phone) => {
        const phoneRegex = /^1[3-9]\d{9}$/;
        return phoneRegex.test(phone);
    }
    //邮箱验证函数
    const checkEmail = (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    //短信获取验证码函数（登录用）
    const getSmsCode = async () => {
        if (!loginForm.value.phone) {
            ElMessage.warning('请输入手机号');
            return;
        }
        if (!checkPhone(loginForm.value.phone)) {
            ElMessage.warning('请输入正确的手机号');
            return;
        }
        try {
            await service.post('/v1/auth/send-sms', {
                phone: loginForm.value.phone
            })
            ElMessage.success('验证码已发送！');
            if (loginSmsTimer.value) clearInterval(loginSmsTimer.value);
            loginCountdown.value = 60;
            loginSmsTimer.value = setInterval(() => {
                loginCountdown.value--;
                if (loginCountdown.value <= 0) {
                    clearInterval(loginSmsTimer.value);
                    loginSmsTimer.value = null;
                }
            }, 1000);
        } catch (e) {
            handleError(e, '获取短信验证码失败')
        }
    }
    //邮箱获取验证码函数
    const getEmailCode = async (type) => {
        // 根据type判断用哪个表单的邮箱
        const targetEmail = type === 'register'
            ? registerForm.value.email
            : loginForm.value.email;

        if (!targetEmail) {
            ElMessage.warning('请输入邮箱');
            return;
        }
        if (!checkEmail(targetEmail)) {
            ElMessage.warning('请输入正确的邮箱地址');
            return;
        }

        try {
            await service.post('/v1/auth/email/code', {
                email: targetEmail,
                biz_type: type
            })

            ElMessage.success('验证码已发送！');

            // 根据类型使用不同的倒计时
            if (type === 'register') {
                if (registerEmailTimer.value) clearInterval(registerEmailTimer.value);
                registerEmailCountdown.value = 60;
                registerEmailTimer.value = setInterval(() => {
                    registerEmailCountdown.value--;
                    if (registerEmailCountdown.value <= 0) {
                        clearInterval(registerEmailTimer.value);
                        registerEmailTimer.value = null;
                    }
                }, 1000);
            } else {
                if (loginEmailTimer.value) clearInterval(loginEmailTimer.value);
                loginEmailCountdown.value = 60;
                loginEmailTimer.value = setInterval(() => {
                    loginEmailCountdown.value--;
                    if (loginEmailCountdown.value <= 0) {
                        clearInterval(loginEmailTimer.value);
                        loginEmailTimer.value = null;
                    }
                }, 1000);
            }
        } catch (e) {
            handleError(e, '获取邮箱验证码失败')
        }
    }
    //登录提交函数
    const submitLogin = async () => {
        //获取验证方式
        const type = activeTab.value;
        if (type === 'sms') {
            if (!loginForm.value.phone) {
                ElMessage.warning('请输入手机号');
                return;
            }
            if (!checkPhone(loginForm.value.phone)) {
                ElMessage.warning('请输入正确的手机号');
                return;
            }
            if (!loginForm.value.code) {
                ElMessage.warning('请输入验证码');
                return;
            }
        }
        else if (type == 'password') {
            if (!loginForm.value.username) {
                ElMessage.warning('请输入账号');
                return;
            }
            if (loginForm.value.username.length < 3) {
                ElMessage.warning('账号长度至少3位');
                return;
            }
            if (!loginForm.value.password) {
                ElMessage.warning('请输入密码');
                return;
            }
            if (loginForm.value.password.length < 6) {
                ElMessage.warning('密码长度至少6位');
                return;
            }
        }
        else if (type == 'email') {
            if (!loginForm.value.email) {
                ElMessage.warning('请输入邮箱');
                return;
            }
            if (!checkEmail(loginForm.value.email)) {
                ElMessage.warning('请输入正确的邮箱地址');
                return;
            }
            if (!loginForm.value.emailCode) {
                ElMessage.warning('请输入邮箱验证码');
                return;
            }
        }


        try {
            let res;
            if (type === 'password') {
                res = await service.post('/v1/auth/login', {
                    username: loginForm.value.username,
                    password: loginForm.value.password
                })
            } else if (type === 'sms') {
                res = await service.post('/v1/auth/login-sms', {
                    username: loginForm.value.phone,
                    code: loginForm.value.code
                })
            } else if (type === 'email') {
                res = await service.post('/v1/auth/email/login', {
                    email: loginForm.value.email,
                    code: loginForm.value.emailCode
                })
            }
            isLoggedIn.value = true;
            userRole.value = res.data.role || 'tenant'
            userName.value = res.data.username || loginForm.value.username;

            // 保存到 localStorage
            localStorage.setItem('token', res.data.token)
            localStorage.setItem('userName', userName.value)
            localStorage.setItem('userRole', userRole.value)

            ElMessage.success(`登录成功！欢迎 ${userName.value}`);
            closeAllModal();
        } catch (e) {
            // 优先显示后端返回的message，如"用户名或密码错误"、"用户不存在"等
            handleError(e, '用户名或密码错误')
        }

    }
    //注册提交函数
    const submitRegister = async () => {
        const type = registerType.value
        if (type === 'password') {
            if (!registerForm.value.username) {
                ElMessage.warning('请输入账号');
                return;
            }
            if (registerForm.value.username.length < 3) {
                ElMessage.warning('账号长度至少3位');
                return;
            }
            if (!registerForm.value.password) {
                ElMessage.warning('请输入密码');
                return;
            }
            if (registerForm.value.password.length < 6) {
                ElMessage.warning('密码长度至少6位');
                return;
            }
        }
        else if (type === 'email') {
            if (!registerForm.value.email) {
                ElMessage.warning('请输入邮箱');
                return;
            }
            if (!checkEmail(registerForm.value.email)) {
                ElMessage.warning('请输入正确的邮箱地址');
                return;
            }
            if (!registerForm.value.emailCode) {
                ElMessage.warning('请输入邮箱验证码');
                return;
            }
        }

        try {
            let res;
            if (type === 'password') {
                res = await service.post('/v1/users', {
                    username: registerForm.value.username,
                    password: registerForm.value.password,
                    role: registerForm.value.role,
                })
            } else if (type === 'email') {
                res = await service.post('/v1/auth/email/register', {
                    email: registerForm.value.email,
                    code: registerForm.value.emailCode,
                    role: registerForm.value.role
                })
            }

            ElMessage.success('注册成功！请登录')
            goToLogin()
        } catch (e) {
            // 优先显示后端返回的message，如"用户名已存在"、"验证码错误"等
            handleError(e, '注册失败')
        }
    }
    // 退出登录
    const logout = () => {
        isLoggedIn.value = false
        userName.value = ''
        userRole.value = 'guest'
        // 清理登录定时器
        if (loginSmsTimer.value) {
            clearInterval(loginSmsTimer.value);
            loginSmsTimer.value = null;
        }
        if (loginEmailTimer.value) {
            clearInterval(loginEmailTimer.value);
            loginEmailTimer.value = null;
        }
        // 清理注册定时器
        if (registerSmsTimer.value) {
            clearInterval(registerSmsTimer.value);
            registerSmsTimer.value = null;
        }
        if (registerEmailTimer.value) {
            clearInterval(registerEmailTimer.value);
            registerEmailTimer.value = null;
        }
        // 重置所有倒计时
        loginCountdown.value = 0;
        loginEmailCountdown.value = 0;
        registerCountdown.value = 0;
        registerEmailCountdown.value = 0;
        // 清空表单
        loginForm.value = { username: '', phone: '', code: '', password: '', email: '', emailCode: '' }
        registerForm.value = { username: '', password: '', email: '', emailCode: '', role: 'tenant' }
        // 清除 localStorage
        localStorage.removeItem('token')
        localStorage.removeItem('userName')
        localStorage.removeItem('userRole')

        router.push('/')
    }

    return {
        // 状态
        isLoggedIn,
        userName,
        userRole,
        showLogin,
        showRegister,
        loginForm,
        registerForm,
        activeTab,
        registerType,
        // 登录倒计时
        loginCountdown,
        loginEmailCountdown,
        // 注册倒计时
        registerCountdown,
        registerEmailCountdown,
        currentMenus,


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
