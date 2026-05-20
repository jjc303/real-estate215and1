// 租客端账单模拟数据
export const mockTenantBills = [
  {
    id: 1,
    contract_id: 1,
    house_id: 1,
    tenant_id: 2,
    landlord_id: 3,
    period: '2024年1月',
    amount: '5000.00',
    status: 'paid',
    due_date: '2024-01-10',
    paid_date: '2024-01-05',
    created_at: '2024-01-01T00:00:00',
    updated_at: '2024-01-05T10:00:00',
    house: {
      id: 1,
      title: '中南大学14舍',
      region: '岳麓区',
      address: '中南大学14舍'
    }
  },
  {
    id: 2,
    contract_id: 1,
    house_id: 1,
    tenant_id: 2,
    landlord_id: 3,
    period: '2024年2月',
    amount: '5000.00',
    status: 'unpaid',
    due_date: '2024-02-10',
    paid_date: null,
    created_at: '2024-02-01T00:00:00',
    updated_at: '2024-02-01T00:00:00',
    house: {
      id: 1,
      title: '中南大学14舍',
      region: '岳麓区',
      address: '中南大学14舍'
    }
  },
  {
    id: 3,
    contract_id: 2,
    house_id: 2,
    tenant_id: 4,
    landlord_id: 5,
    period: '2024年1月',
    amount: '3500.00',
    status: 'overdue',
    due_date: '2024-01-15',
    paid_date: null,
    created_at: '2024-01-01T00:00:00',
    updated_at: '2024-01-01T00:00:00',
    house: {
      id: 2,
      title: '麓山南路88号',
      region: '岳麓区',
      address: '麓山南路88号'
    }
  },
  {
    id: 5,
    contract_id: 4,
    house_id: 4,
    tenant_id: 8,
    landlord_id: 9,
    period: '2024年2月',
    amount: '4200.00',
    status: 'unpaid',
    due_date: '2024-02-12',
    paid_date: null,
    created_at: '2024-02-01T00:00:00',
    updated_at: '2024-02-01T00:00:00',
    house: {
      id: 4,
      title: '阳光公寓A座',
      region: '雨花区',
      address: '阳光公寓A座'
    }
  }
]

// 房东端账单模拟数据
export const mockLandlordBills = [
  {
    id: 1,
    contract_id: 1,
    house_id: 1,
    tenant_id: 2,
    tenant_name: '张三',
    landlord_id: 3,
    period: '2024年1月',
    amount: '5000.00',
    status: 'paid',
    due_date: '2024-01-10',
    paid_date: '2024-01-05',
    created_at: '2024-01-01T00:00:00',
    updated_at: '2024-01-05T10:00:00',
    house: {
      id: 1,
      title: '中南大学14舍',
      region: '岳麓区',
      address: '中南大学14舍'
    }
  },
  {
    id: 2,
    contract_id: 1,
    house_id: 1,
    tenant_id: 2,
    tenant_name: '张三',
    landlord_id: 3,
    period: '2024年2月',
    amount: '5000.00',
    status: 'unpaid',
    due_date: '2024-02-10',
    paid_date: null,
    created_at: '2024-02-01T00:00:00',
    updated_at: '2024-02-01T00:00:00',
    house: {
      id: 1,
      title: '中南大学14舍',
      region: '岳麓区',
      address: '中南大学14舍'
    }
  },
  {
    id: 3,
    contract_id: 2,
    house_id: 2,
    tenant_id: 4,
    tenant_name: '李四',
    landlord_id: 5,
    period: '2024年1月',
    amount: '3500.00',
    status: 'overdue',
    due_date: '2024-01-15',
    paid_date: null,
    created_at: '2024-01-01T00:00:00',
    updated_at: '2024-01-01T00:00:00',
    house: {
      id: 2,
      title: '麓山南路88号',
      region: '岳麓区',
      address: '麓山南路88号'
    }
  },
  {
    id: 4,
    contract_id: 3,
    house_id: 3,
    tenant_id: 6,
    tenant_name: '王五',
    landlord_id: 7,
    period: '2024年1月',
    amount: '2800.00',
    status: 'paid',
    due_date: '2024-01-08',
    paid_date: '2024-01-06',
    created_at: '2024-01-01T00:00:00',
    updated_at: '2024-01-06T15:00:00',
    house: {
      id: 3,
      title: '天马小区3栋',
      region: '岳麓区',
      address: '天马小区3栋'
    }
  },
  {
    id: 5,
    contract_id: 4,
    house_id: 4,
    tenant_id: 8,
    tenant_name: '赵六',
    landlord_id: 9,
    period: '2024年2月',
    amount: '4200.00',
    status: 'unpaid',
    due_date: '2024-02-12',
    paid_date: null,
    created_at: '2024-02-01T00:00:00',
    updated_at: '2024-02-01T00:00:00',
    house: {
      id: 4,
      title: '阳光公寓A座',
      region: '雨花区',
      address: '阳光公寓A座'
    }
  },
  {
    id: 6,
    contract_id: 2,
    house_id: 2,
    tenant_id: 4,
    tenant_name: '李四',
    landlord_id: 5,
    period: '2024年2月',
    amount: '3500.00',
    status: 'unpaid',
    due_date: '2024-02-15',
    paid_date: null,
    created_at: '2024-02-01T00:00:00',
    updated_at: '2024-02-01T00:00:00',
    house: {
      id: 2,
      title: '麓山南路88号',
      region: '岳麓区',
      address: '麓山南路88号'
    }
  }
]