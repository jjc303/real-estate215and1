import request from '@/utils/request'

export const uploadHouseVideo = (houseId, formData) => {
    return request({
        url: `v1/houses/${houseId}/videos/upload`,
        method: 'post',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

export const getHouseVideos = (houseId) => {
    return request({
        url: `v1/houses/${houseId}/videos`,
        method: 'get'
    })
}

export const deleteHouseVideo = (houseId, videoId) => {
    return request({
        url: `v1/houses/${houseId}/videos/${videoId}`,
        method: 'delete'
    })
}
