import { useState, useEffect } from 'react'
import { Table, Button, Card, Space, Input, Select, Modal, Form, InputNumber, message } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import api from '../../api/client'

export default function OpsCosts() {
  const [data, setData] = useState([])
  const [platforms, setPlatforms] = useState([])
  const [loading, setLoading] = useState(false)
  const [modal, setModal] = useState({ open: false, editing: null })
  const [form] = Form.useForm()
  const [filters, setFilters] = useState({ sales_unit: '', platform: '', month: '' })

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
      if (filters.sales_unit) params.sales_unit = filters.sales_unit
      if (filters.platform) params.platform_id = filters.platform
      if (filters.month) params.month = filters.month
      const res = await api.get('/reports/costs', { params })
      setData(res.data)
    } catch (e) { message.error('获取费用数据失败') }
    finally { setLoading(false) }
  }

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      await api.post('/reports/costs', values)
      message.success('已创建')
      setModal({ open: false, editing: null })
      form.resetFields()
      fetchData()
    } catch (e) {
      if (e.response?.data?.detail) message.error(e.response.data.detail)
    }
  }

  const columns = [
    { title: '销售单位', dataIndex: 'sales_unit', width: 120 },
    { title: '平台', dataIndex: 'platform_name', width: 80 },
    { title: '方案金额', dataIndex: 'plan_amount', width: 120, render: v => v?.toLocaleString() || '-' },
    { title: '累计费用', dataIndex: 'accumulated_cost', width: 120, render: v => v?.toFixed(2) || '-' },
    { title: '累计费比', dataIndex: 'cost_ratio', width: 100, render: v => v ? `${(v * 100).toFixed(2)}%` : '-' },
    { title: '累计交易额', dataIndex: 'transaction_amount', width: 120, render: v => v?.toLocaleString() || '-' },
    { title: '当月费用', dataIndex: 'month_cost', width: 120, render: v => v?.toFixed(2) || '-' },
    { title: '当月费比', dataIndex: 'month_cost_ratio', width: 100, render: v => v ? `${(v * 100).toFixed(2)}%` : '-' },
    { title: '月份', dataIndex: 'month', width: 80 },
  ]

  return (
    <div className="page-container">
      <div className="page-header">
        <h2>费用管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { form.resetFields(); setModal({ open: true, editing: null }) }}>新增费用记录</Button>
      </div>
      <Card>
        <div className="filter-bar">
          <Input.Search placeholder="销售单位" allowClear style={{ width: 150 }} onSearch={(v) => setFilters(prev => ({ ...prev, sales_unit: v }))} />
          <Select placeholder="平台" allowClear style={{ width: 120 }} options={platforms.map(p => ({ value: p.id, label: p.name }))} onChange={(v) => setFilters(prev => ({ ...prev, platform: v || '' }))} />
          <Input.Search placeholder="月份 如：2026-04" allowClear style={{ width: 150 }} onSearch={(v) => setFilters(prev => ({ ...prev, month: v }))} />
          <Button onClick={fetchData}>查询</Button>
        </div>
        <Table columns={columns} dataSource={data} rowKey="id" loading={loading} scroll={{ x: 1000 }} pagination={{ pageSize: 20, showTotal: t => `共 ${t} 条` }} />
      </Card>

      <Modal title="新增费用记录" open={modal.open} onOk={handleSave} onCancel={() => { setModal({ open: false, editing: null }); form.resetFields() }} width={600}>
        <Form form={form} layout="vertical">
          <Form.Item name="sales_unit" label="销售单位" rules={[{ required: true }]}><Input placeholder="如：吉林省区" /></Form.Item>
          <Form.Item name="platform_id" label="平台">
            <Select allowClear options={platforms.map(p => ({ value: p.id, label: p.name }))} />
          </Form.Item>
          <Form.Item name="plan_amount" label="方案金额"><InputNumber style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="accumulated_cost" label="累计费用"><InputNumber style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="cost_ratio" label="累计费比 (0-1)"><InputNumber min={0} max={1} step={0.01} style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="transaction_amount" label="累计交易额"><InputNumber style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="month_cost" label="当月费用"><InputNumber style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="month_cost_ratio" label="当月费比 (0-1)"><InputNumber min={0} max={1} step={0.01} style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="month_expected_transaction" label="当月预计交易额"><InputNumber style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="month" label="月份"><Input placeholder="如：2026-04" /></Form.Item>
          <Form.Item name="year" label="年份"><Input type="number" placeholder="如：2026" /></Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
