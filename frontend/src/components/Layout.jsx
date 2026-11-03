import React from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  Shield,
  LayoutDashboard,
  Bot,
  Receipt,
  CheckCircle,
  FileText,
  History,
  BarChart3,
  User,
  LogOut
} from 'lucide-react'

export default function Layout() {
  const { user, logout } = useAuth()
  const location = useLocation()

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'AI Agent Workspace', path: '/agent', icon: Bot },
    { name: 'Expense Claims', path: '/claims', icon: Receipt },
    ...(user?.role === 'MANAGER' || user?.role === 'ADMIN'
      ? [{ name: 'Approvals Queue', path: '/approvals', icon: CheckCircle }]
      : []),
    ...(user?.role === 'ADMIN'
      ? [{ name: 'Policy Management', path: '/policies', icon: FileText }]
      : []),
    { name: 'Audit Logs', path: '/audit', icon: History },
    { name: 'Evaluation Benchmarks', path: '/evaluation', icon: BarChart3 },
  ]

  return (
    <div className="flex h-screen bg-slate-50 text-slate-900">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-white flex flex-col border-r border-slate-800">
        <div className="p-5 flex items-center space-x-3 border-b border-slate-800">
          <div className="p-2 bg-gradient-to-tr from-purple-600 to-teal-500 rounded-lg">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg leading-tight tracking-wide">AgentShield AI</h1>
            <span className="text-xs text-teal-400 font-mono tracking-wider">GOVERNED EXECUTION</span>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon
            const active = location.pathname.startsWith(item.path)
            return (
              <Link
                key={item.name}
                to={item.path}
                className={`flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  active
                    ? 'bg-purple-600/20 text-purple-300 border border-purple-500/30'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                <Icon className={`w-4 h-4 ${active ? 'text-teal-400' : 'text-slate-400'}`} />
                <span>{item.name}</span>
              </Link>
            )
          })}
        </nav>

        {/* User Footer */}
        <div className="p-4 border-t border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-3 overflow-hidden">
            <div className="w-9 h-9 rounded-full bg-purple-700 flex items-center justify-center font-bold text-sm">
              {user?.name?.[0] || 'U'}
            </div>
            <div className="truncate">
              <p className="text-sm font-medium text-white truncate">{user?.name || 'User'}</p>
              <p className="text-xs text-teal-400 font-mono">{user?.role || 'EMPLOYEE'}</p>
            </div>
          </div>
          <button
            onClick={logout}
            className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded"
            title="Log out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-800">
            {navItems.find((n) => location.pathname.startsWith(n.path))?.name || 'Enterprise Governance'}
          </h2>
          <div className="flex items-center space-x-4">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
              ● Gateway: Active (Fail-Closed)
            </span>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
