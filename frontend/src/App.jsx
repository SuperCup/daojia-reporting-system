import { Routes, Route, Navigate } from 'react-router-dom'
import { Spin } from 'antd'
import { useAuth } from './context/AuthContext'
import Login from './pages/Login'
import Register from './pages/Register'
import ClientLayout from './components/ClientLayout'
import OpsLayout from './components/OpsLayout'
import ClientActivities from './pages/client/Activities'
import ActivityForm from './pages/client/ActivityForm'
import ClientChannels from './pages/client/Channels'
import ClientProducts from './pages/client/Products'
import OpsDashboard from './pages/ops/Dashboard'
import OpsReports from './pages/ops/Reports'
import OpsReportDetail from './pages/ops/ReportDetail'
import OpsChannels from './pages/ops/Channels'
import OpsProducts from './pages/ops/Products'
import OpsUsers from './pages/ops/Users'
import OpsCosts from './pages/ops/Costs'

function ProtectedRoute({ children, roles }) {
  const { user, loading } = useAuth()
  if (loading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}><Spin size="large" /></div>
  }
  if (!user) {
    return <Navigate to="/login" />
  }
  if (roles && !roles.includes(user.role)) {
    return <Navigate to={user.role === 'client' ? '/client' : '/ops'} />
  }
  return children
}

export default function App() {
  const { user, loading } = useAuth()

  if (loading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}><Spin size="large" /></div>
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Client routes */}
      <Route path="/client" element={
        <ProtectedRoute roles={['client', 'ops', 'admin']}>
          <ClientLayout />
        </ProtectedRoute>
      }>
        <Route index element={<ClientActivities />} />
        <Route path="activities" element={<ClientActivities />} />
        <Route path="activities/new" element={<ActivityForm />} />
        <Route path="activities/:id/edit" element={<ActivityForm />} />
        <Route path="channels" element={<ClientChannels />} />
        <Route path="products" element={<ClientProducts />} />
      </Route>

      {/* Operations routes */}
      <Route path="/ops" element={
        <ProtectedRoute roles={['ops', 'admin']}>
          <OpsLayout />
        </ProtectedRoute>
      }>
        <Route index element={<OpsDashboard />} />
        <Route path="dashboard" element={<OpsDashboard />} />
        <Route path="reports" element={<OpsReports />} />
        <Route path="reports/:id" element={<OpsReportDetail />} />
        <Route path="channels" element={<OpsChannels />} />
        <Route path="products" element={<OpsProducts />} />
        <Route path="users" element={<OpsUsers />} />
        <Route path="costs" element={<OpsCosts />} />
      </Route>

      {/* Default redirect */}
      <Route path="*" element={
        user ? (
          <Navigate to={user.role === 'client' ? '/client' : '/ops'} />
        ) : (
          <Navigate to="/login" />
        )
      } />
    </Routes>
  )
}
