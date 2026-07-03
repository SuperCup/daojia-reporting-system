import { Layout, Menu, Avatar, Dropdown, Space, Tag } from 'antd'
import {
  DashboardOutlined, FileSearchOutlined, ShopOutlined, BoxOutlined,
  TeamOutlined, DollarOutlined, LogoutOutlined, UserOutlined
} from '@ant-design/icons'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const { Header, Sider, Content } = Layout

export default function OpsLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    { key: '/ops/dashboard', icon: <DashboardOutlined />, label: '运营看板' },
    { key: '/ops/reports', icon: <FileSearchOutlined />, label: '提报管理' },
    { key: '/ops/channels', icon: <ShopOutlined />, label: '渠道管理' },
    { key: '/ops/products', icon: <BoxOutlined />, label: '商品管理' },
    { key: '/ops/users', icon: <TeamOutlined />, label: '用户管理' },
    { key: '/ops/costs', icon: <DollarOutlined />, label: '费用管理' },
  ]

  const handleMenuClick = ({ key }) => navigate(key)

  const userMenu = {
    items: [
      { key: 'client', icon: <UserOutlined />, label: '切换到客户端' },
      { type: 'divider' },
      { key: 'logout', icon: <LogoutOutlined />, label: '退出登录' },
    ],
    onClick: ({ key }) => {
      if (key === 'logout') {
        logout()
        navigate('/login')
      } else if (key === 'client') {
        navigate('/client')
      }
    }
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider breakpoint="lg" collapsedWidth="0" theme="dark" width={220}>
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
          <Space>
            <Tag color="blue">运营端</Tag>
            {user?.role === 'admin' && <Tag color="gold">管理员</Tag>}
          </Space>
          <Dropdown menu={userMenu}>
            <Space style={{ cursor: 'pointer' }}>
              <Avatar icon={<UserOutlined />} />
              <span>{user?.real_name || user?.username}</span>
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
