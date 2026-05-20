// 租客维修申请模拟数据
export const mockTenantRepairs = [
    {
        id: 1,
        title: '水龙头漏水',
        house_id: 1,
        house: {
            id: 1,
            title: '中南大学14舍'
        },
        type: 'water',
        description: '卫生间的水龙头一直漏水，已经影响正常使用，请尽快安排维修人员上门处理。',
        status: 'completed',
        created_at: '2024-01-10 09:30:00',
        processed_at: '2024-01-11 14:00:00'
    },
    {
        id: 2,
        title: '空调不制冷',
        house_id: 2,
        house: {
            id: 2,
            title: '麓山南路88号'
        },
        type: 'electricity',
        description: '主卧的空调不制冷了，夏天太热了，希望能尽快修好。',
        status: 'processing',
        created_at: '2024-01-14 11:20:00',
        processed_at: '2024-01-14 16:00:00'
    },
    {
        id: 3,
        title: '衣柜门损坏',
        house_id: 3,
        house: {
            id: 3,
            title: '天马小区3栋'
        },
        type: 'furniture',
        description: '衣柜门的铰链坏了，门无法正常关闭。',
        status: 'pending',
        created_at: '2024-01-15 15:00:00',
        processed_at: null
    },
    {
        id: 4,
        title: '灯泡烧坏',
        house_id: 1,
        house: {
            id: 1,
            title: '中南大学14舍'
        },
        type: 'electricity',
        description: '客厅的吸顶灯灯泡烧坏了，请更换新的灯泡。',
        status: 'pending',
        created_at: '2024-01-15 08:30:00',
        processed_at: null
    }
]

export const mockMyHouses = [
    {
        id: 1,
        title: '中南大学14舍'
    },
    {
        id: 2,
        title: '麓山南路88号'
    },
    {
        id: 3,
        title: '天马小区3栋'
    },
    {
        id: 4,
        title: '阳光公寓A座'
    },
    {
        id: 5,
        title: '河西王府井小区'
    }
]
