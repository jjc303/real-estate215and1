import service from '@/utils/request'

// 创建预约
export const createAppointment = (data) => {
  return service.post('/v1/appointments', data)
}

// 获取预约列表
export const getAppointmentList = (params = {}) => {
  return service.get('/v1/appointments', { params })
}

// 获取预约详情
export const getAppointmentDetail = (id) => {
  return service.get(`/v1/appointments/${id}`)
}

// 确认预约
export const confirmAppointment = (id) => {
  return service.patch(`/v1/appointments/${id}/confirm`)
}

// 拒绝预约
export const rejectAppointment = (id) => {
  return service.patch(`/v1/appointments/${id}/reject`)
}

// 取消预约
export const cancelAppointment = (id) => {
  return service.patch(`/v1/appointments/${id}/cancel`)
}
