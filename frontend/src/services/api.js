import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach JWT token from localStorage if present
apiClient.interceptors.request.use((config) => {
  const userJson = localStorage.getItem('agentshield_user')
  if (userJson) {
    try {
      const user = JSON.parse(userJson)
      if (user.token) {
        config.headers.Authorization = `Bearer ${user.token}`
      }
      if (user.role) {
        config.headers['X-Role'] = user.role
      }
      if (user.id) {
        config.headers['X-User-Id'] = user.id
      }
    } catch {
      // Ignore parse error
    }
  }
  return config
})

export const apiService = {
  // Auth
  login: (email, password) => apiClient.post('/auth/login', { email, password }),
  register: (data) => apiClient.post('/auth/register', data),
  getMe: () => apiClient.get('/auth/me'),

  // Tasks (Multi-Agent Workflow)
  runTask: (data) => apiClient.post('/tasks/run', data),
  getTask: (taskId) => apiClient.get(`/tasks/${taskId}`),
  resumeTask: (taskId, verdictData) => apiClient.post(`/tasks/${taskId}/resume`, verdictData),

  // Approvals (Human-in-the-Loop)
  getPendingApprovals: () => apiClient.get('/approvals/pending'),
  getApprovalDetail: (approvalId) => apiClient.get(`/approvals/${approvalId}`),
  decideApproval: (approvalId, decisionData) => apiClient.post(`/approvals/${approvalId}/decide`, decisionData),

  // System Health
  getHealth: () => axios.get('http://localhost:8000/health'),
}

export default apiService
