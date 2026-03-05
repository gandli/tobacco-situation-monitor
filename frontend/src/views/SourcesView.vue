<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Source {
  id: number
  name: string
  list_url: string
  last_crawled_at: string | null
  created_at: string
}

const sources = ref<Source[]>([])
const loading = ref(true)

onMounted(async () => {
  // Mock data for now
  setTimeout(() => {
    sources.value = [
      { id: 1, name: '烟草局官网', list_url: 'https://example.com/news', last_crawled_at: new Date().toISOString(), created_at: '2026-01-01' },
      { id: 2, name: '市场监督管理局', list_url: 'https://example2.gov.cn/list', last_crawled_at: new Date(Date.now() - 3600000).toISOString(), created_at: '2026-01-02' },
      { id: 3, name: '公安执法公告', list_url: 'https://example3.gov.cn/announce', last_crawled_at: null, created_at: '2026-01-03' },
    ]
    loading.value = false
  }, 500)
})

function formatDate(dateStr: string | null) {
  if (!dateStr) return '从未'
  return new Date(dateStr).toLocaleString('zh-CN')
}

function getCrawlStatus(source: Source) {
  if (!source.last_crawled_at) return { class: 'badge-ghost', text: '未运行' }
  const diff = Date.now() - new Date(source.last_crawled_at).getTime()
  if (diff < 3600000) return { class: 'badge-success', text: '运行中' }
  if (diff < 86400000) return { class: 'badge-warning', text: '待运行' }
  return { class: 'badge-error', text: '超时' }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold text-neutral-content">数据源管理</h2>
      <button class="btn btn-primary btn-sm">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        添加数据源
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-24">
      <span class="loading loading-spinner loading-lg text-primary"></span>
    </div>

    <!-- Sources List -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div 
        v-for="source in sources" 
        :key="source.id"
        class="card bg-neutral/50 border border-neutral-content/10 card-hover"
      >
        <div class="card-body p-4">
          <div class="flex items-start justify-between">
            <div>
              <h3 class="font-medium text-neutral-content">{{ source.name }}</h3>
              <p class="text-xs text-neutral-content/50 mt-1 truncate max-w-xs">{{ source.list_url }}</p>
            </div>
            <span class="badge badge-sm" :class="getCrawlStatus(source).class">
              {{ getCrawlStatus(source).text }}
            </span>
          </div>
          
          <div class="mt-4 pt-4 border-t border-neutral-content/10">
            <div class="flex justify-between text-xs">
              <span class="text-neutral-content/50">最后爬取</span>
              <span class="text-neutral-content/70">{{ formatDate(source.last_crawled_at) }}</span>
            </div>
          </div>
          
          <div class="card-actions justify-end mt-4">
            <button class="btn btn-ghost btn-xs">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              运行
            </button>
            <button class="btn btn-ghost btn-xs">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              配置
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="stats shadow bg-neutral/50 border border-neutral-content/10 w-full">
      <div class="stat">
        <div class="stat-title text-neutral-content/60">总数据源</div>
        <div class="stat-value text-primary">{{ sources.length }}</div>
      </div>
      <div class="stat">
        <div class="stat-title text-neutral-content/60">运行中</div>
        <div class="stat-value text-success">{{ sources.filter(s => getCrawlStatus(s).text === '运行中').length }}</div>
      </div>
      <div class="stat">
        <div class="stat-title text-neutral-content/60">待运行</div>
        <div class="stat-value text-warning">{{ sources.filter(s => getCrawlStatus(s).text === '待运行').length }}</div>
      </div>
    </div>
  </div>
</template>