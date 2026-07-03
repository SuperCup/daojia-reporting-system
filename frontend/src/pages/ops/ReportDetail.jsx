import { useState, useEffect } from 'react'
import { Card, Descriptions, Table, Tag, Button, Space, Spin, message, Divider } from 'antd'
import { ArrowLeftOutlined } from '@ant-design/icons'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../../api/client'
import dayjs from 'dayjs'

const statusMap = {
  draft: { text: '草稿', color: 'default' },
  submitted: { text: '待审核', color: 'processing' },
  approved: { text: '已通过', color: 'success' },
  rejected: { text: '已驳回', color: 'error' },
}

export default function OpsReportDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get(`/reports/activities/${id}/detail`)
      .then(res => setData(res.data))
      .catch(() => message.error('加载明细失败'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', padding: 100 }}><Spin size="large" /></div>
  if (!data) return null

  const channelCols = [
    { title: '渠道名称', dataIndex: 'name' },
    { title: '类型', dataIndex: 'channel_type', width: 100, render: t => t ? <Tag>{t}</Tag> : '-' },
    { title: '平台', dataIndex: 'platform_name', width: 80 },
    { title: '店铺ID', dataIndex: 'platform_store_id', width: 120 },
    { title: '区域', dataIndex: 'region', width: 80 },
    { title: '地址', dataIndex: 'address', ellipsis: true },
  ]

  const productCols = [
    { title: 'UPC', dataIndex: 'upc', width: 140 },
    { title: '产品名称', dataIndex: 'name' },
    { title: '品牌系列', dataIndex: 'brand_series', width: 130 },
    { title: '中心系列', dataIndex: 'center_series', width: 120 },
    { title: '规格', dataIndex: 'spec', width: 80 },
    { title: '装箱数', dataIndex: 'pack_quantity', width: 70 },
  ]

  return (
    <div className="page-container">
      <div className="page-header">
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/ops/reports')}>返回</Button>
          <h2>提报明细</h2>
        </Space>
      </div>

      <Card style={{ marginBottom: 16 }}>
        <Descriptions title="活动基本信息" bordered column={3} size="small">
          <Descriptions.Item label="区域">{data.region}</Descriptions.Item>
          <Descriptions.Item label="活动时间">{data.activity_time}</Descriptions.Item>
          <Descriptions.Item label="活动机制">{data.mechanism}</Descriptions.Item>
          <Descriptions.Item label="投放平台">{data.platform_name || '-'}</Descriptions.Item>
          <Descriptions.Item label="渠道类型">{data.channel_type || '-'}</Descriptions.Item>
          <Descriptions.Item label="券数量">{data.voucher_quantity?.toLocaleString() || '-'}</Descriptions.Item>
          <Descriptions.Item label="预算金额">{data.budget?.toLocaleString() || '-'}</Descriptions.Item>
          <Descriptions.Item label="品牌">{data.brand || '-'}</Descriptions.Item>
          <Descriptions.Item label="前缀">{data.prefix || '-'}</Descriptions.Item>
          <Descriptions.Item label="状态" span={3}>
            {(() => { const m = statusMap[data.status] || { text: data.status, color: 'default' }; return <Tag color={m.color}>{m.text}</Tag> })()}
          </Descriptions.Item>
          <Descriptions.Item label="备注" span={3}>{data.remarks || '-'}</Descriptions.Item>
        </Descriptions>

        <Divider />

        <Descriptions title="提报与审核信息" bordered column={2} size="small">
          <Descriptions.Item label="提报人">{data.creator_name || '-'}</Descriptions.Item>
          <Descriptions.Item label="提报时间">{data.submitted_at ? dayjs(data.submitted_at).format('YYYY-MM-DD HH:mm:ss') : '-'}</Descriptions.Item>
          <Descriptions.Item label="审核人">{data.reviewer_name || '-'}</Descriptions.Item>
          <Descriptions.Item label="审核时间">{data.reviewed_at ? dayjs(data.reviewed_at).format('YYYY-MM-DD HH:mm:ss') : '-'}</Descriptions.Item>
          <Descriptions.Item label="审核意见" span={2}>{data.review_comment || '-'}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title={`投放渠道 (${data.channels?.length || 0})`} style={{ marginBottom: 16 }}>
        <Table columns={channelCols} dataSource={data.channels} rowKey="id" size="small" pagination={false} />
      </Card>

      <Card title={`投放商品 (${data.products?.length || 0})`}>
        <Table columns={productCols} dataSource={data.products} rowKey="id" size="small" pagination={false} scroll={{ x: 700 }} />
      </Card>
    </div>
  )
}
