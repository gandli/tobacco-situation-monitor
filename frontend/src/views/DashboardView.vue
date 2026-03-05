<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import KPICard from '@/components/KPICard.vue'
import RegionChart from '@/components/RegionChart.vue'
import RiskChart from '@/components/RiskChart.vue'
import IntelTable from '@/components/IntelTable.vue'
import type { Intel } from '@/types'

const store = useDashboardStore()

onMounted(() => {
  store.refreshAll()
})

// Computed values for charts
const riskData = computed(() => {
  const counts = store.riskLevelCounts
  return {
    high: counts.high,
    medium: counts.medium,
    low: counts.low
  }
})

function handleIntelSelect(intel: Intel) {
  // Navigate to intel detail
  console.log('Selected intel:', intel)
  // router.push(`/intels/${intel.id}`)
}
</script>

<template>
  <div class="space-y-6">
    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
      <KPICard
        title="覆盖率"
        :value="store.kpi?.coverage_rate?.percentage ?? '-'"
        subtitle="%"
        :description="store.kpi?.coverage_rate?.description"
        icon="coverage"
        color="primary"
      />
      <KPICard
        title="时效性"
        :value="store.kpi?.timeliness_score?.avg_hours ?? '-'"
        subtitle="小时"
        :description="store.kpi?.timeliness_score?.description"
        icon="timeliness"
        color="secondary"
      />
      <KPICard
        title="识别准确率"
        :value="store.kpi?.accuracy_rate?.percentage ?? '-'"
        subtitle="%"
        :description="store.kpi?.accuracy_rate?.description"
        icon="accuracy"
        color="success"
      />
      <KPICard
        title="噪音率"
        :value="store.kpi?.noise_rate?.percentage ?? '-'"
        subtitle="%"
        :description="store.kpi?.noise_rate?.description"
        icon="noise"
        color="warning"
      />
      <KPICard
        title="可复核率"
        :value="store.kpi?.reviewable_rate?.percentage ?? '-'"
        subtitle="%"
        :description="store.kpi?.reviewable_rate?.description"
        icon="reviewable"
        color="accent"
      />
    </div>

    <!-- Summary Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="stats shadow bg-neutral/50 border border-neutral-content/10">
        <div class="stat">
          <div class="stat-figure text-primary">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="stat-title text-neutral-content/60">今日新增</div>
          <div class="stat-value text-primary">{{ store.summary?.today_new ?? 0 }}</div>
          <div class="stat-desc text-neutral-content/50">条情报</div>
        </div>
      </div>
      
      <div class="stats shadow bg-neutral/50 border border-neutral-content/10">
        <div class="stat">
          <div class="stat-figure text-error">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div class="stat-title text-neutral-content/60">高风险情报</div>
          <div class="stat-value text-error">{{ store.summary?.high_risk ?? 0 }}</div>
          <div class="stat-desc text-neutral-content/50">待处理</div>
        </div>
      </div>
      
      <div class="stats shadow bg-neutral/50 border border-neutral-content/10">
        <div class="stat">
          <div class="stat-figure text-secondary">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <div class="stat-title text-neutral-content/60">情报总数</div>
          <div class="stat-value text-secondary">{{ store.intelsTotal }}</div>
          <div class="stat-desc text-neutral-content/50">已采集</div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <RegionChart 
        :data="store.summary?.by_region ?? []" 
        :loading="store.loading" 
      />
      <RiskChart
        :high="riskData.high"
        :medium="riskData.medium"
        :low="riskData.low"
        :loading="store.loading"
      />
    </div>

    <!-- Recent Intels -->
    <div>
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-neutral-content">最新情报</h2>
        <router-link to="/intels" class="btn btn-ghost btn-sm text-primary">
          查看全部
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </router-link>
      </div>
      <IntelTable 
        :intels="store.intels.slice(0, 10)" 
        :loading="store.loading"
        @select="handleIntelSelect"
      />
    </div>
  </div>
</template>