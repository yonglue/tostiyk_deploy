<!-- src/components/TrendChart.vue -->
<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  dates: { type: Array, default: () => [] },
  amounts: { type: Array, default: () => [] }
})

const chartRef = ref(null)
let chartInstance = null
let observer = null

const getCssVar = (name) => {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}

const renderChart = () => {
  if (!chartRef.value) return
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  const accentColor = getCssVar('--color-accent') || '#1e40af'
  const textColor = getCssVar('--color-secondary') || '#475569'
  const lineColor = getCssVar('--color-line') || '#e2e8f0'
  const isDark = document.documentElement.classList.contains('dark')

  const option = {
    grid: { top: 15, left: 10, right: 20, bottom: 5, containLabel: true },
    tooltip: {
      trigger: 'axis',
      backgroundColor: isDark ? 'rgba(30, 41, 59, 0.9)' : 'rgba(255, 255, 255, 0.95)',
      borderColor: lineColor,
      borderWidth: 1,
      textStyle: { color: isDark ? '#f1f5f9' : '#0f172a', fontSize: 12, fontWeight: 'bold' },
      padding: [6, 10],
      extraCssText: 'box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-radius: 6px;',
      axisPointer: { type: 'line', lineStyle: { color: accentColor, type: 'dashed', width: 1 } }
    },
    xAxis: {
      type: 'category',
      data: props.dates,
      boundaryGap: false,
      axisLine: { lineStyle: { color: lineColor } },
      axisLabel: { color: textColor, fontSize: 11, margin: 12 },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: lineColor, type: 'dashed', opacity: 0.5 } },
      axisLabel: { color: textColor, fontSize: 11, formatter: '${value}' }
    },
    series: [
      {
        name: '销售额',
        type: 'line',
        smooth: 0.4, // 平滑度，0.4 刚刚好不夸张
        showSymbol: false, // 默认不显示圆点，鼠标悬浮才显示
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: { 
          color: accentColor, 
          borderWidth: 2, 
          borderColor: isDark ? '#1e293b' : '#ffffff' 
        },
        lineStyle: { 
          width: 3, /* 从 2 改成 3，在深色背景下更凸显 */
          color: accentColor
        },
        areaStyle: {
          // 🌟 极淡的渐变阴影，只留一点点悬浮感
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: accentColor + (isDark ? '15' : '15') }, /* 暗色模式下也降到 15% */
            { offset: 1, color: accentColor + '00' }
          ])
        },
        data: props.amounts
      }
    ]
  }

  chartInstance.setOption(option, { notMerge: true })
}

onMounted(() => {
  renderChart()
  window.addEventListener('resize', () => chartInstance?.resize())
  observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.attributeName === 'class') renderChart()
    })
  })
  observer.observe(document.documentElement, { attributes: true })
})

watch(() => [props.dates, props.amounts], () => {
  renderChart()
}, { deep: true })

onUnmounted(() => {
  window.removeEventListener('resize', () => chartInstance?.resize())
  if (observer) observer.disconnect()
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<template>
  <div ref="chartRef" class="w-full h-full min-h-[250px]"></div>
</template>