<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title: string
  value: string | number
  subtitle?: string
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
  icon: 'coverage' | 'timeliness' | 'accuracy' | 'noise' | 'reviewable'
  color?: 'primary' | 'secondary' | 'accent' | 'success' | 'warning' | 'error'
}

const props = withDefaults(defineProps<Props>(), {
  color: 'primary'
})

const iconPath = computed(() => {
  const icons = {
    coverage: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
    timeliness: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
    accuracy: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
    noise: 'M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636',
    reviewable: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4'
  }
  return icons[props.icon]
})

const colorClass = computed(() => {
  const colors = {
    primary: 'text-primary',
    secondary: 'text-secondary',
    accent: 'text-accent',
    success: 'text-success',
    warning: 'text-warning',
    error: 'text-error'
  }
  return colors[props.color]
})

const bgClass = computed(() => {
  const colors = {
    primary: 'bg-primary/10',
    secondary: 'bg-secondary/10',
    accent: 'bg-accent/10',
    success: 'bg-success/10',
    warning: 'bg-warning/10',
    error: 'bg-error/10'
  }
  return colors[props.color]
})
</script>

<template>
  <div class="card bg-neutral/50 border border-neutral-content/10 card-hover">
    <div class="card-body p-4 md:p-6">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <h3 class="text-sm text-neutral-content/60 mb-1">{{ title }}</h3>
          <div class="flex items-baseline gap-2">
            <span class="text-2xl md:text-3xl font-bold" :class="colorClass">{{ value }}</span>
            <span v-if="subtitle" class="text-sm text-neutral-content/50">{{ subtitle }}</span>
          </div>
          <div v-if="trend" class="flex items-center gap-1 mt-2">
            <svg v-if="trend === 'up'" class="w-4 h-4 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
            </svg>
            <svg v-else-if="trend === 'down'" class="w-4 h-4 text-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
            <span v-if="trendValue" class="text-xs" :class="trend === 'up' ? 'text-success' : trend === 'down' ? 'text-error' : 'text-neutral-content/50'">
              {{ trendValue }}
            </span>
          </div>
        </div>
        <div class="p-3 rounded-xl" :class="bgClass">
          <svg class="w-6 h-6" :class="colorClass" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="iconPath" />
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>