import request from '@/utils/request'

export const listNews = (params) => {
  return request({
    url: 'v1/news',
    method: 'get',
    params
  })
}

export const getNewsDetail = (id) => {
  return request({
    url: `v1/news/${id}`,
    method: 'get'
  })
}

export const createNews = (data) => {
  return request({
    url: 'v1/news',
    method: 'post',
    data
  })
}

export const updateNews = (id, data) => {
  return request({
    url: `v1/news/${id}`,
    method: 'patch',
    data
  })
}

export const deleteNews = (id) => {
  return request({
    url: `v1/news/${id}`,
    method: 'delete'
  })
}
