import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import ErrorHandler from './utils/errorHandler'
import '@fortawesome/fontawesome-free/css/all.min.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus, {
  message: {
    duration: 2500,
    center: true,
    showClose: true,
    grouping: true
  }
})

ErrorHandler.init(app)

app.mount('#app')
