import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('admin_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth APIs
export const authAPI = {
  login: (telegram_id, password) =>
    api.post('/admin/auth/login', { telegram_id, password }),
}

// Dashboard APIs
export const dashboardAPI = {
  getStats: () => api.get('/admin/dashboard/stats'),
  getUsers: (params) => api.get('/admin/dashboard/users', { params }),
  getOrders: (params) => api.get('/admin/dashboard/orders', { params }),
  getReferrers: (params) => api.get('/admin/dashboard/referrers', { params }),
  getPaymentMonitoring: (days = 7) => api.get(`/admin/dashboard/payment-monitoring?days=${days}`),
  getKPI: (days = 30) => api.get(`/admin/dashboard/kpi?days=${days}`),
  getAuditLogs: (params) => api.get('/admin/dashboard/audit-logs', { params }),
}

// Withdrawal APIs
export const withdrawalAPI = {
  getAll: (status) => api.get('/withdrawals/admin/all', { params: { status } }),
  getStatistics: () => api.get('/withdrawals/admin/statistics'),
  approve: (withdrawal_id, data) => api.post(`/withdrawals/${withdrawal_id}/approve`, data),
  reject: (withdrawal_id, data) => api.post(`/withdrawals/${withdrawal_id}/reject`, data),
  markPaid: (withdrawal_id, data) => api.post(`/withdrawals/${withdrawal_id}/paid`, data),
}

// Fraud Detection APIs
export const fraudAPI = {
  getFlags: (params) => api.get('/fraud/flags', { params }),
  getUserFlags: (user_id) => api.get(`/fraud/user/${user_id}/flags`),
  createFlag: (data) => api.post('/fraud/flags/create', data),
  resolveFlag: (flag_id, notes) => api.post(`/fraud/flags/${flag_id}/resolve`, { resolution_notes: notes }),
  blockUser: (user_id, reason) => api.post(`/fraud/user/${user_id}/block`, { reason }),
  unblockUser: (user_id) => api.post(`/fraud/user/${user_id}/unblock`),
  runChecks: (user_id, upi_id) => api.post(`/fraud/user/${user_id}/run-checks`, { upi_id }),
}

// Settings APIs
export const settingsAPI = {
  getAll: () => api.get('/settings/all'),
  update: (key, value) => api.put(`/settings/${key}`, { setting_value: value }),
}

export default api
