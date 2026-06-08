import service from '@/utils/request'

// 创建会话
export const createConversation = (houseId) => {
  return service.post('/v1/conversations', { "house_id": houseId })
}

// 获取会话列表
export const getConversationList = (params = {}) => {
  return service.get('/v1/conversations', { params })
}

// 获取会话详情
export const getConversationDetail = (id) => {
  return service.get(`/v1/conversations/${id}`)
}

// 获取消息列表
export const getMessageList = (conversationId, page = 1, pageSize = 100) => {
  return service.get(`/v1/conversations/${conversationId}/messages`, {
    params: { page, page_size: pageSize }
  })
}

// 发送消息
export const sendMessage = (conversationId, content) => {
  return service.post(`/v1/conversations/${conversationId}/messages`, {
    content: content
  })
}

// 标记已读
export const markAsRead = (conversationId) => {
  return service.patch(`/v1/conversations/${conversationId}/read`)
}