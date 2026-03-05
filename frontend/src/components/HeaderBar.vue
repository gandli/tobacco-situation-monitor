<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const currentTime = ref(new Date())
const pageTitle = computed(() => route.meta?.title || '态势监测')

setInterval(() => {
  currentTime.value = new Date()
}, 1000)

const formattedTime = computed(() => {
  return currentTime.value.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
})

const statusText = computed(() => {
  const hour = currentTime.value.getHours()
  if (hour >= 6 && hour < 12) return '☀️ 上午'
  if (hour >= 12 && hour < 14) return '🌤️ 中午'
  if (hour >= 14 && hour < 18) return '⛅ 下午'
  if (hour >= 18 && hour < 22) return '🌙 傍晚'
  return '🌃 夜间'
})
</script>

<template>
  <header class="h-16 bg-neutral/50 border-b border-neutral-content/10 flex items-center justify-between px-4 md:px-6">
    <!-- Left: Title -->
    <div class="flex items-center gap-4">
      <h1 class="text-lg md:text-xl font-semibold text-neutral-content">
        {{ pageTitle }}
      </h1>
      <div class="badge badge-primary badge-sm hidden md:flex">
        实时监控
      </div>
    </div>

    <!-- Right: Status & Time -->
    <div class="flex items-center gap-4 md:gap-6">
      <!-- System Status -->
      <div class="flex items-center gap-2">
        <span class="w-2 h-2 bg-success rounded-full animate-pulse"></span>
        <span class="text-sm text-neutral-content/70 hidden md:inline">系统正常</span>
      </div>

      <!-- Time -->
      <div class="text-sm text-neutral-content/80 font-mono">
        <span class="hidden md:inline">{{ statusText }} · </span>
        <span>{{ formattedTime }}</span>
      </div>

      <!-- Refresh Button -->
      <button class="btn btn-ghost btn-sm btn-circle" title="刷新数据">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </button>
    </div>
  </header>
</template>