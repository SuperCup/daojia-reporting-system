import { useState, useEffect } from 'react'
import { Card, Form, Input, InputNumber, Select, Button, message, Row, Col, Space, Table, Tag, Divider, AutoComplete } from 'antd'
import { ArrowLeftOutlined, SaveOutlined, SendOutlined } from '@ant-design/icons'
import { useNavigate, useParams } from 'react-router-dom'
import api from '../../api/client'
import { useAuth } from '../../context/AuthContext'

const { TextArea } = Input

export default function ActivityForm() {
  const { user } = useAuth()
  const { id } = useParams()
  const navigate = useNavigate()
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [platforms, setPlatforms] = useState([])
  const [channels, setChannels] = useState([])
  const [products, setProducts] = useState([])
  const [selectedChannels, setSelectedChannels] = useState([])
  const [selectedProducts, setSelectedProducts] = useState([])
  const [channelFilter, setChannelFilter] = useState({ type: '', keyword: '' })
  const [productFilter, setProductFilter] = useState({ brand: '', keyword: '' })

  useEffect(() => {
    loadPlatforms()
    loadChannels()
    loadProducts()
    if (id) loadActivity()
  }, [id])

  const loadPlatforms = async () => {
    try {
      const res = await api.get('/platforms')
      setPlatforms(res.data)
    } catch (e) { console.error(e) }
  }

  const loadChannels = async () => {
    try {
      const res = await api.get('/channels', { params: { page_size: 200 } })
      setChannels(res.data)
    } catch (e) { console.error(e) }
  }

  const loadProducts = async () => {
    try {
      const res = await api.get('/products', { params: { page_size: 200 } })
      setProducts(res.data)
    } catch (e) { console.error(e) }
  }

  const loadActivity = async () => {
    setLoading(true)
    try {
      const res = await api.get(`/activities/${id}`)
      const act = res.data
      form.setFieldsValue({
        title: act.title,
        region: act.region,
        activity_time: act.activity_time,
        mechanism: act.mechanism,
        platform_id: act.platform_id,
        voucher_quantity: act.voucher_quantity,
        budget: act.budget,
        remarks: act.remarks,
        prefix: act.prefix,
        brand: act.brand,
      })
      setSelectedChannels(act.channels?.map(c => c.id) || [])
      setSelectedProducts(act.products?.map(p => p.id) || [])
    } catch (e) {
      message.error('加载活动失败')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async (submit = false) => {
    try {
      const values = await form.validateFields()
      setSaving(true)
      const payload = {
        ...values,
        channel_ids: selectedChannels,
        product_ids: selectedProducts,
      }
      let res
      if (id) {
        res = await api.patch(`/activities/${id}`, payload)
        if (submit) {
          await api.post(`/activities/${id}/submit`)
          message.success('已提交，等待审核')
        } else {
          message.success('已保存')
        }
      } else {
        res = await api.post('/activities', { ...payload, status: 'draft' })
        if (submit) {
          await api.post(`/activities/${res.data.id}/submit`)
          message.success('已创建并提交')
        } else {
          message.success('已保存草稿')
        }
        navigate(`/client/activities/${res.data.id}/edit`)
      }
    } catch (err) {
      if (err.response?.data?.detail) {
        message.error(err.response.data.detail)
      }
    } finally {
      setSaving(false)
    }
  }

  const filteredChannels = channels.filter(ch => {
    if (channelFilter.type && ch.channel_type !== channelFilter.type) return false
    if (channelFilter.keyword && !ch.name.includes(channelFilter.keyword)) return false
    return true
  })

  const filteredProducts = products.filter(p => {
    if (productFilter.brand && p.brand_series !== productFilter.brand) return false
    if (productFilter.keyword && !p.name.includes(productFilter.keyword) && !p.upc.includes(productFilter.keyword)) return false
    return true
  })

  const channelTypes = [...new Set(channels.map(c => c.channel_type).filter(Boolean))]
  const brands = [...new Set(products.map(p => p.brand_series).filter(Boolean))]

  const channelCols = [
    { title: '选择', width: 50, render: (_, r) => (
      <input type="checkbox" checked={selectedChannels.includes(r.id)} onChange={(e) => {
        if (e.target.checked) setSelectedChannels(prev => [...prev, r.id])
        else setSelectedChannels(prev => prev.filter(x => x !== r.id))
      }} />
    )},
    { title: '渠道名称', dataIndex: 'name', ellipsis: true },
    { title: '类型', dataIndex: 'channel_type', width: 100 },
    { title: '平台', dataIndex: 'platform_name', width: 80 },
    { title: '店铺ID', dataIndex: 'platform_store_id', width: 100 },
  ]

  const productCols = [
    { title: '选择', width: 50, render: (_, r) => (
      <input type="checkbox" checked={selectedProducts.includes(r.id)} onChange={(e) => {
        if (e.target.checked) setSelectedProducts(prev => [...prev, r.id])
        else setSelectedProducts(prev => prev.filter(x => x !== r.id))
      }} />
    )},
    { title: 'UPC', dataIndex: 'upc', width: 130 },
    { title: '产品名称', dataIndex: 'name', ellipsis: true },
    { title: '品牌系列', dataIndex: 'brand_series', width: 130 },
    { title: '规格', dataIndex: 'spec', width: 80 },
  ]

  return (
    <div className="page-container">
      <div className="page-header">
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/client/activities')}>返回</Button>
          <h2>{id ? '编辑活动' : '创建活动'}</h2>
        </Space>
        <Space>
          <Button icon={<SaveOutlined />} loading={saving} onClick={() => handleSave(false)}>保存草稿</Button>
          <Button type="primary" icon={<SendOutlined />} loading={saving} onClick={() => handleSave(true)}>保存并提交</Button>
        </Space>
      </div>

      <Card loading={loading} style={{ marginBottom: 16 }}>
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={6}>
              <Form.Item name="region" label="区域" rules={[{ required: true, message: '请输入区域' }]}>
                <Input placeholder="如：吉林省区" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="activity_time" label="活动时间" rules={[{ required: true, message: '请输入活动时间' }]}>
                <Input placeholder="如：4.1-4.30 或 周六日" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="mechanism" label="活动机制" rules={[{ required: true, message: '请输入活动机制' }]}>
                <Input placeholder="如：满79减30（品18）" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="platform_id" label="投放平台">
                <Select placeholder="选择平台" allowClear options={platforms.map(p => ({ value: p.id, label: p.name }))} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={6}>
              <Form.Item name="brand" label="品牌">
                <Input placeholder="如：青啤" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="voucher_quantity" label="券数量">
                <InputNumber min={0} style={{ width: '100%' }} placeholder="如：80000" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="budget" label="预算金额">
                <InputNumber min={0} style={{ width: '100%' }} placeholder="如：80000" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="prefix" label="前缀">
                <Input placeholder="如：区域下沉" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="title" label="活动标题">
            <Input placeholder="选填，不填将自动生成" />
          </Form.Item>
          <Form.Item name="remarks" label="备注">
            <TextArea rows={2} placeholder="如：每个用户ID每天限一个" />
          </Form.Item>
        </Form>
      </Card>

      <Row gutter={16}>
        <Col span={12}>
          <Card title="投放渠道" size="small" extra={<Tag color="blue">{selectedChannels.length} 已选</Tag>}>
            <div className="filter-bar">
              <Select
                placeholder="渠道类型"
                allowClear
                style={{ width: 120 }}
                options={channelTypes.map(t => ({ value: t, label: t }))}
                value={channelFilter.type || undefined}
                onChange={(v) => setChannelFilter(prev => ({ ...prev, type: v || '' }))}
              />
              <Input.Search
                placeholder="搜索渠道名称"
                allowClear
                style={{ width: 200 }}
                onSearch={(v) => setChannelFilter(prev => ({ ...prev, keyword: v }))}
              />
            </div>
            <Table
              columns={channelCols}
              dataSource={filteredChannels}
              rowKey="id"
              size="small"
              scroll={{ y: 400 }}
              pagination={{ pageSize: 10, size: 'small' }}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="投放商品" size="small" extra={<Tag color="blue">{selectedProducts.length} 已选</Tag>}>
            <div className="filter-bar">
              <Select
                placeholder="品牌系列"
                allowClear
                style={{ width: 150 }}
                options={brands.map(b => ({ value: b, label: b }))}
                value={productFilter.brand || undefined}
                onChange={(v) => setProductFilter(prev => ({ ...prev, brand: v || '' }))}
              />
              <Input.Search
                placeholder="搜索产品名称/UPC"
                allowClear
                style={{ width: 200 }}
                onSearch={(v) => setProductFilter(prev => ({ ...prev, keyword: v }))}
              />
            </div>
            <Table
              columns={productCols}
              dataSource={filteredProducts}
              rowKey="id"
              size="small"
              scroll={{ y: 400 }}
              pagination={{ pageSize: 10, size: 'small' }}
            />
          </Card>
        </Col>
      </Row>
    </div>
  )
}
