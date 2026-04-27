import { Search, X } from 'lucide-react'

const PAYMENT_METHODS = ['All', 'Cash', 'UPI', 'Card', 'NetBanking']

export default function FilterBar({ filters = {}, categories = [], onFilterChange }) {
  const hasActiveFilter =
    filters.search || filters.category_id || filters.date_from ||
    filters.date_to || (filters.payment_method && filters.payment_method !== 'All')

  const handleChange = (key, value) => {
    onFilterChange({ ...filters, [key]: value })
  }

  const clearAll = () => {
    onFilterChange({
      search: '',
      category_id: '',
      date_from: '',
      date_to: '',
      payment_method: 'All',
    })
  }

  return (
    <div className="flex flex-wrap items-center gap-3 bg-white border border-slate-200 rounded-xl px-4 py-3">

      {/* Search */}
      <div className="relative flex-1 min-w-[180px]">
        <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          placeholder="Search description…"
          value={filters.search ?? ''}
          onChange={(e) => handleChange('search', e.target.value)}
          className="w-full pl-8 pr-3 py-1.5 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {/* Category */}
      <select
        value={filters.category_id ?? ''}
        onChange={(e) => handleChange('category_id', e.target.value)}
        className="text-sm border border-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-700"
      >
        <option value="">All Categories</option>
        {categories.map((c) => (
          <option key={c.id} value={c.id}>
            {c.icon} {c.name}
          </option>
        ))}
      </select>

      {/* Date from */}
      <input
        type="date"
        value={filters.date_from ?? ''}
        onChange={(e) => handleChange('date_from', e.target.value)}
        className="text-sm border border-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-700"
      />

      {/* Date to */}
      <input
        type="date"
        value={filters.date_to ?? ''}
        onChange={(e) => handleChange('date_to', e.target.value)}
        className="text-sm border border-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-700"
      />

      {/* Payment method */}
      <select
        value={filters.payment_method ?? 'All'}
        onChange={(e) => handleChange('payment_method', e.target.value)}
        className="text-sm border border-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-700"
      >
        {PAYMENT_METHODS.map((m) => (
          <option key={m} value={m}>{m}</option>
        ))}
      </select>

      {/* Clear */}
      {hasActiveFilter && (
        <button
          onClick={clearAll}
          className="flex items-center gap-1 text-sm text-slate-500 hover:text-red-500 transition-colors"
        >
          <X size={14} />
          Clear
        </button>
      )}
    </div>
  )
}
