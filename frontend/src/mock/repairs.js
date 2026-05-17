// 维修申请模拟数据
export const mockRepairs = [
    {
        id: 1,
        title: '水龙头漏水',
        house: {
            id: 1,
            title: '中南大学14舍'
        },
        tenant_name: '张三',
        type: 'water',
        description: '卫生间的水龙头一直漏水，已经影响正常使用，请尽快安排维修人员上门处理。',
        status: 'pending',
        created_at: '2024-01-15 09:30:00',
        processed_at: null
    },
    {
        id: 2,
        title: '空调不制冷',
        house: {
            id: 2,
            title: '麓山南路88号'
        },
        tenant_name: '李四',
        type: 'electricity',
        description: '主卧的空调不制冷了，夏天太热了，希望能尽快修好。',
        status: 'processing',
        created_at: '2024-01-14 14:20:00',
        processed_at: '2024-01-14 16:00:00'
    },
    {
        id: 3,
        title: '衣柜门损坏',
        house: {
            id: 3,
            title: '天马小区3栋'
        },
        tenant_name: '王五',
        type: 'furniture',
        description: '衣柜门的铰链坏了，门无法正常关闭。',
        status: 'completed',
        created_at: '2024-01-12 10:00:00',
        processed_at: '2024-01-13 09:00:00'
    },
    {
        id: 4,
        title: '灯泡烧坏',
        house: {
            id: 1,
            title: '中南大学14舍'
        },
        tenant_name: '赵六',
        type: 'electricity',
        description: '客厅的吸顶灯灯泡烧坏了，请更换新的灯泡。',
        status: 'pending',
        created_at: '2024-01-15 11:00:00',
        processed_at: null
    },
    {
        id: 5,
        title: '马桶堵塞',
        house: {
            id: 4,
            title: '阳光公寓A座'
        },
        tenant_name: '孙七',
        type: 'water',
        description: '卫生间马桶堵塞了，无法正常使用。',
        status: 'processing',
        created_at: '2024-01-15 08:30:00',
        processed_at: '2024-01-15 10:00:00'
    },
    {
        id: 6,
        title: '门锁故障',
        house: {
            id: 2,
            title: '麓山南路88号'
        },
        tenant_name: '周八',
        type: 'other',
        description: '房门锁不太灵敏，有时候打不开，需要维修。',
        status: 'completed',
        created_at: '2024-01-10 15:00:00',
        processed_at: '2024-01-11 10:00:00'
    }
]
