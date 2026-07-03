import { useState, useEffect } from 'react'
import { Table, Button, Card, Space, Input, Select, Modal, Form, message, Tag, Popconfirm } from 'antd'
import { PlusOutlined, CheckOutlined, DeleteOutlined, KeyOutlined } from '@ant-design/icons'
import api from '../../api/client'

const roleMap = { admin: { text: '管理员', color: 'gold' }, ops: { text: '运营', color: 'blue' }, client: { text: '客户端', color: 'green' } }
const statusMap = { active: { text: '正常', color: 'green' }, pending: { text: '待审核', color: 'orange' }, disabled: { text: '已禁用', color: 'red' } }

export default function OpsUsers() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [modal, setModal] = useState({ open: false, editing: null })
  const [pwModal, setPwModal] = useState({ open: false, user: null })
  const [form] = Form.useForm()
  const [pwForm] = Form.useForm()
  const [filters, setFilters] = useState({ role: '', status: '', keyword: '' })

  const fetchData = async () => {
    setLoading(true)
    try {
      const params = {}
      if (filters.role) params.role = filters.role
      if (filters.status) params.status = filters.status
      if (filters.keyword) params.keyword = filters.keyword
      const res = await api.get('/users', { params })
      setData(res.data)
    } catch (e) { message.error('获取用户失败') }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchData() }, [])

  const handleCreate = async () => {
    try {
      const values = await form.validateFields()
      await api.post('/users', values)
      message.success('已创建')
      setModal({ open: false, editing: null })
      form.resetFields()
      fetchData()
    } catch (e) {
      if (e.response?.data?.detail) message.error(e.response.data.detail)
    }
  }

  const handleApprove = async (id) => {
    try {
      await api.post(`/users/${id}/approve`)
      message.success('已审核通过')
      fetchData()
    } catch (e) { message.error('操作失败') }
  }

  const handleDelete = async (id) => {
    try {
      await api.delete(`/users/${id}`)
      message.success('已禁用')
      fetchData()
    } catch (e) { message.error('操作失败') }
  }

  const handleResetPw = async () => {
    try {
      const values = await pwForm.validateFields()
      await api.patch(`/users/${pwModal.user.id}`, { password: values.password })
      message.success('密码已重置')
      setPwModal({ open: false, user: null })
      pwForm.resetFields()
    } catch (e) {
      if (e.response?.data?.detail) message.error(e.response.data.detail)
    }
  }

  const columns = [
    { title: '用户名', dataIndex: 'username', width: 120 },
    { title: '姓名', dataIndex: 'real_name', width: 100 },
    { title: '角色', dataIndex: 'role', width: 90, render: r => { const m = roleMap[r] || {}; return <Tag color={m.color}>{m.text}</Tag> } },
    { title: '区域', dataIndex: 'region', width: 100 },
    { title: '手机', dataIndex: 'phone', width: 120 },
    { title: '邮箱', dataIndex: 'email', ellipsis: true },
    { title: '状态', dataIndex: 'status', width: 90, render: s => { const m = statusMap[s] || {}; return <Tag color={m.color}>{m.text}</Tag> } },
    { title: '创建时间', dataIndex: 'created_at', width: 160, render: t => t ? new Date(t).toLocaleString('zh-CN') : '-' },
    { title: '操作', width: 220, render: (_, r) => (
      <Space>
        {r.status === 'pending' && (
          <Button size="small" type="primary" icon={<CheckOutlined />} onClick={() => handleApprove(r.id)}>审核</Button>
        )}
        <Button size="small" icon={<KeyOutlined />} onClick={() => setPwModal({ open: true, user: r })}>密码</Button>
        {r.status !== 'disabled' && (
          <Popconfirm title="确定禁用此用户？" onConfirm={() => handleDelete(r.id)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        )}
      </Space>
    )},
  ]

  return (
    <div className="page-container">
      <div className="page-header">
        <h2>用户管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { form.resetFields(); setModal({ open: true, editing: null }) }}>创建账号</Button>
      </div>
      <Card>
        <div className="filter-bar">
          <Select placeholder="角色" allowClear style={{ width: 100 }} options={Object.entries(roleMap).map(([k, v]) => ({ value: k, label: v.text }))} onChange={(v) => setFilters(prev => ({ ...prev, role: v || '' }))} />
          <Select placeholder="状态" allowClear style={{ width: 100 }} options={Object.entries(statusMap).map(([k, v]) => ({ value: k, label: v.text }))} onChange={(v) => setFilters(prev => ({ ...prev, status: v || '' }))} />
          <Input.Search placeholder="搜索用户名/姓名" allowClear style={{ width: 200 }} onSearch={(v) => setFilters(prev => ({ ...prev, keyword: v }))} />
          <Button onClick={fetchData}>查询</Button>
        </div>
        <Table columns={columns} dataSource={data} rowKey="id" loading={loading} scroll={{ x: 1000 }} pagination={{ pageSize: 20, showTotal: t => `共 ${t} 条` }} />
      </Card>

      <Modal title="创建账号" open={modal.open} onOk={handleCreate} onCancel={() => { setModal({ open: false, editing: null }); form.resetFields() }} width={500}>
        <Form form={form} layout="vertical">
          <Form.Item name="username" label="用户名" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true }]}><Input.Password /></Form.Item>
          <Form.Item name="role" label="角色" rules={[{ required: true }]} initialValue="client">
            <Select options={Object.entries(roleMap).map(([k, v]) => ({ value: k, label: v.text }))} />
          </Form.Item>
          <Form.Item name="real_name" label="姓名"><Input /></Form.Item>
          <Form.Item name="region" label="区域"><Input placeholder="如：吉林省区" /></Form.Item>
          <Form.Item name="phone" label="手机"><Input /></Form.Item>
          <Form.Item name="email" label="邮箱"><Input /></Form.Item>
        </Form>
      </Modal>

      <Modal title="重置密码" open={pwModal.open} onOk={handleResetPw} onCancel={() => { setPwModal({ open: false, user: null }); pwForm.resetFields() }}>
        <Form form={pwForm} layout="vertical">
          <Form.Item name="password" label="新密码" rules={[{ required: true }, { min: 6, message: '至少6个字符' }]}>
            <Input.Password />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
