import { useState, useEffect } from 'react'
import { Table, Button, Card, Space, Input, Select, Modal, Form, message, Tag } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import api from '../../api/client'

export default function ClientProducts() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [modal, setModal] = useState({ open: false, editing: null })
  const [form] = Form.useForm()
  const [filters, setFilters] = useState({ brand: '', keyword: '' })

  const fetchData = async () => {
    setLoading(true)
    try {
      const params = {}
      if (filters.brand) params.brand_series = filters.brand
      if (filters.keyword) params.keyword = filters.keyword
      const res = await api.get('/products', { params: { ...params, page_size: 200 } })
      setData(res.data)
    } catch (e) { message.error('获取商品失败') }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchData() }, [])

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      if (modal.editing) {
        await api.patch(`/products/${modal.editing.id}`, values)
        message.success('已更新')
      } else {
        await api.post('/products', values)
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
      await api.delete(`/products/${id}`)
      message.success('已停用')
      fetchData()
    } catch (e) { message.error('操作失败') }
  }

  const columns = [
    { title: 'UPC', dataIndex: 'upc', width: 140 },
    { title: '产品名称', dataIndex: 'name', ellipsis: true },
    { title: '品牌系列', dataIndex: 'brand_series', width: 130 },
    { title: '中心系列', dataIndex: 'center_series', width: 120 },
    { title: '规格(ml)', dataIndex: 'spec', width: 80 },
    { title: '装箱数', dataIndex: 'pack_quantity', width: 70 },
    { title: '状态', dataIndex: 'status', width: 70, render: s => <Tag color={s === 'active' ? 'green' : 'default'}>{s === 'active' ? '启用' : '停用'}</Tag> },
    { title: '操作', width: 120, render: (_, r) => (
      <Space>
        <Button size="small" icon={<EditOutlined />} onClick={() => handleEdit(r)} />
        <Button size="small" danger icon={<DeleteOutlined />} onClick={() => handleDelete(r.id)} />
      </Space>
    )},
  ]

  const brands = [...new Set(data.map(d => d.brand_series).filter(Boolean))]

  return (
    <div className="page-container">
      <div className="page-header">
        <h2>商品管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { form.resetFields(); setModal({ open: true, editing: null }) }}>新增商品</Button>
      </div>
      <Card>
        <div className="filter-bar">
          <Select placeholder="品牌系列" allowClear style={{ width: 150 }} options={brands.map(b => ({ value: b, label: b }))} onChange={(v) => setFilters(prev => ({ ...prev, brand: v || '' }))} />
          <Input.Search placeholder="搜索产品名称/UPC" allowClear style={{ width: 250 }} onSearch={(v) => setFilters(prev => ({ ...prev, keyword: v }))} />
          <Button onClick={fetchData}>查询</Button>
        </div>
        <Table columns={columns} dataSource={data} rowKey="id" loading={loading} scroll={{ x: 900 }} pagination={{ pageSize: 20, showTotal: t => `共 ${t} 条` }} />
      </Card>

      <Modal title={modal.editing ? '编辑商品' : '新增商品'} open={modal.open} onOk={handleSave} onCancel={() => { setModal({ open: false, editing: null }); form.resetFields() }} width={600}>
        <Form form={form} layout="vertical">
          <Form.Item name="upc" label="UPC条码" rules={[{ required: true, message: '请输入UPC条码' }]}>
            <Input placeholder="如：6901035614221" disabled={!!modal.editing} />
          </Form.Item>
          <Form.Item name="name" label="产品名称" rules={[{ required: true, message: '请输入产品名称' }]}>
            <Input placeholder="如：青岛啤酒 11°P白啤 500ml*12听/箱" />
          </Form.Item>
          <Form.Item name="brand_series" label="品牌系列">
            <Input placeholder="如：青岛白啤" />
          </Form.Item>
          <Form.Item name="center_series" label="中心系列">
            <Input placeholder="如：青岛听装" />
          </Form.Item>
          <Form.Item name="detail_series" label="明细系列">
            <Input placeholder="如：白啤听装" />
          </Form.Item>
          <Form.Item name="spec" label="单瓶规格(ml)">
            <Input placeholder="如：500" />
          </Form.Item>
          <Form.Item name="pack_quantity" label="装箱数">
            <Input type="number" placeholder="如：12" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
