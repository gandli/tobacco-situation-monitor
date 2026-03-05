import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { dashboardApi, intelsApi } from '@/api'
import type { DashboardKPI, DashboardSummary, Intel } from '@/types'

export const useDashboardStore = defineStore('dashboard', () => {
  // State
  const kpi = ref<DashboardKPI | null>(null)
  const summary = ref<DashboardSummary | null>(null)
  const intels = ref<Intel[]>([])
  const intelsTotal = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const riskLevelCounts = computed(() => {
    const counts = { high: 0, medium: 0, low: 0 }
    intels.value.forEach(intel => {
      if (intel.risk_level in counts) {
        counts[intel.risk_level as keyof typeof counts]++
      }
    })
    return counts
  })

  const statusCounts = computed(() => {
    const counts: Record<string, number> = {}
    intels.value.forEach(intel => {
      counts[intel.status] = (counts[intel.status] || 0) + 1
    })
    return counts
  })

  // Actions
  async function fetchKPI() {
    try {
      const { data } = await dashboardApi.getKPI()
      kpi.value = data
    } catch (e) {
      console.error('Failed to fetch KPI:', e)
      error.value = '获取KPI数据失败'
    }
  }

  async function fetchSummary() {
    try {
      const { data } = await dashboardApi.getSummary()
      summary.value = data
    } catch (e) {
      console.error('Failed to fetch summary:', e)
      error.value = '获取摘要数据失败'
    }
  }

  async function fetchIntels(params?: {
    status?: string
    risk_level?: string
    region?: string
    limit?: number
    offset?: number
  }) {
    loading.value = true
    error.value = null
    try {
      const { data } = await intelsApi.list(params)
      intels.value = data.items
      intelsTotal.value = data.total
    } catch (e) {
      console.error('Failed to fetch intels:', e)
      error.value = '获取情报数据失败'
    } finally {
      loading.value = false
    }
  }

  async function refreshAll() {
    loading.value = true
    error.value = null
    try {
      await Promise.all([
        fetchKPI(),
        fetchSummary(),
        fetchIntels({ limit: 50 })
      ])
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    kpi,
    summary,
    intels,
    intelsTotal,
    loading,
    error,
    // Getters
    riskLevelCounts,
    statusCounts,
    // Actions
    fetchKPI,
    fetchSummary,
    fetchIntels,
    refreshAll,
  }
})