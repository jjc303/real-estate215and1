// 租客端预约模拟数据
export const mockTenantReservations = [
    {
        id: 1,
        house_title: '中南大学14舍',
        house_address: '岳麓区麓山南路932号',
        landlord_name: '李阿姨',
        landlord_phone: '138****8888',
        reservation_date: '2024-01-15',
        reservation_time: '14:00-16:00',
        remark: '想下午看房，希望能详细介绍一下周边环境',
        status: 'pending'
    },
    {
        id: 2,
        house_title: '麓山南路88号',
        house_address: '岳麓区麓山南路88号',
        landlord_name: '王叔叔',
        landlord_phone: '139****9999',
        reservation_date: '2024-01-16',
        reservation_time: '10:00-12:00',
        remark: '',
        status: 'confirmed'
    },
    {
        id: 3,
        house_title: '天马小区3栋',
        house_address: '岳麓区天马小区3栋402',
        landlord_name: '张女士',
        landlord_phone: '137****7777',
        reservation_date: '2024-01-14',
        reservation_time: '09:00-11:00',
        remark: '已确认看房时间',
        status: 'completed'
    },
    {
        id: 4,
        house_title: '阳光公寓A座',
        house_address: '岳麓区阳光公寓A座1201',
        landlord_name: '刘先生',
        landlord_phone: '136****6666',
        reservation_date: '2024-01-13',
        reservation_time: '15:00-17:00',
        remark: '临时有事，无法前往',
        status: 'cancelled'
    }
]

// 房东端预约模拟数据
export const mockLandlordReservations = [
    {
        id: 1,
        house_title: '中南大学14舍',
        tenant_name: '张三',
        phone: '138****1234',
        reservation_date: '2024-01-15',
        reservation_time: '14:00-16:00',
        remark: '想下午看房，希望能详细介绍一下周边环境',
        status: 'pending'
    },
    {
        id: 2,
        house_title: '麓山南路88号',
        tenant_name: '李四',
        phone: '139****5678',
        reservation_date: '2024-01-16',
        reservation_time: '10:00-12:00',
        remark: '',
        status: 'pending'
    },
    {
        id: 3,
        house_title: '天马小区3栋',
        tenant_name: '王五',
        phone: '137****9012',
        reservation_date: '2024-01-14',
        reservation_time: '09:00-11:00',
        remark: '已确认看房时间',
        status: 'confirmed'
    },
    {
        id: 4,
        house_title: '阳光公寓A座',
        tenant_name: '赵六',
        phone: '136****3456',
        reservation_date: '2024-01-13',
        reservation_time: '15:00-17:00',
        remark: '租客临时有事取消',
        status: 'rejected'
    },
    {
        id: 5,
        house_title: '望月湖小区',
        tenant_name: '钱七',
        phone: '135****7890',
        reservation_date: '2024-01-10',
        reservation_time: '14:00-16:00',
        remark: '',
        status: 'completed'
    },
    {
        id: 6,
        house_title: '溁湾镇地铁口',
        tenant_name: '孙八',
        phone: '134****2345',
        reservation_date: '2024-01-17',
        reservation_time: '11:00-13:00',
        remark: '周末有空，希望能尽快安排',
        status: 'pending'
    }
]