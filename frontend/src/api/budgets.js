import api from './client'

export const getBudgets = (params) => api.get('/budgets', { params })
export const setBudget = (data) => api.post('/budgets', data)
export const deleteBudget = (id) => api.delete(`/budgets/${id}`)
