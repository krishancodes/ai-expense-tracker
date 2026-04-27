import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Receipt,
  PiggyBank,
  Sparkles,
  Settings,
} from 'lucide-react'
import { useAuthStore } from '../../stores/authStore'

const NAV_ITEMS = [
  { label: 'Dashboard', icon: LayoutDashboard, path: '/dashboard' },
  { label: 'Expenses',  icon: Receipt,         path: '/expenses'  },
  { label: 'Budgets',   icon: PiggyBank,        path: '/budgets'   },
  { label: 'Insights',  icon: Sparkles,         path: '/insights'  },
  { label: 'Settings',  icon: Settings,         path: '/settings'  },
]

function getInitials(name = '') {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((n) => n[0].toUpperCase())
    .join('')
}

export default function Sidebar() {
  const { pathname } = useLocation()
  const user = useAuthStore((s) => s.user)

  return (
    <aside className="fixed inset-y-0 left-0 w-64 bg-slate-900 flex flex-col hidden lg:flex">

      {/* Logo */}
      <div className="px-6 py-5 border-b border-slate-700/50 flex items-center gap-2">
        <span className="text-2xl">💰</span>
        <span className="text-white font-bold text-lg">SpendAI</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map(({ label, icon: Icon, path }) => {
          const isActive = pathname === path || (path === '/dashboard' && pathname === '/')
          return (
            <NavLink
              key={path}
              to={path}
              className={
                isActive
                  ? 'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium bg-indigo-600 text-white'
                  : 'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-slate-400 hover:bg-slate-800 hover:text-white transition-colors'
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          )
        })}
      </nav>

      {/* User profile */}
      <div className="px-4 py-4 border-t border-slate-700/50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs font-bold shrink-0">
            {getInitials(user?.full_name ?? user?.name ?? '')}
          </div>
          <div className="min-w-0">
            <p className="text-white text-sm font-medium truncate">
              {user?.full_name ?? user?.name ?? 'User'}
            </p>
            <p className="text-slate-400 text-xs truncate">{user?.email ?? ''}</p>
          </div>
        </div>
      </div>
    </aside>
  )
}
