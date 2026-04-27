import api from './client'

export const getMe = () => api.get('/users/me')
export const updateMe = (data) => api.put('/users/me', data)
export const deleteMe = () => api.delete('/users/me')
