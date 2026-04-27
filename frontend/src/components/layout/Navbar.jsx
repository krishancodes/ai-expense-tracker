import { useLocation } from 'react-router-dom'
import { Bell, Menu } from 'lucide-react'
import { useAuthStore } from '../../stores/authStore'
import { useUIStore } from '../../stores/uiStore'

const PAGE_TITLES = {
  '/':          'Dashboard',
  '/dashboard': 'Dashboard',
  '/expenses':  'Expenses',
  '/budgets':   'Budgets',
  '/insights':  'Insights',
  '/settings':  'Settings',
}

function getInitials(name = '') {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((n) => n[0].toUpperCase())
    .join('')
}

export default function Navbar() {
  const { pathname } = useLocation()
  const user = useAuthStore((s) => s.user)
  const toggleSidebar = useUIStore((s) => s.toggleSidebar)

  const title = PAGE_TITLES[pathname] ?? 'AI Expense Tracker'

  return (
    <header className="h-16 sticky top-0 bg-white border-b border-slate-200 z-10 flex items-center px-6 gap-4">

      {/* Mobile hamburger */}
      <button
        onClick={toggleSidebar}
        className="lg:hidden text-slate-500 hover:text-slate-700 transition-colors"
        aria-label="Toggle sidebar"
      >
        <Menu size={22} />
      </button>

      {/* Page title */}
      <h1 className="flex-1 text-lg font-semibold text-slate-800">{title}</h1>

      {/* Right actions */}
      <div className="flex items-center gap-3">
        <button
          className="text-slate-500 hover:text-slate-700 transition-colors"
          aria-label="Notifications"
        >
          <Bell size={20} />
        </button>

        {/* Avatar */}
        <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs font-bold">
          {getInitials(user?.full_name ?? user?.name ?? '')}
        </div>
      </div>
    </header>
  )
}
