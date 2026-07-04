<template>
  <div v-if="districts.length > 0" class="comparison-bar">
    <h3 class="comparison-title">各区域房源概览</h3>
    <p class="comparison-subtitle">点击区域直接筛选</p>
    <div class="comparison-cards">
      <div
        v-for="d in districts"
        :key="d.district"
        class="comparison-card"
        :class="{ hovered: hoveredDistrict === d.district }"
        @click="$emit('select-district', d.district)"
        @mouseenter="hoveredDistrict = d.district"
        @mouseleave="hoveredDistrict = null"
      >
        <div class="comp-card-header">
          <span class="comp-district-name">{{ d.district }}</span>
          <span class="comp-count">{{ d.house_count }}套</span>
        </div>
        <div class="comp-card-price">
          <span class="comp-price-value">{{ d.avg_price }}</span>
          <span class="comp-price-unit">元/月</span>
        </div>
        <div class="comp-card-metrics">
          <span class="comp-metric" :class="getSunlightClass(d.avg_sunlight)">
            &#x2600;{{ d.avg_sunlight }}h
          </span>
          <span class="comp-metric" :class="getNoiseClass(d.avg_noise)">
            &#x1F50A;{{ d.avg_noise }}dB
          </span>
        </div>
        <!-- Bar chart visual -->
        <div class="comp-bar-wrapper">
          <div class="comp-bar-price" :style="{ width: barWidth(d.avg_price) + '%' }">
            <span class="comp-bar-label">均价</span>
          </div>
        </div>
        <div class="comp-bar-wrapper">
          <div class="comp-bar-sunlight" :style="{ width: barWidthSunlight(d.avg_sunlight) + '%' }">
            <span class="comp-bar-label">采光</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fetchDistrictStats } from '../../api/client.js'

defineEmits(['select-district'])

const districts = ref([])
const hoveredDistrict = ref(null)

const maxPrice = ref(5000)
const maxSunlight = ref(5)

onMounted(async () => {
  try {
    const data = await fetchDistrictStats()
    if (data && data.districts) {
      districts.value = data.districts.sort((a, b) => b.house_count - a.house_count)
      if (districts.value.length > 0) {
        maxPrice.value = Math.max(...districts.value.map(d => d.avg_price), 1000)
        maxSunlight.value = Math.max(...districts.value.map(d => d.avg_sunlight), 3)
      }
    }
  } catch (e) {
    console.error('Failed to load district stats:', e)
  }
})

function barWidth(price) {
  return Math.min((price / maxPrice.value) * 100, 100)
}

function barWidthSunlight(sunlight) {
  return Math.min((sunlight / maxSunlight.value) * 100, 100)
}

function getSunlightClass(hours) {
  if (hours >= 4) return 'metric-good'
  if (hours >= 2.5) return 'metric-medium'
  return 'metric-bad'
}

function getNoiseClass(db) {
  if (db < 40) return 'metric-good'
  if (db < 50) return 'metric-medium'
  return 'metric-bad'
}
</script>

<style scoped>
.comparison-bar {
  margin-bottom: 24px;
}

.comparison-title {
  font-size: 16px;
  margin-bottom: 2px;
  color: var(--text);
}

.comparison-subtitle {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.comparison-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 10px;
}

.comparison-card {
  background: #fff;
  border-radius: 10px;
  padding: 14px;
  box-shadow: var(--shadow);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 2px solid transparent;
}

.comparison-card:hover,
.comparison-card.hovered {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
  border-color: var(--accent);
}

.comp-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.comp-district-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
}

.comp-count {
  font-size: 11px;
  color: #fff;
  background: var(--accent);
  padding: 1px 8px;
  border-radius: 8px;
  font-weight: 600;
}

.comp-card-price {
  margin-bottom: 8px;
}

.comp-price-value {
  font-size: 20px;
  font-weight: 800;
  color: var(--danger);
}

.comp-price-unit {
  font-size: 11px;
  color: var(--text-secondary);
  margin-left: 2px;
}

.comp-card-metrics {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  font-size: 12px;
}

.comp-metric {
  font-weight: 600;
}

.metric-good {
  color: var(--success);
}

.metric-medium {
  color: var(--warning);
}

.metric-bad {
  color: var(--danger);
}

.comp-bar-wrapper {
  height: 16px;
  background: #f0f0f0;
  border-radius: 4px;
  margin-bottom: 4px;
  overflow: hidden;
  position: relative;
}

.comp-bar-price {
  height: 100%;
  background: linear-gradient(90deg, #f39c1260, #e74c3c80);
  border-radius: 4px;
  min-width: 30%;
  position: relative;
}

.comp-bar-sunlight {
  height: 100%;
  background: linear-gradient(90deg, #27ae6060, #667eea80);
  border-radius: 4px;
  min-width: 30%;
  position: relative;
}

.comp-bar-label {
  position: absolute;
  left: 6px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 10px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.6);
}

@media (max-width: 768px) {
  .comparison-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
