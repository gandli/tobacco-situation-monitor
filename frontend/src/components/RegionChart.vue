<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import type { RegionCount } from '@/types'

interface Props {
  data: RegionCount[]
  loading?: boolean
}

const props = defineProps<Props>()
const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

function initChart() {
  if (!chartRef.value) return
  
  chartInstance = echarts.init(chartRef.value, 'dark')
  updateChart()
}

function updateChart() {
  if (!chartInstance) return

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'rgba(255, 255, 255, 0.1)',
      textStyle: {
        color: '#e2e8f0'
      }
    },
    legend: {
      type: 'scroll',
      orient: 'vertical',
      right: 10,
      top: 20,
      bottom: 20,
      textStyle: {
        color: '#94a3b8'
      },
      pageTextStyle: {
        color: '#94a3b8'
      }
    },
    series: [
      {
        name: '情报分布',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 4,
          borderColor: 'rgba(15, 23, 42, 0.8)',
          borderWidth: 2
        },
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
            color: '#e2e8f0'
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        labelLine: {
          show: false
        },
        data: props.data.map((item, index) => ({
          value: item.count,
          name: item.region,
          itemStyle: {
            color: [
              '#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef',
              '#ec4899', '#f43f5e', '#ef4444', '#f97316', '#eab308'
            ][index % 10]
          }
        }))
      }
    ]
  }

  chartInstance.setOption(option)
}

function handleResize() {
  chartInstance?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})

watch(() => props.data, updateChart, { deep: true })
</script>

<template>
  <div class="card bg-neutral/50 border border-neutral-content/10 h-full">
    <div class="card-body p-4">
      <h3 class="text-sm font-medium text-neutral-content/70 mb-2">地区分布</h3>
      
      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center h-64">
        <span class="loading loading-spinner loading-md text-primary"></span>
      </div>
      
      <!-- Empty -->
      <div v-else-if="data.length === 0" class="flex flex-col items-center justify-center h-64 text-neutral-content/30">
        <svg class="w-12 h-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
        </svg>
        <p class="text-sm">暂无地区数据</p>
      </div>
      
      <!-- Chart -->
      <div v-else ref="chartRef" class="w-full h-64"></div>
    </div>
  </div>
</template>