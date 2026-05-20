import request from '@/utils/request'

export const getHouseList = (params) => {
  return request({
    url: 'v1/houses',
    method: 'get',
    params
  })
}

export const getHouseDetail = (houseId) => {
  return request({
    url: `v1/houses/${houseId}`,
    method: 'get'
  })
}

export const createHouse = (data) => {
  return request({
    url: 'v1/houses',
    method: 'post',
    data
  })
}

export const updateHouse = (houseId, data) => {
  return request({
    url: `v1/houses/${houseId}`,
    method: 'put',
    data
  })
}

export const deleteHouse = (houseId) => {
  return request({
    url: `v1/houses/${houseId}`,
    method: 'delete'
  })
}

export const publishHouse = (houseId) => {
  return request({
    url: `v1/houses/${houseId}/publish`,
    method: 'patch'
  })
}

export const offlineHouse = (houseId) => {
  return request({
    url: `v1/houses/${houseId}/offline`,
    method: 'patch'
  })
}
