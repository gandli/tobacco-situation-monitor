import axios from 'axios'
import type { DashboardKPI, DashboardSummary, IntelListResponse, Intel } from '@/types'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

export const dashboardApi = {
  getKPI: () => api.get<DashboardKPI>('/dashboard/kpi'),
  getSummary: () => api.get<DashboardSummary>('/dashboard/summary'),
}

export const intelsApi = {
  list: (params?: {
    status?: string
    risk_level?: string
    region?: string
    limit?: number
    offset?: number
  }) => api.get<IntelListResponse>('/intels', { params }),
  
  get: (id: number) => api.get<Intel>(`/intels/${id}`),
}

export default api