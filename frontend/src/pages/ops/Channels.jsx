import { useState, useEffect } from 'react'
import { Table, Button, Card, Space, Input, Select, Modal, Form, message, Tag, Upload, BatchOperation } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, UploadOutlined } from '@ant-design/icons'
import api from '../../api/client'

export default function OpsChannels() {
  const [data, setData] = useState([])
  const [platforms, setPlatforms] = useState([])
  const [loading, setLoading] = useState(false)
  const [modal, setModal] = useState({ open: false, editing: null })
  const [form] = Form.useForm()
  const [filters, setFilters] = useState({ type: '', platform: '', keyword: '' })

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
      if (filters.type) params.channel_type = filters.type
      if (filters.platform) params.platform_id = filters.platform
      if (filters.keyword) params.keyword = filters.keyword
      const res = await api.get('/channels', { params: { ...params, page_size: 200 } })
      setData(res.data)
    } catch (e) { message.error('获取渠道失败') }
    finally { setLoading(false) }
  }

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      if (modal.editing) {
        await api.patch(`/channels/${modal.editing.id}`, values)
        message.success('已更新')
      } else {
        await api.post('/channels', values)
        message.success('已创建')
      }
      setModal({ open: false, editing: null })
      form.resetFields()
      fetchData()
    } catch (e) {
      if (e.response?.data?.detail) message.error(e.response.data.detail)
    }
  }

  const handleEdit = (record) => {
    setModal({ open: true, editing: record })
    form.setFieldsValue(record)
  }

  const handleDelete = async (id) => {
    try {
      await api.delete(`/channels/${id}`)
      message.success('已停用')
      fetchData()
    } catch (e) { message.error('操作失败') }
  }

  const columns = [
    { title: '渠道名称', dataIndex: 'name', ellipsis: true },
    { title: '类型', dataIndex: 'channel_type', width: 100, render: t => t ? <Tag>{t}</Tag> : '-' },
    { title: '平台', dataIndex: 'platform_name', width: 80 },
    { title: '店铺ID', dataIndex: 'platform_store_id', width: 120 },
    { title: '区域', dataIndex: 'region', width: 80 },
    { title: '地址', dataIndex: 'address', ellipsis: true },
    { title: '联系人', dataIndex: 'contact', width: 80 },
    { title: '状态', dataIndex: 'status', width: 70, render: s => <Tag color={s === 'active' ? 'green' : 'default'}>{s === 'active' ? '启用' : '停用'}</Tag> },
    { title: '操作', width: 120, render: (_, r) => (
      <Space>
        <Button size="small" icon={<EditOutlined />} onClick={() => handleEdit(r)} />
        <Button size="small" danger icon={<DeleteOutlined />} onClick={() => handleDelete(r.id)} />
      </Space>
    )},
  ]

  return (
    <div className="page-container">
      <div className="page-header">
        <h2>渠道管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { form.resetFields(); setModal({ open: true, editing: null }) }}>新增渠道</Button>
      </div>
      <Card>
        <div className="filter-bar">
          <Select placeholder="渠道类型" allowClear style={{ width: 120 }} onChange={(v) => setFilters(prev => ({ ...prev, type: v || '' }))} options={['便利', '超市', 'KA超市', '酒专营', '散店', '全渠道', '闪电仓'].map(t => ({ value: t, label: t }))} />
          <Select placeholder="平台" allowClear style={{ width: 120 }} options={platforms.map(p => ({ value: p.id, label: p.name }))} onChange={(v) => setFilters(prev => ({ ...prev, platform: v || '' }))} />
          <Input.Search placeholder="搜索渠道名称/店铺ID" allowClear style={{ width: 250 }} onSearch={(v) => setFilters(prev => ({ ...prev, keyword: v }))} />
          <Button onClick={fetchData}>查询</Button>
        </div>
        <Table columns={columns} dataSource={data} rowKey="id" loading={loading} scroll={{ x: 900 }} pagination={{ pageSize: 20, showTotal: t => `共 ${t} 条` }} />
      </Card>

      <Modal title={modal.editing ? '编辑渠道' : '新增渠道'} open={modal.open} onOk={handleSave} onCancel={() => { setModal({ open: false, editing: null }); form.resetFields() }} width={600}>
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="渠道名称" rules={[{ required: true }]}>
            <Input placeholder="如：优客超市" />
          </Form.Item>
          <Form.Item name="channel_type" label="渠道类型" rules={[{ required: true }]}>
            <Select options={['便利', '超市', 'KA超市', '酒专营', '散店', '全渠道', '闪电仓'].map(t => ({ value: t, label: t }))} />
          </Form.Item>
          <Form.Item name="platform_id" label="所属平台">
            <Select allowClear options={platforms.map(p => ({ value: p.id, label: p.name }))} />
          </Form.Item>
          <Form.Item name="platform_store_id" label="平台店铺ID">
            <Input />
          </Form.Item>
          <Form.Item name="region" label="区域"><Input /></Form.Item>
          <Form.Item name="address" label="地址"><Input.TextArea rows={2} /></Form.Item>
          <Form.Item name="contact" label="联系人"><Input /></Form.Item>
          <Form.Item name="status" label="状态">
            <Select options={[{ value: 'active', label: '启用' }, { value: 'inactive', label: '停用' }]} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
