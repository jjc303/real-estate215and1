import request from '@/utils/request'

// 获取通知列表
export const getNotificationList = (params) => {
  return request({
    url: 'v1/notifications',
    method: 'get',
    params
  })
}

// 获取通知详情
export const getNotificationDetail = (id) => {
  return request({
    url: `v1/notifications/${id}`,
    method: 'get'
  })
}

// 标记通知已读
export const markNotificationRead = (id) => {
  return request({
    url: `v1/notifications/${id}/read`,
    method: 'patch'
  })
}

// 删除通知
export const deleteNotification = (id) => {
  return request({
    url: `v1/notifications/${id}`,
    method: 'delete'
  })
}
