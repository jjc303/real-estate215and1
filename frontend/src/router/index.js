import { createRouter, createWebHistory } from 'vue-router'

const Home = () => import('../views/Home/index.vue')
const Message = () => import('../views/Message/index.vue')
const MessageChat = () => import('../views/Message/chat.vue')
const MessageNews = () => import('../views/Message/news.vue')
const PublicNews = () => import('../views/PublicNews/index.vue')
const Admin = () => import('../views/Admin/index.vue')
const HouseDetail = () => import('../views/HouseDetail/index.vue')
const HouseList = () => import('../views/HouseList/index.vue')
const Reservation = () => import('../views/Reservation/index.vue')
const MyHouses = () => import('../views/MyHouses/index.vue')
const MyHousesPublish = () => import('@/views/MyHouses/publish.vue')
const MyHousesList = () => import('../views/MyHouses/list.vue')
const Profile = () => import('../views/Profile/index.vue')

const routes = [
  {
    path: '/',
    name: 'home',
    meta: { title: '中南找房', hideHeader: true },
    component: Home
  },
  {
    path: '/news',
    name: 'publicNews',
    meta: { title: '新闻通知' },
    component: PublicNews
  },
  {
    path: '/message',
    name: 'message',
    component: Message,
    redirect: '/message/chat',
    children: [
      { path: 'chat', name: 'messageChat', component: MessageChat },
      { path: 'news', name: 'messageNews', component: MessageNews }
    ]
  },
  {
    path: '/admin',
    name: 'admin',
    component: Admin
  },
  {
    path: '/houseDetail',
    name: 'houseDetail',
    component: HouseDetail
  },
  {
    path: '/houseList',
    name: 'houseList',
    meta: { title: '长沙租房' },
    component: HouseList
  },
  {
    path: '/myhouses',
    name: 'myhouses',
    component: MyHouses,
    children: [
      { path: 'publish', name: 'myhousesPublish', component: MyHousesPublish },
      { path: 'edit/:id', name: 'myhousesEdit', component: MyHousesPublish },
      { path: 'list', name: 'myhousesList', component: MyHousesList }
    ]
  },
  {
    path: '/reservation',
    name: 'reservation',
    component: Reservation,
  },
  {
    path: '/profile',
    name: 'profile',
    component: Profile
  }
]
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
