<template>
  <div class="metric-card sunlight-card">
    <h3>&#x2600;&#xFE0F; 日照分析</h3>
    <div class="value sunlight-value">{{ formattedHours }}</div>
    <p class="sunlight-unit">小时 / 天</p>
    <span :class="['badge', levelBadgeClass]">{{ sunlight.level || '--' }}</span>

    <!-- Expandable Detail -->
    <button class="detail-btn" @click="expanded = !expanded">
      {{ expanded ? '收起详情' : '查看详情' }}
    </button>

    <Transition name="expand">
      <div v-if="expanded" class="sunlight-detail">
        <h4>计算公式</h4>
        <ul>
          <li>
            <strong>朝向系数：</strong>
            <span>{{ orientationText }}</span>
          </li>
          <li>
            <strong>楼层系数：</strong>
            <span>{{ floorText }}</span>
          </li>
          <li>
            <strong>窗户系数：</strong>
            <span>{{ windowText }}</span>
          </li>
          <li>
            <strong>计算结果：</strong>
            <span class="sunlight-result">{{ formattedHours }} 小时/天 - {{ sunlight.level }}</span>
          </li>
        </ul>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  sunlight: { type: Object, default: () => ({ hours: 0, level: '' }) },
  orientation: { type: String, default: '' },
  floor: { type: [Number, String], default: '' },
  total_floors: { type: [Number, String], default: '' },
  window_type: { type: String, default: '' },
})

const expanded = ref(false)

const formattedHours = computed(() => {
  const hours = props.sunlight?.hours
  if (hours == null) return '--'
  return Number(hours).toFixed(1)
})

const levelBadgeClass = computed(() => {
  const level = props.sunlight?.level || ''
  if (level.includes('优') || level.includes('良')) return 'badge-green'
  if (level.includes('中')) return 'badge-yellow'
  return 'badge-red'
})

const orientationText = computed(() => {
  const map = { '南': '最佳采光 (1.0x)', '东南': '良好采光 (0.9x)', '西南': '良好采光 (0.9x)', '东': '一般采光 (0.7x)', '西': '一般采光 (0.7x)', '北': '较差采光 (0.5x)' }
  return map[props.orientation] || `${props.orientation} (需人工评估)`
})

const floorText = computed(() => {
  const f = Number(props.floor)
  const t = Number(props.total_floors)
  if (isNaN(f) || isNaN(t)) return '数据不足'
  const ratio = f / t
  if (ratio >= 0.7) return `高层${f}/${t}F (系数 0.95x)`
  if (ratio >= 0.3) return `中层${f}/${t}F (系数 0.75x)`
  return `低层${f}/${t}F (系数 0.5x)`
})

const windowText = computed(() => {
  const map = { '落地窗': '极佳采光 (1.0x)', '飘窗': '良好采光 (0.85x)', '普通窗': '一般采光 (0.7x)', '小窗': '较差采光 (0.5x)' }
  return map[props.window_type] || `${props.window_type || '--'} (需人工评估)`
})
</script>

<style scoped>
.sunlight-card {
  text-align: center;
}

.sunlight-value {
  color: #e67e22;
}

.sunlight-unit {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.sunlight-detail {
  margin-top: 16px;
  text-align: left;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
}

.sunlight-detail h4 {
  font-size: 14px;
  margin-bottom: 10px;
  color: var(--text);
}

.sunlight-detail ul {
  list-style: none;
  padding: 0;
}

.sunlight-detail li {
  font-size: 13px;
  padding: 6px 0;
  border-bottom: 1px solid #eee;
  color: var(--text-secondary);
}

.sunlight-detail li:last-child {
  border-bottom: none;
}

.sunlight-detail li strong {
  color: var(--text);
}

.sunlight-result {
  color: #e67e22;
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
