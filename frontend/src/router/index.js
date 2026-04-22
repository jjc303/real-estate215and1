import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home/index.vue'
import Message from '../views/Message/index.vue'
import Admin from '../views/Admin/index.vue'
import HouseDetail from '../views/HouseDetail/index.vue'
import HouseList from '../views/HouseList/index.vue'
const routes = [
  {
    path: '/',
    name:'home',
    component: Home
  },
  {
    path:'/message',
    name:'message',
    component: Message
  },
  {
    path:'/admin',
    name:'admin',
    component: Admin
  },
  {
    path:'/houseDetail',
    name:'houseDetail',
    component: HouseDetail
  },
  {
    path:'/houseList',
    name:'houseList',
    component: HouseList
  }
]
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
