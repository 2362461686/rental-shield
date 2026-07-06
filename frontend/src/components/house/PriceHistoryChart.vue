<template>
  <div class="price-chart" v-if="data.length > 0">
    <div class="chart-header">
      <span class="chart-label">价格走势 ({{ months }}个月)</span>
      <span class="chart-legend">
        <span class="legend-dot current"></span> 本房源
        <span class="legend-dot avg"></span> 市场均价
      </span>
    </div>
    <div class="chart-container">
      <svg :viewBox="`0 0 ${W} ${H}`" class="chart-svg">
        <!-- Grid lines -->
        <line v-for="y in gridLines" :key="'g'+y" :x1="PAD" :y1="y" :x2="W-PAD" :y2="y" class="grid-line" />
        <!-- Y axis labels -->
        <text v-for="(label, i) in yLabels" :key="'yl'+i" :x="PAD-8" :y="yPositions[i]+4" class="axis-label" text-anchor="end">{{ label }}</text>
        <!-- X axis labels -->
        <text v-for="(item, i) in data" :key="'xl'+i" :x="xScale(i)" :y="H-6" class="axis-label" text-anchor="middle">{{ formatDate(item.record_date) }}</text>
        <!-- Avg price line -->
        <polyline v-if="marketPrice" :points="avgLinePoints" class="chart-line avg-line" />
        <!-- Price line -->
        <polyline :points="priceLinePoints" class="chart-line price-line" />
        <!-- Area fill -->
        <polygon v-if="marketPrice" :points="areaPoints" class="chart-area" />
        <!-- Data dots -->
        <circle v-for="(item, i) in data" :key="'d'+i" :cx="xScale(i)" :cy="yScale(Math.min(maxY, item.price))" r="4" class="data-dot" />
        <!-- Tooltips on hover -->
        <rect
          v-for="(item, i) in data" :key="'t'+i"
          :x="xScale(i)-25" :y="yScale(Math.min(maxY, item.price))-28"
          width="50" height="22" rx="4"
          class="tooltip-rect"
          :class="{ hidden: tooltipIdx !== i }"
        />
        <text
          v-for="(item, i) in data" :key="'tv'+i"
          :x="xScale(i)" :y="yScale(Math.min(maxY, item.price))-13"
          class="tooltip-text"
          :class="{ hidden: tooltipIdx !== i }"
          text-anchor="middle"
        >{{ item.price }}</text>
        <!-- Invisible wider hit areas for hover -->
        <rect
          v-for="(item, i) in data" :key="'h'+i"
          :x="xScale(i)-15" :y="PAD" :width="step>30?step:30" :height="H-PAD*2"
          fill="transparent"
          @mouseenter="tooltipIdx=i" @mouseleave="tooltipIdx=null"
        />
      </svg>
    </div>
    <p class="chart-note">{{ trendText }}</p>
  </div>
  <div v-else class="chart-empty">暂无价格历史数据</div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  data: { type: Array, default: () => [] },
  marketPrice: { type: Number, default: null },
})

const tooltipIdx = ref(null)

const W = 520
const H = 200
const PAD = 40

const step = computed(() => props.data.length > 1 ? (W - PAD * 2) / (props.data.length - 1) : 0)
const maxY = computed(() => {
  let mx = 0
  for (const d of props.data) mx = Math.max(mx, d.price)
  if (props.marketPrice) mx = Math.max(mx, props.marketPrice)
  return Math.ceil(mx / 500) * 500 || 500
})
const minY = computed(() => {
  let mn = Infinity
  for (const d of props.data) mn = Math.min(mn, d.price)
  return Math.floor(mn / 500) * 500 || 0
})

const gridLines = computed(() => {
  const lines = []
  const range = maxY.value - minY.value
  const step = range / 4
  for (let i = 0; i <= 4; i++) lines.push(yScale(minY.value + step * i))
  return lines
})

const yLabels = computed(() => {
  const labels = []
  const range = maxY.value - minY.value
  const step = range / 4
  for (let i = 0; i <= 4; i++) labels.push(Math.round(minY.value + step * i))
  return labels
})

const yPositions = computed(() => {
  const pos = []
  const range = maxY.value - minY.value
  const step = range / 4
  for (let i = 0; i <= 4; i++) pos.push(yScale(minY.value + step * i))
  return pos
})

const months = computed(() => props.data.length)

function xScale(i) { return PAD + i * step.value }
function yScale(v) {
  const range = maxY.value - minY.value || 1
  return H - PAD - ((v - minY.value) / range) * (H - PAD * 2)
}

const priceLinePoints = computed(() => {
  return props.data.map((d, i) => `${xScale(i)},${yScale(Math.min(maxY.value, d.price))}`).join(' ')
})

const avgLinePoints = computed(() => {
  if (!props.marketPrice) return ''
  return `${xScale(0)},${yScale(props.marketPrice)} ${xScale(props.data.length - 1)},${yScale(props.marketPrice)}`
})

const areaPoints = computed(() => {
  if (!props.marketPrice || props.data.length < 2) return ''
  const points = props.data.map((d, i) => `${xScale(i)},${yScale(Math.min(maxY.value, d.price))}`).join(' ')
  const last = xScale(props.data.length - 1)
  const first = xScale(0)
  const yAvg = yScale(props.marketPrice)
  return `${first},${yAvg} ${points} ${last},${yAvg}`
})

const trendText = computed(() => {
  if (props.data.length < 2) return ''
  const first = props.data[0].price
  const last = props.data[props.data.length - 1].price
  const change = last - first
  const pct = first ? Math.round((change / first) * 100) : 0
  if (change > 0) return `近${months.value}个月上涨 ${Math.abs(pct)}%，略高于市场，需关注性价比`
  if (change < 0) return `近${months.value}个月下跌 ${Math.abs(pct)}%，当前价格有优势`
  return `近${months.value}个月价格稳定`
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  return typeof dateStr === 'string' ? dateStr.substring(5) : String(dateStr).substring(5)
}
</script>

<style scoped>
.price-chart {
  background: #fff; border-radius: var(--radius);
  padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.chart-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 16px;
}
.chart-label { font-size: 14px; font-weight: 600; color: var(--text); }
.chart-legend { font-size: 12px; color: var(--text-secondary); display: flex; gap: 10px; align-items: center; }
.legend-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.legend-dot.current { background: var(--primary); }
.legend-dot.avg { background: var(--text-muted); }
.chart-container { width: 100%; overflow: hidden; }
.chart-svg { width: 100%; height: auto; }
.grid-line { stroke: #F0F1F3; stroke-width: 1; }
.axis-label { font-size: 10px; fill: var(--text-muted); }
.chart-line { fill: none; stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round; }
.price-line { stroke: var(--primary); }
.avg-line { stroke: var(--text-muted); stroke-dasharray: 6 3; stroke-width: 1.5; }
.chart-area { fill: rgba(245,158,11,0.08); }
.data-dot { fill: #fff; stroke: var(--primary); stroke-width: 2; }
.tooltip-rect { fill: rgba(0,0,0,0.75); }
.tooltip-rect.hidden { display: none; }
.tooltip-text { font-size: 11px; fill: #fff; font-weight: 600; }
.tooltip-text.hidden { display: none; }
.chart-note { font-size: 12px; color: var(--text-secondary); margin-top: 10px; text-align: center; }
.chart-empty { text-align: center; padding: 40px; color: var(--text-muted); font-size: 14px; }
</style>
