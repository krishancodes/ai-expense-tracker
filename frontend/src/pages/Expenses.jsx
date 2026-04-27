import { useState } from 'react'
import { Plus } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { useExpenses, useDeleteExpense } from '../hooks/useExpenses'
import FilterBar from '../components/expenses/FilterBar'
import ExpenseTable from '../components/expenses/ExpenseTable'
import AddExpenseModal from '../components/expenses/AddExpenseModal'
import api from '../api/client'

function useCategories() {
  return useQuery({
    queryKey: ['categories'],
    queryFn: () => api.get('/categories').then((r) => r.data),
    staleTime: 300000,
  })
}

export default function Expenses() {
  const [modalOpen, setModalOpen] = useState(false)
  const [filters, setFilters] = useState({
    search: '',
    category_id: '',
    date_from: '',
    date_to: '',
    payment_method: 'All',
  })

  // Build query params — strip empty values + 'All' payment method
  const queryParams = Object.fromEntries(
    Object.entries(filters).filter(([k, v]) => v && v !== 'All')
  )

  const { data: expensesData, isLoading } = useExpenses(queryParams)
  const { data: categories = [] } = useCategories()
  const deleteExpense = useDeleteExpense()

  const handleDelete = (exp) => {
    if (window.confirm(`Delete "${exp.description || 'this expense'}"? This cannot be undone.`)) {
      deleteExpense.mutate(exp.id)
    }
  }

  return (
    <div className="space-y-5">

      {/* Page header */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-900">Expenses</h1>
        <button
          onClick={() => setModalOpen(true)}
          className="flex items-center gap-2 bg-indigo-600 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
        >
          <Plus size={16} />
          Add Expense
        </button>
      </div>

      {/* Filters */}
      <FilterBar
        filters={filters}
        categories={categories}
        onFilterChange={setFilters}
      />

      {/* Table — pass full response object; ExpenseTable extracts .data internally */}
      <div className="bg-white rounded-xl border border-slate-200">
        <ExpenseTable
          expenses={expensesData}
          isLoading={isLoading}
          onDelete={handleDelete}
        />
      </div>

      {/* Add modal */}
      <AddExpenseModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        categories={categories}
      />
    </div>
  )
}
