import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import ErrorHandler from './utils/errorHandler'
import '@fortawesome/fontawesome-free/css/all.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus, {
  // 全局配置 Message
  message: {
    duration: 2500,       // 显示2.5秒自动关
    center: true,          // 居中显示
    showClose: true,       // 显示关闭按钮
    grouping: true         // 同类消息合并
  }
})

// 初始化错误处理
ErrorHandler.init(app)

app.mount('#app')
