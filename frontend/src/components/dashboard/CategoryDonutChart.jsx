import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'

function formatCurrency(val) {
  return `₹${Number(val).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`
}

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const { name, value } = payload[0]
  return (
    <div className="bg-white border border-slate-200 rounded-lg px-3 py-2 shadow-sm text-sm">
      <p className="text-slate-500 mb-1">{name}</p>
      <p className="font-semibold text-slate-900">{formatCurrency(value)}</p>
    </div>
  )
}

export default function CategoryDonutChart({ data = [] }) {
  if (!data.length) {
    return (
      <div className="h-60 flex items-center justify-center text-slate-400 text-sm">
        No category data yet
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      <ResponsiveContainer width="100%" height={240}>
        <PieChart>
          <Pie
            data={data}
            dataKey="spent"
            nameKey="name"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={2}
          >
            {data.map((entry, i) => (
              <Cell key={`cell-${i}`} fill={entry.color ?? '#6366F1'} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>

      {/* Legend */}
      <ul className="space-y-2">
        {data.map((cat, i) => (
          <li key={i} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <span
                className="w-3 h-3 rounded-full shrink-0"
                style={{ backgroundColor: cat.color ?? '#6366F1' }}
              />
              <span className="text-slate-600 truncate max-w-[140px]">{cat.name}</span>
            </div>
            <span className="text-slate-800 font-medium tabular-nums">
              {formatCurrency(cat.spent)}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
