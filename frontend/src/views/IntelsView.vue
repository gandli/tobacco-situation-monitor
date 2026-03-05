<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDashboardStore } from '@/stores/dashboard'
import IntelTable from '@/components/IntelTable.vue'
import type { Intel } from '@/types'

const route = useRoute()
const router = useRouter()
const store = useDashboardStore()

// Filters
const filters = ref({
  status: route.query.status as string || '',
  risk_level: route.query.risk_level as string || '',
  region: route.query.region as string || ''
})

// Pagination
const currentPage = ref(1)
const pageSize = 20

// Load data
onMounted(() => {
  loadData()
})

function loadData() {
  const params: Record<string, unknown> = {
    limit: pageSize,
    offset: (currentPage.value - 1) * pageSize
  }
  
  if (filters.value.status) params.status = filters.value.status
  if (filters.value.risk_level) params.risk_level = filters.value.risk_level
  if (filters.value.region) params.region = filters.value.region
  
  store.fetchIntels(params)
  
  // Update URL
  router.replace({
    query: {
      ...route.query,
      page: currentPage.value.toString(),
      ...Object.fromEntries(
        Object.entries(filters.value).filter(([_, v]) => v)
      )
    }
  })
}

// Watch filters
watch(filters, () => {
  currentPage.value = 1
  loadData()
}, { deep: true })

// Watch page
watch(currentPage, loadData)

// Pagination
const totalPages = ref(1)
watch(() => store.intelsTotal, (total) => {
  totalPages.value = Math.ceil(total / pageSize)
})

// Reset filters
function resetFilters() {
  filters.value = { status: '', risk_level: '', region: '' }
  currentPage.value = 1
}

// Handle intel selection
function handleSelect(intel: Intel) {
  router.push(`/intels/${intel.id}`)
}
</script>

<template>
  <div class="space-y-6">
    <!-- Filters -->
    <div class="card bg-neutral/50 border border-neutral-content/10">
      <div class="card-body p-4">
        <div class="flex flex-wrap gap-4 items-end">
          <!-- Status Filter -->
          <div class="form-control">
            <label class="label">
              <span class="label-text text-neutral-content/60 text-xs">状态</span>
            </label>
            <select 
              v-model="filters.status" 
              class="select select-bordered select-sm bg-neutral border-neutral-content/20 text-neutral-content"
            >
              <option value="">全部</option>
              <option value="new">待处理</option>
              <option value="reviewing">复核中</option>
              <option value="confirmed">已确认</option>
              <option value="dismissed">已排除</option>
            </select>
          </div>
          
          <!-- Risk Level Filter -->
          <div class="form-control">
            <label class="label">
              <span class="label-text text-neutral-content/60 text-xs">风险等级</span>
            </label>
            <select 
              v-model="filters.risk_level" 
              class="select select-bordered select-sm bg-neutral border-neutral-content/20 text-neutral-content"
            >
              <option value="">全部</option>
              <option value="high">高</option>
              <option value="medium">中</option>
              <option value="low">低</option>
            </select>
          </div>
          
          <!-- Region Filter -->
          <div class="form-control">
            <label class="label">
              <span class="label-text text-neutral-content/60 text-xs">地区</span>
            </label>
            <input 
              v-model="filters.region" 
              type="text" 
              placeholder="输入地区名称"
              class="input input-bordered input-sm bg-neutral border-neutral-content/20 text-neutral-content w-40"
            />
          </div>
          
          <!-- Reset Button -->
          <button 
            @click="resetFilters"
            class="btn btn-ghost btn-sm text-neutral-content/60"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            重置
          </button>
          
          <!-- Results Count -->
          <div class="ml-auto text-sm text-neutral-content/50">
            共 {{ store.intelsTotal }} 条记录
          </div>
        </div>
      </div>
    </div>
    
    <!-- Intel Table -->
    <IntelTable 
      :intels="store.intels" 
      :loading="store.loading"
      @select="handleSelect"
    />
    
    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex justify-center">
      <div class="join">
        <button 
          class="join-item btn btn-sm" 
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          «
        </button>
        <button class="join-item btn btn-sm">
          第 {{ currentPage }} / {{ totalPages }} 页
        </button>
        <button 
          class="join-item btn btn-sm" 
          :disabled="currentPage >= totalPages"
          @click="currentPage++"
        >
          »
        </button>
      </div>
    </div>
  </div>
</template>