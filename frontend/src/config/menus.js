// /src/config/menus.js
export const menus = {
  guest: [
    { name: '中南找房', path: '/', icon: 'Home' },
    { name: '房源搜索', path: '/houseList', icon: 'Search' },
    { name: '新闻通知', path: '/news' },
    { name: '帮助手册', path: '/help' },
    { name: '特别鸣谢', path: '/thanks' },
  ],

  tenant: [  // 租客
    { name: '首页', path: '/', icon: 'Home' },
    { name: '房源搜索', path: '/houseList', icon: 'Search' },
    {
      name: '我的租赁',
      path: '/lease',
      icon: 'FileText',
      children: [
        { name: '预约看房', path: '/lease/appointment' },
        { name: '在线签约', path: '/lease/contract' },
        { name: '租金支付', path: '/lease/payment' }
      ]
    },
    {
      name: '维修投诉',
      path: '/service',
      icon: 'Tool',
      children: [
        { name: '维修申请', path: '/service/repair' },
        { name: '投诉管理', path: '/service/complaint' }
      ]
    },
    { name: '新闻通知', path: '/news', icon: 'Message' },
    { name: '个人中心', path: '/profile', icon: 'User' }
  ],

  landlord: [  // 房东
    { name: '首页', path: '/', icon: 'Home' },
    {
      name: '我的房源',
      path: '/myhouses',
      icon: 'Home',
      children: [
        { name: '创建房源', path: '/myhouses/publish' },
        { name: '房源列表', path: '/myhouses/list' }
      ]
    },
    { name: '房源列表', path: '/houseList', icon: 'Search' },
    {
      name: '租赁管理',
      path: '/manage',
      icon: 'FileText',
      children: [
        { name: '预约确认', path: '/reservation' },
        { name: '合同管理', path: '/contracts' },
        { name: '租金监控', path: '/manage/rent' },
        { name: '维修处理', path: '/manage/repair' }
      ]
    },
    { name: '新闻通知', path: '/news', icon: 'Message' },
    { name: '个人中心', path: '/profile', icon: 'User' }
  ],
}