// /src/config/menus.js
export const menus = {
  guest: [
    { name: '中南找房', path: '/', icon: 'Home' },
    { name: '房源搜索', path: '/houseList', icon: 'Search' },
    { name: '租赁指南', path: '/handbook' },
    { name: '关于我们', path: '/about' },
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
    { 
      name: '消息中心', 
      path: '/message', 
      icon: 'Message',
      children: [
        { name: '留言管理', path: '/message/chat' },
        { name: '新闻查看', path: '/message/news' }
      ]
    },
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
        { name: '预约确认', path: '/manage/appointment' },
        { name: '合同管理', path: '/manage/contract' },
        { name: '租金监控', path: '/manage/rent' }
      ]
    },
    { 
      name: '消息中心', 
      path: '/message', 
      icon: 'Message',
      children: [
        { name: '留言管理', path: '/message/chat' },
        { name: '新闻管理', path: '/message/news' }
      ]
    },
    { name: '个人中心', path: '/profile', icon: 'User' }
  ],
  
  admin: [  // 管理员
    { name: '用户管理', path: '/admin/users', icon: 'Users' },
    { name: '房源监管', path: '/admin/houses', icon: 'Home' },
    { name: '投诉处理', path: '/admin/complaints', icon: 'Tool' },
    { name: '报表统计', path: '/admin/reports', icon: 'BarChart' },
    { name: '系统监控', path: '/admin/monitor', icon: 'Monitor' }
  ]
}