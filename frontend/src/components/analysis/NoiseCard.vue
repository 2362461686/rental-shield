<template>
  <div class="metric-card noise-card">
    <h3>&#x1F50A; 噪音分析</h3>
    <div class="value noise-value">{{ formattedDb }}</div>
    <p class="noise-unit">dB</p>
    <span :class="['badge', noiseBadgeClass]">{{ noise.level || '--' }}</span>

    <!-- Expandable Detail -->
    <button class="detail-btn" @click="expanded = !expanded">
      {{ expanded ? '收起详情' : '查看详情' }}
    </button>

    <Transition name="expand">
      <div v-if="expanded" class="noise-detail">
        <h4>计算公式</h4>
        <ul>
          <li>
            <strong>建筑类型系数：</strong>
            <span>{{ buildingTypeText }}</span>
          </li>
          <li>
            <strong>建筑年代系数：</strong>
            <span>{{ buildingYearText }}</span>
          </li>
          <li>
            <strong>楼层系数：</strong>
            <span>{{ floorNoiseText }}</span>
          </li>
          <li>
            <strong>距主街系数：</strong>
            <span>{{ streetDistanceText }}</span>
          </li>
          <li>
            <strong>底商影响：</strong>
            <span>{{ businessBelowText }}</span>
          </li>
          <li>
            <strong>计算结果：</strong>
            <span class="noise-result">{{ formattedDb }} dB - {{ noise.level }}</span>
          </li>
        </ul>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  noise: { type: Object, default: () => ({ db: 0, level: '' }) },
  building_type: { type: String, default: '' },
  building_year: { type: [Number, String], default: '' },
  floor: { type: [Number, String], default: '' },
  total_floors: { type: [Number, String], default: '' },
  distance_to_street: { type: [Number, String], default: '' },
  has_business_below: { type: Boolean, default: false },
})

const expanded = ref(false)

const formattedDb = computed(() => {
  const db = props.noise?.db
  if (db == null) return '--'
  return Number(db).toFixed(1)
})

const noiseBadgeClass = computed(() => {
  const level = props.noise?.level || ''
  if (level.includes('优') || level.includes('静')) return 'badge-green'
  if (level.includes('良') || level.includes('中')) return 'badge-yellow'
  return 'badge-red'
})

const buildingTypeText = computed(() => {
  const map = { '板楼': '隔音较好 (0.8x)', '塔楼': '隔音一般 (1.0x)', '筒子楼': '隔音较差 (1.2x)' }
  return map[props.building_type] || `${props.building_type || '未知'} (默认 1.0x)`
})

const buildingYearText = computed(() => {
  const year = Number(props.building_year)
  if (isNaN(year)) return '数据不足'
  if (year >= 2015) return `${year}年 - 新楼隔音好 (0.8x)`
  if (year >= 2005) return `${year}年 - 隔音一般 (1.0x)`
  return `${year}年 - 老楼隔音差 (1.2x)`
})

const floorNoiseText = computed(() => {
  const f = Number(props.floor)
  const t = Number(props.total_floors)
  if (isNaN(f) || isNaN(t)) return '数据不足'
  if (f <= 3) return `低层${f}F (系数 1.2x，更靠近噪音源)`
  if (f >= t - 3) return `高层${f}F (系数 0.7x)`
  return `中层${f}F (系数 1.0x)`
})

const streetDistanceText = computed(() => {
  const d = Number(props.distance_to_street)
  if (isNaN(d)) return '数据不足'
  if (d < 50) return `${d}m - 紧邻主街 (1.3x)`
  if (d < 200) return `${d}m - 较近 (1.1x)`
  return `${d}m - 距离较远 (0.8x)`
})

const businessBelowText = computed(() => {
  return props.has_business_below ? '有底商，噪音增加 (1.2x)' : '无底商 (1.0x)'
})
</script>

<style scoped>
.noise-card {
  text-align: center;
}

.noise-value {
  color: #3498db;
}

.noise-unit {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.noise-detail {
  margin-top: 16px;
  text-align: left;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
}

.noise-detail h4 {
  font-size: 14px;
  margin-bottom: 10px;
  color: var(--text);
}

.noise-detail ul {
  list-style: none;
  padding: 0;
}

.noise-detail li {
  font-size: 13px;
  padding: 6px 0;
  border-bottom: 1px solid #eee;
  color: var(--text-secondary);
}

.noise-detail li:last-child {
  border-bottom: none;
}

.noise-detail li strong {
  color: var(--text);
}

.noise-result {
  color: #3498db;
  font-weight: 700;
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.25s ease;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 500px;
}
</style>
