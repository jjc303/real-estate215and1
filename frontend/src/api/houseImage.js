import request from '@/utils/request'

export const uploadHouseImage = (houseId, formData) => {
  return request({
    url: `v1/houses/${houseId}/images/upload`,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const getHouseImages = (houseId) => {
  return request({
    url: `v1/houses/${houseId}/images`,
    method: 'get'
  })
}

export const updateHouseImage = (houseId, imageId, data) => {
  return request({
    url: `v1/houses/${houseId}/images/${imageId}`,
    method: 'patch',
    data
  })
}

export const deleteHouseImage = (houseId, imageId) => {
  return request({
    url: `v1/houses/${houseId}/images/${imageId}`,
    method: 'delete'
  })
}
