import { useEffect } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { X } from 'lucide-react'
import { useCreateExpense } from '../../hooks/useExpenses'

const PAYMENT_METHODS = ['Cash', 'UPI', 'Card', 'NetBanking']

const schema = z.object({
  amount: z
    .string()
    .min(1, 'Amount is required')
    .refine((v) => Number(v) > 0, 'Amount must be greater than 0'),
  category_id: z.string().min(1, 'Category is required'),
  date: z.string().min(1, 'Date is required'),
  description: z.string().max(200, 'Max 200 characters').optional(),
  payment_method: z.enum(['Cash', 'UPI', 'Card', 'NetBanking']),
})

function todayStr() {
  return new Date().toISOString().split('T')[0]
}

export default function AddExpenseModal({ isOpen, onClose, categories = [] }) {
  const { mutateAsync, isPending } = useCreateExpense()

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(schema),
    defaultValues: {
      amount: '',
      category_id: '',
      date: todayStr(),
      description: '',
      payment_method: 'UPI',
    },
  })

  // Reset form when modal opens
  useEffect(() => {
    if (isOpen) reset({ amount: '', category_id: '', date: todayStr(), description: '', payment_method: 'UPI' })
  }, [isOpen, reset])

  const onSubmit = async (data) => {
    await mutateAsync({
      ...data,
      amount: parseFloat(data.amount),
    })
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40"
        onClick={onClose}
      />

      {/* Modal card */}
      <div className="relative z-10 w-full max-w-md bg-white rounded-xl shadow-xl p-6">

        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold text-slate-900">Add Expense</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition-colors">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">

          {/* Amount */}
          <div>
            <label className="block text-slate-700 text-sm font-medium mb-1">Amount (₹)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              {...register('amount')}
              placeholder="0.00"
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            {errors.amount && <p className="text-red-500 text-xs mt-1">{errors.amount.message}</p>}
          </div>

          {/* Category */}
          <div>
            <label className="block text-slate-700 text-sm font-medium mb-1">Category</label>
            <select
              {...register('category_id')}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-700"
            >
              <option value="">Select category…</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.icon} {c.name}
                </option>
              ))}
            </select>
            {errors.category_id && <p className="text-red-500 text-xs mt-1">{errors.category_id.message}</p>}
          </div>

          {/* Date */}
          <div>
            <label className="block text-slate-700 text-sm font-medium mb-1">Date</label>
            <input
              type="date"
              max={todayStr()}
              {...register('date')}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            {errors.date && <p className="text-red-500 text-xs mt-1">{errors.date.message}</p>}
          </div>

          {/* Description */}
          <div>
            <label className="block text-slate-700 text-sm font-medium mb-1">
              Description <span className="text-slate-400 font-normal">(optional)</span>
            </label>
            <input
              type="text"
              {...register('description')}
              placeholder="e.g. Lunch at café"
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            {errors.description && <p className="text-red-500 text-xs mt-1">{errors.description.message}</p>}
          </div>

          {/* Payment method — segmented control */}
          <div>
            <label className="block text-slate-700 text-sm font-medium mb-2">Payment Method</label>
            <Controller
              name="payment_method"
              control={control}
              render={({ field }) => (
                <div className="flex gap-2 flex-wrap">
                  {PAYMENT_METHODS.map((m) => (
                    <button
                      key={m}
                      type="button"
                      onClick={() => field.onChange(m)}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors ${
                        field.value === m
                          ? 'bg-indigo-600 text-white border-indigo-600'
                          : 'bg-white text-slate-600 border-slate-300 hover:border-indigo-400'
                      }`}
                    >
                      {m}
                    </button>
                  ))}
                </div>
              )}
            />
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2 rounded-lg border border-slate-300 text-sm text-slate-700 hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isPending}
              className="flex-1 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {isPending ? 'Saving…' : 'Save Expense'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
