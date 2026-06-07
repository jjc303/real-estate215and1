import request from '@/utils/request'

// 房源智能问答
export const houseChat = (data) => {
    return request({
        url: 'v1/ai/house-chat',
        method: 'post',
        data
    })
}

// 通用对话
export const chat = (data) => {
    return request({
        url: 'v1/ai/chat',
        method: 'post',
        data
    })
}
