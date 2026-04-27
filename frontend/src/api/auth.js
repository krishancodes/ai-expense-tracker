import api from './client'

export const register = (data) => api.post('/auth/register', data)
export const login = (data) => api.post('/auth/login', data)
export const logout = (data) => api.post('/auth/logout', data)
export const refreshToken = (data) => api.post('/auth/refresh', data)
