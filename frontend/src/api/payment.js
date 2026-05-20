import service from '@/utils/request'

// 创建支付
export const createPayment = (data) => {
  return service.post('/v1/payments', data)
}

// 获取支付列表
export const getPaymentList = (params = {}) => {
  return service.get('/v1/payments', { params })
}

// 获取支付详情
export const getPaymentDetail = (id) => {
  return service.get(`/v1/payments/${id}`)
}
