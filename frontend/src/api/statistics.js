import request from '@/utils/request'

export const getHouseUtilization = () => {
  return request({
    url: 'v1/statistics/house-utilization',
    method: 'get'
  })
}

export const getRentIncome = () => {
  return request({
    url: 'v1/statistics/rent-income',
    method: 'get'
  })
}

export const getActiveUsers = () => {
  return request({
    url: 'v1/statistics/active-users',
    method: 'get'
  })
}

export const getComplaintRepairCount = () => {
  return request({
    url: 'v1/statistics/complaint-repair-count',
    method: 'get'
  })
}