import { Pencil, Trash2, ChevronLeft, ChevronRight } from 'lucide-react'
import { format, parseISO } from 'date-fns'
import { useState } from 'react'

const PAGE_SIZE = 10

function formatCurrency(val) {
  return `₹${Number(val).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`
}

function CategoryBadge({ category }) {
  if (!category) return <span className="text-slate-400 text-xs">—</span>
  return (
    <span
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
      style={{
        backgroundColor: category.color ? `${category.color}20` : '#e0e7ff',
        color: category.color ?? '#6366F1',
      }}
    >
      {category.icon && <span>{category.icon}</span>}
      {category.name}
    </span>
  )
}

function PaymentBadge({ method }) {
  if (!method) return null
  return (
    <span className="inline-flex px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-xs font-medium">
      {method}
    </span>
  )
}

export default function ExpenseTable({ expenses, onEdit, onDelete, isLoading }) {
  const [page, setPage] = useState(0)

  // expenses is the full API response: { data: [], total, page, limit }
  const rows = expenses?.data ?? []
  const total = expenses?.total ?? rows.length
  const totalPages = Math.ceil(total / PAGE_SIZE)
  const pageData = rows.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

  if (isLoading) {
    return (
      <div className="space-y-2 p-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-12 bg-slate-100 rounded-lg animate-pulse" />
        ))}
      </div>
    )
  }

  if (!rows.length) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-slate-400 gap-3">
        <p className="text-sm">No expenses yet</p>
      </div>
    )
  }

  return (
    <div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200">
              <th className="text-left py-3 px-4 text-slate-500 font-medium">Date</th>
              <th className="text-left py-3 px-4 text-slate-500 font-medium">Description</th>
              <th className="text-left py-3 px-4 text-slate-500 font-medium">Category</th>
              <th className="text-left py-3 px-4 text-slate-500 font-medium">Payment</th>
              <th className="text-right py-3 px-4 text-slate-500 font-medium">Amount</th>
              <th className="py-3 px-4" />
            </tr>
          </thead>
          <tbody>
            {pageData.map((exp) => (
              <tr
                key={exp.id}
                className="border-b border-slate-100 last:border-0 hover:bg-slate-50 transition-colors"
              >
                <td className="py-3 px-4 text-slate-500 whitespace-nowrap">
                  {exp.date ? format(parseISO(exp.date), 'MMM d') : '—'}
                </td>
                <td className="py-3 px-4 text-slate-800 max-w-[200px]">
                  <span title={exp.description} className="block truncate">
                    {exp.description || <span className="text-slate-400 italic">No description</span>}
                  </span>
                </td>
                <td className="py-3 px-4">
                  <CategoryBadge category={exp.category} />
                </td>
                <td className="py-3 px-4">
                  <PaymentBadge method={exp.payment_method} />
                </td>
                <td className="py-3 px-4 text-right font-medium text-slate-900 tabular-nums whitespace-nowrap">
                  {formatCurrency(exp.amount)}
                </td>
                <td className="py-3 px-4">
                  <div className="flex items-center justify-end gap-2">
                    <button
                      onClick={() => onEdit?.(exp)}
                      className="text-slate-400 hover:text-indigo-600 transition-colors"
                      title="Edit"
                    >
                      <Pencil size={15} />
                    </button>
                    <button
                      onClick={() => onDelete?.(exp)}
                      className="text-slate-400 hover:text-red-500 transition-colors"
                      title="Delete"
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-slate-200">
          <span className="text-xs text-slate-500">
            Page {page + 1} of {totalPages}
          </span>
          <div className="flex gap-1">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="p-1.5 rounded-lg text-slate-500 hover:bg-slate-100 disabled:opacity-40 transition-colors"
            >
              <ChevronLeft size={16} />
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page === totalPages - 1}
              className="p-1.5 rounded-lg text-slate-500 hover:bg-slate-100 disabled:opacity-40 transition-colors"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
