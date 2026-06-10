import request from '@/utils/request'

export const listUsers = (params) => {
  return request({
    url: 'v1/admin/users',
    method: 'get',
    params
  })
}

export const getUserDetail = (userId) => {
  return request({
    url: `v1/admin/users/${userId}`,
    method: 'get'
  })
}

export const createUser = (data) => {
  return request({
    url: 'v1/admin/users',
    method: 'post',
    data
  })
}

export const updateUser = (userId, data) => {
  return request({
    url: `v1/admin/users/${userId}`,
    method: 'put',
    data
  })
}

export const updateUserStatus = (userId, status) => {
  return request({
    url: `v1/admin/users/${userId}/status`,
    method: 'patch',
    data: { status }
  })
}

export const listHouses = (params) => {
  return request({
    url: 'v1/admin/houses',
    method: 'get',
    params
  })
}

export const getHouseDetail = (houseId) => {
  return request({
    url: `v1/admin/houses/${houseId}`,
    method: 'get'
  })
}

export const listComplaints = (params) => {
  return request({
    url: 'v1/admin/complaints',
    method: 'get',
    params
  })
}

export const getComplaintDetail = (complaintId) => {
  return request({
    url: `v1/admin/complaints/${complaintId}`,
    method: 'get'
  })
}

export const processComplaint = (complaintId) => {
  return request({
    url: `v1/admin/complaints/${complaintId}/process`,
    method: 'patch'
  })
}

export const resolveComplaint = (complaintId) => {
  return request({
    url: `v1/admin/complaints/${complaintId}/resolve`,
    method: 'patch'
  })
}

export const rejectComplaint = (complaintId) => {
  return request({
    url: `v1/admin/complaints/${complaintId}/reject`,
    method: 'patch'
  })
}

export const closeComplaint = (complaintId) => {
  return request({
    url: `v1/admin/complaints/${complaintId}/close`,
    method: 'patch'
  })
}

export const listRepairs = (params) => {
  return request({
    url: 'v1/admin/repairs',
    method: 'get',
    params
  })
}

export const getRepairDetail = (repairId) => {
  return request({
    url: `v1/admin/repairs/${repairId}`,
    method: 'get'
  })
}

export const processRepair = (repairId) => {
  return request({
    url: `v1/admin/repairs/${repairId}/process`,
    method: 'patch'
  })
}

export const completeRepair = (repairId) => {
  return request({
    url: `v1/admin/repairs/${repairId}/complete`,
    method: 'patch'
  })
}

export const rejectRepair = (repairId) => {
  return request({
    url: `v1/admin/repairs/${repairId}/reject`,
    method: 'patch'
  })
}

export const closeRepair = (repairId) => {
  return request({
    url: `v1/admin/repairs/${repairId}/close`,
    method: 'patch'
  })
}

export const listContracts = (params) => {
  return request({
    url: 'v1/admin/contracts',
    method: 'get',
    params
  })
}

export const getContractDetail = (contractId) => {
  return request({
    url: `v1/admin/contracts/${contractId}`,
    method: 'get'
  })
}

export const updateContractStatus = (contractId, status) => {
  return request({
    url: `v1/admin/contracts/${contractId}/status`,
    method: 'patch',
    data: { status }
  })
}

export const listLogs = (params) => {
  return request({
    url: 'v1/admin/logs',
    method: 'get',
    params
  })
}

export const listBills = (params) => {
  return request({
    url: 'v1/admin/bills',
    method: 'get',
    params
  })
}

// 管理员房源状态管理
export const adminPublishHouse = (houseId) => {
  return request({
    url: `v1/admin/houses/${houseId}/publish`,
    method: 'patch'
  })
}

export const adminOfflineHouse = (houseId) => {
  return request({
    url: `v1/admin/houses/${houseId}/offline`,
    method: 'patch'
  })
}

export const adminSetHouseMaintenance = (houseId) => {
  return request({
    url: `v1/admin/houses/${houseId}/maintenance`,
    method: 'patch'
  })
}

export const adminRestoreHouse = (houseId) => {
  return request({
    url: `v1/admin/houses/${houseId}/restore`,
    method: 'patch'
  })
}