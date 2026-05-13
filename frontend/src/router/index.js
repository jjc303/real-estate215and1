import { createRouter, createWebHistory } from 'vue-router'

const Home = () => import('../views/Home/index.vue')
const PublicNews = () => import('../views/PublicNews/index.vue')
const Admin = () => import('../views/Admin/index.vue')
const HouseDetail = () => import('../views/HouseDetail/index.vue')
const HouseList = () => import('../views/HouseList/index.vue')
const Reservation = () => import('../views/Reservation/index.vue')
const Contracts = () => import('../views/Contracts/index.vue')
const ContractDetail = () => import('../views/Contracts/detail.vue')
const ContractCreate = () => import('../views/Contracts/create.vue')
const MyHouses = () => import('../views/MyHouses/index.vue')
const MyHousesPublish = () => import('@/views/MyHouses/publish.vue')
const MyHousesList = () => import('../views/MyHouses/list.vue')
const Profile = () => import('../views/Profile/index.vue')
const Thanks = () => import('../views/Thanks/index.vue')
const Help = () => import('../views/Help/index.vue')
const Bills = () => import('../views/Bills/index.vue')
const BillDetail = () => import('../views/Bills/detail.vue')

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
    path: '/contracts',
    name: 'contracts',
    component: Contracts,
  },
  {
    path: '/contracts/detail/:id',
    name: 'contractDetail',
    component: ContractDetail,
  },
  {
    path: '/contracts/create',
    name: 'contractCreate',
    component: ContractCreate,
  },
  {
    path: '/profile',
    name: 'profile',
    component: Profile
  },
  {
    path: '/manage/rent',
    name: 'bills',
    component: Bills,
  },
  {
    path: '/lease/payment',
    name: 'leasePayment',
    component: Bills,
  },
  {
    path: '/bills/detail/:id',
    name: 'billDetail',
    component: BillDetail,
  },
  {
    path: '/thanks',
    name: 'thanks',
    meta: { title: '特别鸣谢' },
    component: Thanks
  },
  {
    path: '/help',
    name: 'help',
    meta: { title: '帮助手册' },
    component: Help
  }
]
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
