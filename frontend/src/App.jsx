import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import AgentChatPage from './pages/AgentChatPage'
import ClaimsPage from './pages/ClaimsPage'
import ClaimDetailPage from './pages/ClaimDetailPage'
import ApprovalsPage from './pages/ApprovalsPage'
import PoliciesPage from './pages/PoliciesPage'
import AuditPage from './pages/AuditPage'
import EvaluationPage from './pages/EvaluationPage'
import ProfilePage from './pages/ProfilePage'
import AdminPage from './pages/AdminPage'

function ProtectedRoute({ children, roles }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="flex items-center justify-center h-screen"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div></div>
  if (!user) return <Navigate to="/login" replace />
  if (roles && !roles.includes(user.role)) return <Navigate to="/dashboard" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="agent" element={<AgentChatPage />} />
        <Route path="claims" element={<ClaimsPage />} />
        <Route path="claims/:claimId" element={<ClaimDetailPage />} />
        <Route path="approvals" element={<ProtectedRoute roles={['MANAGER', 'ADMIN']}><ApprovalsPage /></ProtectedRoute>} />
        <Route path="policies" element={<ProtectedRoute roles={['ADMIN']}><PoliciesPage /></ProtectedRoute>} />
        <Route path="audit" element={<ProtectedRoute roles={['MANAGER', 'ADMIN']}><AuditPage /></ProtectedRoute>} />
        <Route path="evaluation" element={<ProtectedRoute roles={['ADMIN']}><EvaluationPage /></ProtectedRoute>} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="admin" element={<ProtectedRoute roles={['ADMIN']}><AdminPage /></ProtectedRoute>} />
      </Route>
    </Routes>
  )
}
