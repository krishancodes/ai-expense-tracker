import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1',
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const orig = err.config
    if (err.response?.status === 401 && !orig._retry) {
      orig._retry = true
      try {
        const { data } = await axios.post(
          `${import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'}/auth/refresh`,
          { refresh_token: localStorage.getItem('refresh_token') }
        )
        useAuthStore.getState().setAuth(data.user, data.access_token)
        orig.headers.Authorization = `Bearer ${data.access_token}`
        return api(orig)
      } catch {
        useAuthStore.getState().clearAuth()
      }
    }
    return Promise.reject(err)
  }
)

export default api
