import { Wallet, Target, Tag, TrendingUp } from 'lucide-react'
import { useDashboard } from '../hooks/useDashboard'
import StatCard from '../components/dashboard/StatCard'
import MonthlyBarChart from '../components/dashboard/MonthlyBarChart'
import CategoryDonutChart from '../components/dashboard/CategoryDonutChart'
import { format, parseISO } from 'date-fns'

function formatCurrency(val) {
  if (val == null) return '₹0.00'
  return `₹${Number(val).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`
}

// ── Skeleton ──────────────────────────────────────────────────────────────────

function SkeletonCard() {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 animate-pulse space-y-3">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-slate-200" />
        <div className="h-4 w-28 bg-slate-200 rounded" />
      </div>
      <div className="h-8 w-32 bg-slate-200 rounded" />
      <div className="h-4 w-20 bg-slate-200 rounded" />
    </div>
  )
}

function SkeletonBlock({ className = '' }) {
  return (
    <div className={`bg-white rounded-xl border border-slate-200 animate-pulse ${className}`} />
  )
}

// ── Recent expenses table ─────────────────────────────────────────────────────

function RecentExpenses({ expenses = [] }) {
  if (!expenses.length) {
    return (
      <p className="text-slate-400 text-sm text-center py-8">No expenses yet this month.</p>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200">
            <th className="text-left py-3 px-4 text-slate-500 font-medium">Date</th>
            <th className="text-left py-3 px-4 text-slate-500 font-medium">Description</th>
            <th className="text-left py-3 px-4 text-slate-500 font-medium">Category</th>
            <th className="text-right py-3 px-4 text-slate-500 font-medium">Amount</th>
          </tr>
        </thead>
        <tbody>
          {expenses.map((exp, i) => (
            <tr key={exp.id ?? i} className="border-b border-slate-100 last:border-0 hover:bg-slate-50 transition-colors">
              <td className="py-3 px-4 text-slate-500 whitespace-nowrap">
                {exp.date ? format(parseISO(exp.date), 'dd MMM yyyy') : '—'}
              </td>
              <td className="py-3 px-4 text-slate-800 font-medium">{exp.description ?? '—'}</td>
              <td className="py-3 px-4">
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 text-xs font-medium">
                  {exp.category?.name ?? exp.category ?? '—'}
                </span>
              </td>
              <td className="py-3 px-4 text-right font-semibold text-slate-900 tabular-nums">
                {formatCurrency(exp.amount)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ── Dashboard page ────────────────────────────────────────────────────────────

export default function Dashboard() {
  const { data, isLoading, error } = useDashboard()

  // ── Error state ──
  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-red-500 text-sm">Failed to load dashboard data. Please try again.</p>
      </div>
    )
  }

  // ── Loading skeletons ──
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => <SkeletonCard key={i} />)}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-7 gap-6">
          <SkeletonBlock className="lg:col-span-4 h-72" />
          <SkeletonBlock className="lg:col-span-3 h-72" />
        </div>
        <SkeletonBlock className="h-64" />
      </div>
    )
  }

  // ── Derived values ──
  const totalSpent      = formatCurrency(data?.total_spent)
  const budgetRemaining = formatCurrency(data?.budget_remaining)
  const topCatName      = data?.top_categories?.[0]?.name ?? '—'
  const utilization     = data?.utilization_pct != null ? `${data.utilization_pct}%` : '—'

  const monthlyTrend      = data?.monthly_trend ?? []
  const categoryBreakdown = data?.category_breakdown ?? []
  const recentExpenses    = data?.recent_expenses ?? []

  const budgetTrend =
    (data?.budget_remaining ?? 0) >= 0 ? 'up' : 'down'

  return (
    <div className="space-y-6">

      {/* ── Row 1: Stat cards ─────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Spent"
          value={totalSpent}
          trend="neutral"
          icon={Wallet}
          iconBg="bg-indigo-100"
        />
        <StatCard
          title="Budget Left"
          value={budgetRemaining}
          trend={budgetTrend}
          icon={Target}
          iconBg="bg-emerald-100"
        />
        <StatCard
          title="Top Category"
          value={topCatName}
          trend="neutral"
          icon={Tag}
          iconBg="bg-amber-100"
        />
        <StatCard
          title="Utilization"
          value={utilization}
          trend={
            (data?.utilization_pct ?? 0) > 90 ? 'down' :
            (data?.utilization_pct ?? 0) > 50 ? 'neutral' : 'up'
          }
          icon={TrendingUp}
          iconBg="bg-purple-100"
        />
      </div>

      {/* ── Row 2: Charts ─────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-7 gap-6">

        {/* Bar chart */}
        <div className="lg:col-span-4 bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-slate-800 font-semibold mb-4">Monthly Spending</h2>
          <MonthlyBarChart data={monthlyTrend} />
        </div>

        {/* Donut chart */}
        <div className="lg:col-span-3 bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-slate-800 font-semibold mb-4">By Category</h2>
          <CategoryDonutChart data={categoryBreakdown} />
        </div>
      </div>

      {/* ── Row 3: Recent expenses ────────────────────────────────────── */}
      <div className="bg-white rounded-xl border border-slate-200">
        <div className="px-6 py-4 border-b border-slate-200">
          <h2 className="text-slate-800 font-semibold">Recent Expenses</h2>
        </div>
        <RecentExpenses expenses={recentExpenses.slice(0, 5)} />
      </div>

    </div>
  )
}
