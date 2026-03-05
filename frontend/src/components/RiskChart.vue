<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

interface Props {
  high: number
  medium: number
  low: number
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

  const total = props.high + props.medium + props.low

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
    series: [
      {
        name: '风险等级',
        type: 'pie',
        radius: ['60%', '80%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 6,
          borderColor: 'rgba(15, 23, 42, 0.8)',
          borderWidth: 3
        },
        label: {
          show: true,
          position: 'center',
          formatter: () => `{total|${total}}\n{label|总数}`,
          rich: {
            total: {
              fontSize: 28,
              fontWeight: 'bold',
              color: '#e2e8f0'
            },
            label: {
              fontSize: 12,
              color: '#94a3b8',
              padding: [5, 0, 0, 0]
            }
          }
        },
        emphasis: {
          label: {
            show: true
          },
          itemStyle: {
            shadowBlur: 20,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          {
            value: props.high,
            name: '高风险',
            itemStyle: { color: '#ef4444' }
          },
          {
            value: props.medium,
            name: '中风险',
            itemStyle: { color: '#f59e0b' }
          },
          {
            value: props.low,
            name: '低风险',
            itemStyle: { color: '#22c55e' }
          }
        ]
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

watch(() => [props.high, props.medium, props.low], updateChart)
</script>

<template>
  <div class="card bg-neutral/50 border border-neutral-content/10 h-full">
    <div class="card-body p-4">
      <h3 class="text-sm font-medium text-neutral-content/70 mb-2">风险等级分布</h3>
      
      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center h-64">
        <span class="loading loading-spinner loading-md text-primary"></span>
      </div>
      
      <!-- Chart -->
      <div v-else ref="chartRef" class="w-full h-48"></div>
      
      <!-- Legend -->
      <div v-if="!loading" class="flex justify-center gap-4 mt-2">
        <div class="flex items-center gap-1">
          <span class="w-3 h-3 rounded-full bg-error"></span>
          <span class="text-xs text-neutral-content/60">高 {{ high }}</span>
        </div>
        <div class="flex items-center gap-1">
          <span class="w-3 h-3 rounded-full bg-warning"></span>
          <span class="text-xs text-neutral-content/60">中 {{ medium }}</span>
        </div>
        <div class="flex items-center gap-1">
          <span class="w-3 h-3 rounded-full bg-success"></span>
          <span class="text-xs text-neutral-content/60">低 {{ low }}</span>
        </div>
      </div>
    </div>
  </div>
</template>