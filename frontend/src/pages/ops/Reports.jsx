import { useState, useEffect } from 'react'
import { Table, Button, Card, Space, Tag, Input, Select, DatePicker, message, Modal, Form, Radio } from 'antd'
import { EyeOutlined, CheckOutlined, CloseOutlined, DownloadOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import api from '../../api/client'
import dayjs from 'dayjs'

const { RangePicker } = DatePicker
const { TextArea } = Input

const statusMap = {
  draft: { text: '草稿', color: 'default' },
  submitted: { text: '待审核', color: 'processing' },
  approved: { text: '已通过', color: 'success' },
  rejected: { text: '已驳回', color: 'error' },
}

export default function OpsReports() {
  const navigate = useNavigate()
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [platforms, setPlatforms] = useState([])
  const [filters, setFilters] = useState({ status: '', region: '', platform_id: '', keyword: '' })
  const [reviewModal, setReviewModal] = useState({ open: false, activity: null })
  const [reviewForm] = Form.useForm()

  useEffect(() => {
    loadPlatforms()
    fetchData()
  }, [])

  const loadPlatforms = async () => {
    try { const res = await api.get('/platforms'); setPlatforms(res.data) } catch (e) {}
  }

  const fetchData = async () => {
    setLoading(true)
    try {
      const params = {}
      if (filters.status) params.status = filters.status
      if (filters.region) params.region = filters.region
      if (filters.platform_id) params.platform_id = filters.platform_id
      if (filters.keyword) params.keyword = filters.keyword
      const res = await api.get('/activities', { params: { ...params, page_size: 100 } })
      setData(res.data)
    } catch (e) { message.error('获取提报列表失败') }
    finally { setLoading(false) }
  }

  const handleReview = async () => {
    try {
      const values = await reviewForm.validateFields()
      await api.post(`/activities/${reviewModal.activity.id}/review`, values)
      message.success(values.status === 'approved' ? '已通过审核' : '已驳回')
      setReviewModal({ open: false, activity: null })
      reviewForm.resetFields()
      fetchData()
    } catch (e) {
      if (e.response?.data?.detail) message.error(e.response.data.detail)
    }
  }

  const handleExport = async () => {
    try {
      const res = await api.get('/reports/export/summary')
      const { columns, rows } = res.data
      if (!rows.length) { message.warning('无数据可导出'); return }
      // Convert to CSV
      const csv = [
        columns.join(','),
        ...rows.map(r => columns.map(c => `"${String(r[c] || '').replace(/"/g, '""')}"`).join(','))
      ].join('\n')
      const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `活动提报汇总_${dayjs().format('YYYYMMDD')}.csv`
      a.click()
      URL.revokeObjectURL(url)
      message.success('导出成功')
    } catch (e) { message.error('导出失败') }
  }

  const columns = [
    { title: '区域', dataIndex: 'region', width: 90 },
    { title: '活动时间', dataIndex: 'activity_time', width: 100 },
    { title: '活动机制', dataIndex: 'mechanism', ellipsis: true },
    { title: '渠道数', width: 60, render: (_, r) => r.channels?.length || 0 },
    { title: '商品数', width: 60, render: (_, r) => r.products?.length || 0 },
    { title: '平台', dataIndex: 'platform_name', width: 70 },
    { title: '券数量', dataIndex: 'voucher_quantity', width: 80, render: v => v?.toLocaleString() || '-' },
    { title: '状态', dataIndex: 'status', width: 80, render: s => { const m = statusMap[s] || { text: s, color: 'default' }; return <Tag color={m.color}>{m.text}</Tag> } },
    { title: '提报人', dataIndex: 'creator_name', width: 80 },
    { title: '提报时间', dataIndex: 'submitted_at', width: 140, render: v => v ? dayjs(v).format('MM-DD HH:mm') : '-' },
    { title: '操作', width: 200, fixed: 'right', render: (_, r) => (
      <Space>
        <Button size="small" icon={<EyeOutlined />} onClick={() => navigate(`/ops/reports/${r.id}`)}>明细</Button>
        {r.status === 'submitted' && (
          <Button size="small" type="primary" onClick={() => { setReviewModal({ open: true, activity: r }); reviewForm.resetFields() }}>审核</Button>
        )}
      </Space>
    )},
  ]

  return (
    <div className="page-container">
      <div className="page-header">
        <h2>提报管理</h2>
        <Button icon={<DownloadOutlined />} onClick={handleExport}>导出汇总</Button>
      </div>
      <Card>
        <div className="filter-bar">
          <Select placeholder="状态" allowClear style={{ width: 100 }} options={Object.entries(statusMap).map(([k, v]) => ({ value: k, label: v.text }))} onChange={(v) => setFilters(prev => ({ ...prev, status: v || '' }))} />
          <Input placeholder="区域" allowClear style={{ width: 100 }} onChange={(e) => setFilters(prev => ({ ...prev, region: e.target.value }))} />
          <Select placeholder="平台" allowClear style={{ width: 100 }} options={platforms.map(p => ({ value: p.id, label: p.name }))} onChange={(v) => setFilters(prev => ({ ...prev, platform_id: v || '' }))} />
          <Input.Search placeholder="搜索活动机制" allowClear style={{ width: 200 }} onSearch={(v) => setFilters(prev => ({ ...prev, keyword: v }))} />
          <Button type="primary" onClick={fetchData}>查询</Button>
        </div>
        <Table columns={columns} dataSource={data} rowKey="id" loading={loading} scroll={{ x: 1200 }} pagination={{ pageSize: 20, showTotal: t => `共 ${t} 条` }} />
      </Card>

      <Modal title="审核活动" open={reviewModal.open} onOk={handleReview} onCancel={() => { setReviewModal({ open: false, activity: null }); reviewForm.resetFields() }}>
        {reviewModal.activity && (
          <div style={{ marginBottom: 16, padding: 12, background: '#f6f8fa', borderRadius: 6 }}>
            <p style={{ margin: 0 }}><strong>区域：</strong>{reviewModal.activity.region}</p>
            <p style={{ margin: '4px 0' }}><strong>活动机制：</strong>{reviewModal.activity.mechanism}</p>
            <p style={{ margin: 0 }}><strong>活动时间：</strong>{reviewModal.activity.activity_time}</p>
          </div>
        )}
        <Form form={reviewForm} layout="vertical">
          <Form.Item name="status" label="审核结果" rules={[{ required: true, message: '请选择审核结果' }]}>
            <Radio.Group>
              <Radio value="approved">通过</Radio>
              <Radio value="rejected">驳回</Radio>
            </Radio.Group>
          </Form.Item>
          <Form.Item name="review_comment" label="审核意见">
            <TextArea rows={3} placeholder="审核意见（选填）" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
