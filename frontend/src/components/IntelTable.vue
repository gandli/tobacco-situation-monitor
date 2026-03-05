<script setup lang="ts">
import type { Intel } from '@/types'

interface Props {
  intels: Intel[]
  loading?: boolean
}

defineProps<Props>()
const emit = defineEmits<{
  (e: 'select', intel: Intel): void
}>()

// formatDate utility - can be used for future date display
// function formatDate(dateStr: string) {
//   return new Date(dateStr).toLocaleString('zh-CN', {
//     month: '2-digit',
//     day: '2-digit',
//     hour: '2-digit',
//     minute: '2-digit'
//   })
// }

function getRiskBadgeClass(level: string) {
  const classes = {
    high: 'badge-error',
    medium: 'badge-warning',
    low: 'badge-success'
  }
  return classes[level as keyof typeof classes] || 'badge-ghost'
}

function getStatusBadgeClass(status: string) {
  const classes = {
    new: 'badge-info',
    reviewing: 'badge-warning',
    confirmed: 'badge-success',
    dismissed: 'badge-ghost'
  }
  return classes[status as keyof typeof classes] || 'badge-ghost'
}

function getStatusText(status: string) {
  const texts = {
    new: '待处理',
    reviewing: '复核中',
    confirmed: '已确认',
    dismissed: '已排除'
  }
  return texts[status as keyof typeof texts] || status
}
</script>

<template>
  <div class="card bg-neutral/50 border border-neutral-content/10">
    <div class="card-body p-0">
      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-12">
        <span class="loading loading-spinner loading-lg text-primary"></span>
      </div>

      <!-- Empty State -->
      <div v-else-if="intels.length === 0" class="flex flex-col items-center justify-center py-12 text-neutral-content/50">
        <svg class="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p>暂无情报数据</p>
      </div>

      <!-- Intel List -->
      <div v-else class="overflow-x-auto">
        <table class="table table-sm">
          <thead>
            <tr class="border-b border-neutral-content/10">
              <th class="text-neutral-content/60 font-medium">ID</th>
              <th class="text-neutral-content/60 font-medium">案件类型</th>
              <th class="text-neutral-content/60 font-medium">地区</th>
              <th class="text-neutral-content/60 font-medium">风险等级</th>
              <th class="text-neutral-content/60 font-medium">状态</th>
              <th class="text-neutral-content/60 font-medium">风险分</th>
              <th class="text-neutral-content/60 font-medium">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="intel in intels" 
              :key="intel.id"
              class="hover:bg-neutral-content/5 cursor-pointer border-b border-neutral-content/5"
              @click="emit('select', intel)"
            >
              <td class="font-mono text-sm">#{{ intel.id }}</td>
              <td>
                <span v-if="intel.case_type" class="text-sm">{{ intel.case_type }}</span>
                <span v-else class="text-neutral-content/30">-</span>
              </td>
              <td>
                <span v-if="intel.region" class="text-sm">{{ intel.region }}</span>
                <span v-else class="text-neutral-content/30">-</span>
              </td>
              <td>
                <span class="badge badge-sm" :class="getRiskBadgeClass(intel.risk_level)">
                  {{ intel.risk_level === 'high' ? '高' : intel.risk_level === 'medium' ? '中' : '低' }}
                </span>
              </td>
              <td>
                <span class="badge badge-sm" :class="getStatusBadgeClass(intel.status)">
                  {{ getStatusText(intel.status) }}
                </span>
              </td>
              <td>
                <div class="flex items-center gap-2">
                  <div class="radial-progress text-xs" :style="`--value: ${intel.risk_score}; --size: 2rem; --thickness: 3px;`" :class="intel.risk_score >= 70 ? 'text-error' : intel.risk_score >= 40 ? 'text-warning' : 'text-success'">
                    {{ intel.risk_score }}
                  </div>
                </div>
              </td>
              <td>
                <button class="btn btn-ghost btn-xs" @click.stop="emit('select', intel)">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>