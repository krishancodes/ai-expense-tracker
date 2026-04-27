import api from './client'

export const getDashboardSummary = (params) => api.get('/dashboard/summary', { params })
