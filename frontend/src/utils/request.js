import axios from 'axios'
import logger from './logger'

// 创建 axios 实例
const service = axios.create({
  baseURL: '/api', // 前端代理，会转发到后端
  timeout: 10000 // 请求超时
})

// 请求拦截器：统一加 token
service.interceptors.request.use(
  config => {
    // 从 localStorage 拿 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = 'Bearer ' + token
    }
    return config
  },
  error => {
    logger.error('请求发送失败：', error.message)
    return Promise.reject(error)
  }
)

// 响应拦截器：统一处理返回结果
service.interceptors.response.use(
  response => {
    const res = response.data
    // 后端正常返回
    return res
  },
  error => {
    logger.error('请求错误：', error)
    // 401 未登录，自动跳登录
    if (error.response && error.response.status === 401) {
      // 登录相关接口（login、register、send-sms等）失败时不跳转，让调用方处理
      const requestUrl = error.response.config.url
      const authPaths = ['/auth/login', '/auth/login-sms', '/auth/email/login', '/users', '/auth/send-sms', '/auth/email/code']
      // 检查 URL 是否包含任何认证相关路径
      const isAuthPath = authPaths.some(path => requestUrl.includes(path))
      if (!isAuthPath) {
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
      }
    }
    return Promise.reject(error)
  }
)

export default service