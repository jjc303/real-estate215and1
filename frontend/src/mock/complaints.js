// 投诉模拟数据
export const mockComplaints = [
    {
        id: 1,
        title: '房东态度恶劣',
        house_id: 1,
        house: {
            id: 1,
            title: '中南大学14舍'
        },
        type: 'service',
        description: '房东在沟通中态度非常恶劣，多次辱骂租客，严重影响租住体验。',
        status: 'completed',
        created_at: '2024-01-10 09:30:00',
        processed_at: '2024-01-12 14:00:00',
        response: '经核实，已对房东进行批评教育，房东已道歉。'
    },
    {
        id: 2,
        title: '房屋设施损坏无人维修',
        house_id: 2,
        house: {
            id: 2,
            title: '麓山南路88号'
        },
        type: 'house',
        description: '厨房的水槽已经坏了两个月了，报修多次房东一直不处理。',
        status: 'processing',
        created_at: '2024-01-14 11:20:00',
        processed_at: '2024-01-14 16:00:00',
        response: null
    },
    {
        id: 3,
        title: '违规收取额外费用',
        house_id: 3,
        house: {
            id: 3,
            title: '天马小区3栋'
        },
        type: 'fee',
        description: '房东在合同约定之外收取了额外的物业费，没有提前告知。',
        status: 'pending',
        created_at: '2024-01-15 15:00:00',
        processed_at: null,
        response: null
    },
    {
        id: 4,
        title: '合同条款不公平',
        house_id: 4,
        house: {
            id: 4,
            title: '阳光公寓A座'
        },
        type: 'contract',
        description: '合同中有些条款明显对租客不利，比如提前退租要扣除两个月租金。',
        status: 'completed',
        created_at: '2024-01-08 10:00:00',
        processed_at: '2024-01-10 09:00:00',
        response: '已协调双方重新签订补充协议，明确退租条款。'
    },
    {
        id: 5,
        title: '噪音扰民',
        house_id: 5,
        house: {
            id: 5,
            title: '河西王府井小区'
        },
        type: 'other',
        description: '楼上住户每天深夜都在装修，严重影响休息。',
        status: 'pending',
        created_at: '2024-01-15 08:30:00',
        processed_at: null,
        response: null
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
