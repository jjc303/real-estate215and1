import service from '@/utils/request'

// 添加收藏
export const addFavorite = (houseId) => {
  return service.post('/v1/favorites', { house_id: houseId })
}

// 获取收藏列表
export const getFavoriteList = (params = {}) => {
  return service.get('/v1/favorites', { params })
}

// 删除收藏
export const removeFavorite = (houseId) => {
  return service.delete(`/v1/favorites/${houseId}`)
}