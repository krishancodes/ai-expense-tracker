import { useQuery } from '@tanstack/react-query'
import { getDashboardSummary } from '../api/dashboard'

export function useDashboard(month, year) {
  const now = new Date()
  const m = month ?? now.getMonth() + 1
  const y = year ?? now.getFullYear()

  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard', m, y],
    queryFn: () => getDashboardSummary({ month: m, year: y }).then((r) => r.data),
    staleTime: 60000,
  })

  return { data, isLoading, error }
}
