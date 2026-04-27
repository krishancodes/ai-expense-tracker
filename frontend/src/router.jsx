import { createBrowserRouter, redirect } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import AppShell from './components/layout/AppShell'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Expenses from './pages/Expenses'
import Budgets from './pages/Budgets'
import Insights from './pages/Insights'
import Settings from './pages/Settings'
import NotFound from './pages/NotFound'

const protectedLoader = () => {
  const token = useAuthStore.getState().accessToken
  if (!token) return redirect('/login')
  return null
}

const router = createBrowserRouter([
  { path: '/login', element: <Login /> },
  { path: '/register', element: <Register /> },
  {
    path: '/',
    element: <AppShell />,
    loader: protectedLoader,
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'dashboard', element: <Dashboard /> },
      { path: 'expenses', element: <Expenses /> },
      { path: 'budgets', element: <Budgets /> },
      { path: 'insights', element: <Insights /> },
      { path: 'settings', element: <Settings /> },
    ],
  },
  { path: '*', element: <NotFound /> },
])

export default router
