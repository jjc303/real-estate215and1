import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ErrorHandler from './utils/errorHandler'
import '@fortawesome/fontawesome-free/css/all.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())// 使用 Pinia 进行状态管理
app.use(router)// 使用 Vue Router 进行路由管理

// 初始化错误处理
ErrorHandler.init(app)

app.mount('#app')
