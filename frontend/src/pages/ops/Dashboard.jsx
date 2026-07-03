import { useState, useEffect } from 'react'
import { Row, Col, Card, Statistic, Table, Tag, Button, Progress, Spin, message } from 'antd'
import { ShoppingOutlined, BoxOutlined, TeamOutlined, DollarOutlined, CheckCircleOutlined, ClockCircleOutlined, CloseCircleOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import api from '../../api/client'

export default function OpsDashboard() {
  const [stats, setStats] = useState(null)
  const [recentActivities, setRecentActivities] = useState([])
  const [pendingUsers, setPendingUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    Promise.all([
      api.get('/reports/dashboard'),
      api.get('/activities', { params: { page_size: 10 } }),
      api.get('/users', { params: { status: 'pending' } }),
    ]).then(([statsRes, actRes, usersRes]) => {
      setStats(statsRes.data)
      setRecentActivities(actRes.data)
      setPendingUsers(usersRes.data)
    }).catch(() => {
      message.error('加载看板数据失败')
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', padding: 100 }}><Spin size="large" /></div>

  const activityCols = [
    { title: '区域', dataIndex: 'region', width: 90 },
    { title: '活动机制', dataIndex: 'mechanism', ellipsis: true },
    { title: '平台', dataIndex: 'platform_name', width: 70 },
    { title: '券数量', dataIndex: 'voucher_quantity', width: 80, render: v => v?.toLocaleString() || '-' },
    { title: '状态', dataIndex: 'status', width: 80, render: s => {
      const map = { draft: { text: '草稿', color: 'default' }, submitted: { text: '待审', color: 'processing' }, approved: { text: '已通过', color: 'success' }, rejected: { text: '已驳回', color: 'error' } }
      const m = map[s] || { text: s, color: 'default' }
      return <Tag color={m.color}>{m.text}</Tag>
    }},
    { title: '提报人', dataIndex: 'creator_name', width: 80 },
  ]

  const userCols = [
    { title: '用户名', dataIndex: 'username', width: 100 },
    { title: '姓名', dataIndex: 'real_name', width: 80 },
    { title: '区域', dataIndex: 'region', width: 80 },
    { title: '操作', width: 100, render: (_, r) => (
      <Button size="small" type="link" onClick={() => navigate('/ops/users')}>去审核</Button>
    )},
  ]

  return (
    <div className="page-container">
      <div className="page-header">
        <h2>运营看板</h2>
      </div>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={4}>
          <Card className="stat-card"><Statistic title="活动总数" value={stats?.total_activities || 0} prefix={<ShoppingOutlined />} /></Card>
        </Col>
        <Col span={4}>
          <Card className="stat-card"><Statistic title="待审核" value={stats?.submitted_activities || 0} prefix={<ClockCircleOutlined />} valueStyle={{ color: '#1677ff' }} /></Card>
        </Col>
        <Col span={4}>
          <Card className="stat-card"><Statistic title="已通过" value={stats?.approved_activities || 0} prefix={<CheckCircleOutlined />} valueStyle={{ color: '#52c41a' }} /></Card>
        </Col>
        <Col span={4}>
          <Card className="stat-card"><Statistic title="渠道总数" value={stats?.total_channels || 0} prefix={<BoxOutlined />} /></Card>
        </Col>
        <Col span={4}>
          <Card className="stat-card"><Statistic title="商品总数" value={stats?.total_products || 0} prefix={<BoxOutlined />} /></Card>
        </Col>
        <Col span={4}>
          <Card className="stat-card"><Statistic title="待审用户" value={stats?.pending_users || 0} prefix={<TeamOutlined />} valueStyle={{ color: '#fa8c16' }} /></Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={12}>
          <Card title="预算概览">
            <Statistic title="总预算" value={stats?.total_budget || 0} prefix={<DollarOutlined />} precision={2} />
            <div style={{ marginTop: 16 }}>
              <Progress
                percent={stats?.total_budget ? Math.round((stats.approved_budget / stats.total_budget) * 100) : 0}
                format={() => `已批 ${stats?.approved_budget?.toLocaleString() || 0}`}
              />
            </div>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="活动状态分布">
            <Row gutter={8}>
              <Col span={6}><Statistic title="草稿" value={stats?.draft_activities || 0} /></Col>
              <Col span={6}><Statistic title="已提交" value={stats?.submitted_activities || 0} valueStyle={{ color: '#1677ff' }} /></Col>
              <Col span={6}><Statistic title="已通过" value={stats?.approved_activities || 0} valueStyle={{ color: '#52c41a' }} /></Col>
              <Col span={6}><Statistic title="已驳回" value={stats?.rejected_activities || 0} valueStyle={{ color: '#ff4d4f' }} /></Col>
            </Row>
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={16}>
          <Card title="最近提报" extra={<Button type="link" onClick={() => navigate('/ops/reports')}>查看全部</Button>}>
            <Table columns={activityCols} dataSource={recentActivities} rowKey="id" size="small" pagination={false} />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="待审核用户" extra={<Button type="link" onClick={() => navigate('/ops/users')}>查看全部</Button>}>
            <Table columns={userCols} dataSource={pendingUsers} rowKey="id" size="small" pagination={false} />
          </Card>
        </Col>
      </Row>
    </div>
  )
}
