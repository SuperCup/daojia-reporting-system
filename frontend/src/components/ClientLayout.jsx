import { Layout, Menu, Avatar, Dropdown, Space } from 'antd'
import {
  HomeOutlined, UnorderedListOutlined, ShopOutlined, BoxOutlined,
  LogoutOutlined, UserOutlined
} from '@ant-design/icons'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const { Header, Sider, Content } = Layout

export default function ClientLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    { key: '/client', icon: <HomeOutlined />, label: '首页' },
    { key: '/client/activities', icon: <UnorderedListOutlined />, label: '活动提报' },
    { key: '/client/channels', icon: <ShopOutlined />, label: '渠道管理' },
    { key: '/client/products', icon: <BoxOutlined />, label: '商品管理' },
  ]

  const handleMenuClick = ({ key }) => {
    navigate(key)
  }

  const userMenu = {
    items: [
      { key: 'logout', icon: <LogoutOutlined />, label: '退出登录' },
    ],
    onClick: ({ key }) => {
      if (key === 'logout') {
        logout()
        navigate('/login')
      }
    }
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider breakpoint="lg" collapsedWidth="0" theme="dark">
        <div style={{ height: 48, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16, fontWeight: 600, padding: '0 8px' }}>
          到家提报系统
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: 16, fontWeight: 500 }}>
            {user?.role === 'ops' || user?.role === 'admin' ? '运营端 — 客户视图' : '客户端'}
          </span>
          <Dropdown menu={userMenu}>
            <Space style={{ cursor: 'pointer' }}>
              <Avatar icon={<UserOutlined />} />
              <span>{user?.real_name || user?.username}</span>
              <span style={{ color: '#999', fontSize: 12 }}>({user?.region})</span>
            </Space>
          </Dropdown>
        </Header>
        <Content style={{ margin: 0, background: '#f0f2f5' }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
