import { useState, useEffect } from 'react'
import { Table, Button, Card, Space, Tag, Input, Select, message, Modal, Popconfirm } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SendOutlined, EyeOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import api from '../../api/client'
import { useAuth } from '../../context/AuthContext'

const statusMap = {
  draft: { text: '草稿', color: 'default' },
  submitted: { text: '已提交', color: 'processing' },
  approved: { text: '已通过', color: 'success' },
  rejected: { text: '已驳回', color: 'error' },
}

export default function ClientActivities() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20, total: 0 })
  const [filters, setFilters] = useState({ status: '', keyword: '' })

  const fetchData = async (page = 1, pageSize = 20) => {
    setLoading(true)
    try {
      const params = { page, page_size: pageSize }
      if (filters.status) params.status = filters.status
      if (filters.keyword) params.keyword = filters.keyword
      const res = await api.get('/activities', { params })
      setData(res.data)
      setPagination(prev => ({ ...prev, current: page, total: res.data.length }))
    } catch (err) {
      message.error('获取活动列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData(1) }, [])

  const handleSubmit = async (id) => {
    try {
      await api.post(`/activities/${id}/submit`)
      message.success('活动已提交，等待审核')
      fetchData(pagination.current)
    } catch (err) {
      message.error(err.response?.data?.detail || '提交失败')
    }
  }

  const handleDelete = async (id) => {
    try {
      await api.delete(`/activities/${id}`)
      message.success('已删除')
      fetchData(pagination.current)
    } catch (err) {
      message.error(err.response?.data?.detail || '删除失败')
    }
  }

  const columns = [
    {
      title: '区域', dataIndex: 'region', width: 100,
    },
    {
      title: '活动时间', dataIndex: 'activity_time', width: 120,
    },
    {
      title: '活动机制', dataIndex: 'mechananism', ellipsis: true,
      render: (_, r) => r.mechanism,
    },
    {
      title: '平台', dataIndex: 'platform_name', width: 80,
    },
    {
      title: '渠道数', dataIndex: 'channels', width: 70,
      render: (ch) => ch?.length || 0,
    },
    {
      title: '商品数', dataIndex: 'products', width: 70,
      render: (p) => p?.length || 0,
    },
    {
      title: '券数量', dataIndex: 'voucher_quantity', width: 90,
      render: (v) => v?.toLocaleString() || '-',
    },
    {
      title: '状态', dataIndex: 'status', width: 90,
      render: (s) => {
        const m = statusMap[s] || { text: s, color: 'default' }
        return <Tag color={m.color}>{m.text}</Tag>
      },
    },
    {
      title: '操作', width: 200, fixed: 'right',
      render: (_, r) => (
        <Space>
          <Button size="small" icon={<EyeOutlined />} onClick={() => navigate(`/client/activities/${r.id}/edit`)}>查看</Button>
          {(r.status === 'draft' || r.status === 'rejected') && (
            <>
              <Button size="small" type="primary" icon={<EditOutlined />} onClick={() => navigate(`/client/activities/${r.id}/edit`)}>编辑</Button>
              <Button size="small" icon={<SendOutlined />} onClick={() => handleSubmit(r.id)}>提交</Button>
              <Popconfirm title="确定删除此活动？" onConfirm={() => handleDelete(r.id)}>
                <Button size="small" danger icon={<DeleteOutlined />} />
              </Popconfirm>
            </>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div className="page-container">
      <div className="page-header">
        <h2>活动提报</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/client/activities/new')}>
          创建活动
        </Button>
      </div>
      <Card>
        <div className="filter-bar">
          <Select
            placeholder="状态筛选"
            allowClear
            style={{ width: 120 }}
            value={filters.status || undefined}
            onChange={(v) => setFilters(prev => ({ ...prev, status: v || '' }))}
            options={Object.entries(statusMap).map(([k, v]) => ({ value: k, label: v.text }))}
          />
          <Input.Search
            placeholder="搜索活动机制/品牌"
            allowClear
            style={{ width: 250 }}
            onSearch={(v) => { setFilters(prev => ({ ...prev, keyword: v })); fetchData(1) }}
          />
          <Button onClick={() => fetchData(1)}>查询</Button>
        </div>
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1000 }}
          pagination={{
            ...pagination,
            onChange: (page, pageSize) => fetchData(page, pageSize),
            showTotal: (t) => `共 ${t} 条`,
          }}
        />
      </Card>
    </div>
  )
}
