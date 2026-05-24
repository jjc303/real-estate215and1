import request from '@/utils/request'

// 获取合同列表
export const getContractList = (params) => {
  return request({
    url: 'v1/contracts',
    method: 'get',
    params
  })
}

// 获取合同详情
export const getContractDetail = (id) => {
  return request({
    url: `v1/contracts/${id}`,
    method: 'get'
  })
}

// 创建合同
export const createContract = (data) => {
  return request({
    url: 'v1/contracts',
    method: 'post',
    data
  })
}

// 更新合同
export const updateContract = (id, data) => {
  return request({
    url: `v1/contracts/${id}`,
    method: 'put',
    data
  })
}

// 确认合同（租客确认）
export const confirmContract = (id) => {
  return request({
    url: `v1/contracts/${id}/confirm`,
    method: 'patch'
  })
}

// 拒绝合同（租客拒绝）
export const rejectContract = (id) => {
  return request({
    url: `v1/contracts/${id}/reject`,
    method: 'patch'
  })
}

// 取消合同（房东取消）
export const cancelContract = (id) => {
  return request({
    url: `v1/contracts/${id}/cancel`,
    method: 'patch'
  })
}

// 终止合同
export const terminateContract = (id) => {
  return request({
    url: `v1/contracts/${id}/terminate`,
    method: 'patch'
  })
}

// 删除合同
export const deleteContract = (id) => {
  return request({
    url: `v1/contracts/${id}`,
    method: 'delete'
  })
}