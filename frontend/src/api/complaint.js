import service from '@/utils/request'

// 创建投诉
export const createComplaint = (data) => {
  return service.post('/v1/complaints', data)
}

// 获取投诉列表
export const getComplaintList = (params = {}) => {
  return service.get('/v1/complaints', { params })
}

// 获取投诉详情
export const getComplaintDetail = (id) => {
  return service.get(`/v1/complaints/${id}`)
}

// 处理投诉
export const processComplaint = (id) => {
  return service.patch(`/v1/complaints/${id}/process`)
}

// 解决投诉
export const resolveComplaint = (id) => {
  return service.patch(`/v1/complaints/${id}/resolve`)
}

// 拒绝投诉
export const rejectComplaint = (id) => {
  return service.patch(`/v1/complaints/${id}/reject`)
}

// 关闭投诉
export const closeComplaint = (id) => {
  return service.patch(`/v1/complaints/${id}/close`)
}
