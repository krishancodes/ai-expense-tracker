import { TrendingUp, TrendingDown } from 'lucide-react'

export default function StatCard({ title, value, change, trend, icon: Icon, iconBg }) {
  const trendColor =
    trend === 'up' ? 'text-emerald-600' :
    trend === 'down' ? 'text-red-500' :
    'text-slate-400'

  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : null

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col gap-4">

      {/* Icon + title row */}
      <div className="flex items-center gap-3">
        <div className={`${iconBg} w-10 h-10 rounded-full flex items-center justify-center shrink-0`}>
          {Icon && <Icon size={20} className="text-slate-700" />}
        </div>
        <span className="text-slate-500 text-sm font-medium">{title}</span>
      </div>

      {/* Value */}
      <p className="text-3xl font-bold text-slate-900 tabular-nums">{value}</p>

      {/* Change badge */}
      {change !== undefined && change !== null && (
        <div className={`flex items-center gap-1 text-sm font-medium ${trendColor}`}>
          {TrendIcon && <TrendIcon size={14} />}
          <span>{change}</span>
        </div>
      )}
    </div>
  )
}
