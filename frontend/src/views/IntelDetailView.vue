<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { intelsApi } from '@/api'
import type { Intel } from '@/types'

const route = useRoute()
const router = useRouter()

const intel = ref<Intel | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

const intelId = computed(() => Number(route.params.id))

onMounted(async () => {
  await loadIntel()
})

async function loadIntel() {
  loading.value = true
  error.value = null
  try {
    const { data } = await intelsApi.get(intelId.value)
    intel.value = data
  } catch (e) {
    error.value = '加载情报详情失败'
    console.error(e)
  } finally {
    loading.value = false
  }
}

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

function goBack() {
  router.push('/intels')
}
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <!-- Back Button -->
    <button @click="goBack" class="btn btn-ghost btn-sm mb-4 text-neutral-content/60">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      返回列表
    </button>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-24">
      <span class="loading loading-spinner loading-lg text-primary"></span>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="alert alert-error">
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
      <span>{{ error }}</span>
    </div>

    <!-- Intel Detail -->
    <div v-else-if="intel" class="space-y-6">
      <!-- Header Card -->
      <div class="card bg-neutral/50 border border-neutral-content/10">
        <div class="card-body">
          <div class="flex items-start justify-between">
            <div>
              <div class="flex items-center gap-2 mb-2">
                <span class="text-sm text-neutral-content/50 font-mono">#{{ intel.id }}</span>
                <span class="badge" :class="getStatusBadgeClass(intel.status)">
                  {{ getStatusText(intel.status) }}
                </span>
                <span class="badge" :class="getRiskBadgeClass(intel.risk_level)">
                  {{ intel.risk_level === 'high' ? '高风险' : intel.risk_level === 'medium' ? '中风险' : '低风险' }}
                </span>
              </div>
              <h1 class="text-xl font-semibold text-neutral-content">
                {{ intel.case_type || '未分类案件' }}
              </h1>
            </div>
            
            <!-- Actions -->
            <div class="flex gap-2">
              <button class="btn btn-success btn-sm">确认</button>
              <button class="btn btn-error btn-sm btn-outline">排除</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Info Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Basic Info -->
        <div class="card bg-neutral/50 border border-neutral-content/10">
          <div class="card-body p-4">
            <h3 class="text-sm font-medium text-neutral-content/60 mb-3">基本信息</h3>
            <div class="space-y-3">
              <div class="flex justify-between">
                <span class="text-neutral-content/50">案件类型</span>
                <span class="text-neutral-content">{{ intel.case_type || '-' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-neutral-content/50">地区</span>
                <span class="text-neutral-content">{{ intel.region || '-' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-neutral-content/50">来源文章ID</span>
                <span class="text-neutral-content font-mono">#{{ intel.article_id }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-neutral-content/50">是否案件相关</span>
                <span :class="intel.is_case_related ? 'text-success' : 'text-neutral-content/50'">
                  {{ intel.is_case_related ? '是' : '否' }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Risk Assessment -->
        <div class="card bg-neutral/50 border border-neutral-content/10">
          <div class="card-body p-4">
            <h3 class="text-sm font-medium text-neutral-content/60 mb-3">风险评估</h3>
            <div class="space-y-3">
              <div class="flex justify-between items-center">
                <span class="text-neutral-content/50">风险分数</span>
                <div class="flex items-center gap-2">
                  <div 
                    class="radial-progress text-sm" 
                    :style="`--value: ${intel.risk_score}; --size: 2.5rem; --thickness: 4px;`"
                    :class="intel.risk_score >= 70 ? 'text-error' : intel.risk_score >= 40 ? 'text-warning' : 'text-success'"
                  >
                    {{ intel.risk_score }}
                  </div>
                </div>
              </div>
              <div class="flex justify-between">
                <span class="text-neutral-content/50">风险等级</span>
                <span :class="{
                  'text-error': intel.risk_level === 'high',
                  'text-warning': intel.risk_level === 'medium',
                  'text-success': intel.risk_level === 'low'
                }">
                  {{ intel.risk_level === 'high' ? '高' : intel.risk_level === 'medium' ? '中' : '低' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Keywords -->
      <div v-if="intel.keywords_matched" class="card bg-neutral/50 border border-neutral-content/10">
        <div class="card-body p-4">
          <h3 class="text-sm font-medium text-neutral-content/60 mb-3">匹配关键词</h3>
          <div class="flex flex-wrap gap-2">
            <span 
              v-for="(keyword, index) in intel.keywords_matched.split(',')" 
              :key="index"
              class="badge badge-outline badge-primary"
            >
              {{ keyword.trim() }}
            </span>
          </div>
        </div>
      </div>

      <!-- Timeline -->
      <div class="card bg-neutral/50 border border-neutral-content/10">
        <div class="card-body p-4">
          <h3 class="text-sm font-medium text-neutral-content/60 mb-3">操作记录</h3>
          <div class="text-center py-8 text-neutral-content/30">
            <svg class="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p>暂无操作记录</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>