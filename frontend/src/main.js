import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ErrorHandler from './utils/errorHandler'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// 初始化错误处理
ErrorHandler.init(app)

app.mount('#app')
