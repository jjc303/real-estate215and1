import service from '@/utils/request'

// 创建报修
export const createRepair = (data) => {
  return service.post('/v1/repairs', data)
}

// 获取报修列表
export const getRepairList = (params = {}) => {
  return service.get('/v1/repairs', { params })
}

// 获取报修详情
export const getRepairDetail = (id) => {
  return service.get(`/v1/repairs/${id}`)
}

// 处理报修
export const processRepair = (id) => {
  return service.patch(`/v1/repairs/${id}/process`)
}

// 完成报修
export const completeRepair = (id) => {
  return service.patch(`/v1/repairs/${id}/complete`)
}

// 拒绝报修
export const rejectRepair = (id) => {
  return service.patch(`/v1/repairs/${id}/reject`)
}

// 关闭报修
export const closeRepair = (id) => {
  return service.patch(`/v1/repairs/${id}/close`)
}

// 重开启报修
export const reopenRepair = (id) => {
  return service.patch(`/v1/repairs/${id}/reopen`)
}
