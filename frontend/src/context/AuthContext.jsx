import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('agentshield_user')
    return saved ? JSON.parse(saved) : {
      id: 'demo-user-1',
      name: 'Priya Sharma',
      email: 'priya@example.com',
      role: 'MANAGER' // Default to MANAGER for demo exploration
    }
  })
  const [loading, setLoading] = useState(false)

  const login = (userData) => {
    setUser(userData)
    localStorage.setItem('agentshield_user', JSON.stringify(userData))
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('agentshield_user')
  }

  return (
    <AuthContext.Provider value={{ user, setUser, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
