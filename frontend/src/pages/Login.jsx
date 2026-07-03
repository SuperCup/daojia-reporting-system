import { useState } from 'react'
import { Card, Form, Input, Button, message, Typography, Space } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const { Title } = Typography

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)

  const onFinish = async (values) => {
    setLoading(true)
    try {
      const user = await login(values.username, values.password)
      message.success('登录成功')
      navigate(user.role === 'client' ? '/client' : '/ops')
    } catch (err) {
      message.error(err.response?.data?.detail || '登录失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <Card style={{ width: 400, boxShadow: '0 8px 24px rgba(0,0,0,0.15)' }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <Title level={3}>到家平台提报管理系统</Title>
          <p style={{ color: '#999' }}>请登录您的账号</p>
        </div>
        <Form onFinish={onFinish} size="large">
          <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              登录
            </Button>
          </Form.Item>
        </Form>
        <div style={{ textAlign: 'center' }}>
          <Space>
            <span style={{ color: '#999' }}>没有账号？</span>
            <Link to="/register">注册申请</Link>
          </Space>
        </div>
        <div style={{ marginTop: 16, padding: 12, background: '#f6f8fa', borderRadius: 6, fontSize: 12, color: '#666' }}>
          <p style={{ margin: 0, fontWeight: 600 }}>测试账号：</p>
          <p style={{ margin: '4px 0' }}>管理员：admin / admin123456</p>
          <p style={{ margin: 0 }}>客户端：client_jilin / client123456</p>
        </div>
      </Card>
    </div>
  )
}
