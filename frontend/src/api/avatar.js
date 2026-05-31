import request from '@/utils/request'

export const uploadAvatar = (formData) => {
  return request({
    url: 'v1/users/me/avatar/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const getCurrentAvatar = () => {
  return request({
    url: 'v1/users/me/avatar',
    method: 'get'
  })
}

export const getAvatarList = (params) => {
  return request({
    url: 'v1/users/me/avatars',
    method: 'get',
    params
  })
}