import { useState } from 'react'
import { Card, Form, Input, Button, message, Typography, Space } from 'antd'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const { Title } = Typography

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)

  const onFinish = async (values) => {
    setLoading(true)
    try {
      await register(values)
      message.success('注册申请已提交，请等待管理员审核')
      navigate('/login')
    } catch (err) {
      message.error(err.response?.data?.detail || '注册失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <Card style={{ width: 440, boxShadow: '0 8px 24px rgba(0,0,0,0.15)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={3}>注册申请</Title>
          <p style={{ color: '#999' }}>提交后需管理员审核通过方可登录</p>
        </div>
        <Form onFinish={onFinish} size="large" layout="vertical">
          <Form.Item name="username" label="用户名" rules={[
            { required: true, message: '请输入用户名' },
            { min: 3, message: '至少3个字符' },
          ]}>
            <Input placeholder="用户名" />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[
            { required: true, message: '请输入密码' },
            { min: 6, message: '至少6个字符' },
          ]}>
            <Input.Password placeholder="密码" />
          </Form.Item>
          <Form.Item name="real_name" label="真实姓名" rules={[{ required: true, message: '请输入姓名' }]}>
            <Input placeholder="真实姓名" />
          </Form.Item>
          <Form.Item name="region" label="所属区域" rules={[{ required: true, message: '请输入区域' }]}>
            <Input placeholder="如：吉林省区" />
          </Form.Item>
          <Form.Item name="phone" label="手机号">
            <Input placeholder="手机号（选填）" />
          </Form.Item>
          <Form.Item name="email" label="邮箱">
            <Input placeholder="邮箱（选填）" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              提交注册申请
            </Button>
          </Form.Item>
        </Form>
        <div style={{ textAlign: 'center' }}>
          <Space>
            <span style={{ color: '#999' }}>已有账号？</span>
            <Link to="/login">返回登录</Link>
          </Space>
        </div>
      </Card>
    </div>
  )
}
