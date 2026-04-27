import api from './client'

export const getInsights = (params) => api.get('/insights', { params })
export const regenerateInsights = (data) => api.post('/insights/regenerate', data)
