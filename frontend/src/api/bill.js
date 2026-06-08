import service from '@/utils/request'

// 获取账单列表
export const getBillList = (params = {}) => {
  return service.get('/v1/bills', { params })
}

// 获取账单详情
export const getBillDetail = (id) => {
  return service.get(`/v1/bills/${id}`)
}

// 创建账单
export const createBill = (data) => {
  return service.post('/v1/bills', data)
}

// 取消账单
export const cancelBill = (id) => {
  return service.patch(`/v1/bills/${id}/cancel`)
}

// 标记逾期
export const markBillOverdue = (id) => {
  return service.patch(`/v1/bills/${id}/mark-overdue`)
}

// 催缴提醒（批量检测逾期并通知）
export const checkOverdueBills = () => {
  return service.post('/v1/bills/check-overdue')
}

// 房东收入汇总
export const getLandlordIncomeSummary = () => {
  return service.get('/v1/bills/landlord/summary')
}

// 下载账单 PDF
export const downloadBill = (id) => {
  return service.get(`/v1/bills/${id}/download`, {
    responseType: 'blob'
  })
}
