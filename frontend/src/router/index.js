import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home/index.vue'
import Message from '../views/Message/index.vue'
import Admin from '../views/Admin/index.vue'
import HouseDetail from '../views/HouseDetail/index.vue'
import HouseList from '../views/HouseList/index.vue'
import Reservation from'../views/Reservation/index.vue'
const routes = [
  {
    path: '/',
    name:'home',
    meta:{title:'中南找房'},
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
    meta:{title:'长沙租房'},
    component: HouseList
  },
  {
    path:'/reservation',
    name:'reservation',
    component:Reservation,
  }
]
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
