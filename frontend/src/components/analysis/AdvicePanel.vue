<template>
  <div :class="['advice-card', adviceCardClass]">
    <!-- Decision -->
    <h2>{{ advice.decision || '暂无建议' }}</h2>

    <!-- Summary -->
    <p v-if="advice.summary" class="advice-summary">{{ advice.summary }}</p>

    <!-- Highlights & Warnings -->
    <div v-if="hasHighlights || hasWarnings" class="advice-columns">
      <!-- Highlights -->
      <div v-if="hasHighlights" class="advice-column advice-highlights">
        <h4>&#x2705; 优点</h4>
        <ul>
          <li v-for="(item, index) in advice.highlights" :key="'h-' + index">
            {{ item }}
          </li>
        </ul>
      </div>

      <!-- Warnings -->
      <div v-if="hasWarnings" class="advice-column advice-warnings">
        <h4>&#x26A0;&#xFE0F; 注意事项</h4>
        <ul>
          <li v-for="(item, index) in advice.warnings" :key="'w-' + index">
            {{ item }}
          </li>
        </ul>
      </div>
    </div>

    <!-- Risk Level Footer -->
    <div v-if="advice.risk_level" class="advice-risk-footer">
      综合风险等级：<span :class="riskBadgeClass">{{ advice.risk_level }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  advice: {
    type: Object,
    default: () => ({
      decision: '',
      risk_level: '',
      summary: '',
      highlights: [],
      warnings: [],
    }),
  },
})

const adviceCardClass = computed(() => {
  const decision = props.advice?.decision || ''
  if (decision.includes('推荐') || decision.includes('建议租')) return 'advice-recommend'
  if (decision.includes('考虑') || decision.includes('谨慎')) return 'advice-consider'
  if (decision.includes('不推荐') || decision.includes('不建议')) return 'advice-not'
  return ''
})

const riskBadgeClass = computed(() => {
  const level = props.advice?.risk_level || ''
  if (level.includes('低')) return 'badge badge-green'
  if (level.includes('中')) return 'badge badge-yellow'
  if (level.includes('高')) return 'badge badge-red'
  return 'badge badge-yellow'
})

const hasHighlights = computed(() => {
  return props.advice?.highlights && Array.isArray(props.advice.highlights) && props.advice.highlights.length > 0
})

const hasWarnings = computed(() => {
  return props.advice?.warnings && Array.isArray(props.advice.warnings) && props.advice.warnings.length > 0
})
</script>

<style scoped>
.advice-card {
  border-radius: var(--radius);
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: var(--shadow);
}

.advice-recommend {
  background: linear-gradient(135deg, #d4edda, #c3e6cb);
  border: 2px solid var(--success);
}

.advice-consider {
  background: linear-gradient(135deg, #fff3cd, #ffeaa7);
  border: 2px solid var(--warning);
}

.advice-not {
  background: linear-gradient(135deg, #f8d7da, #f5c6cb);
  border: 2px solid var(--danger);
}

.advice-card h2 {
  font-size: 24px;
  margin-bottom: 12px;
  color: var(--text);
}

.advice-summary {
  font-size: 15px;
  line-height: 1.7;
  color: var(--text);
  margin-bottom: 20px;
}

.advice-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.advice-column {
  background: rgba(255, 255, 255, 0.5);
  border-radius: 10px;
  padding: 16px;
}

.advice-column h4 {
  font-size: 15px;
  margin-bottom: 10px;
  color: var(--text);
}

.advice-column ul {
  list-style: none;
  padding: 0;
}

.advice-column li {
  font-size: 14px;
  padding: 4px 0;
  line-height: 1.5;
  color: var(--text-secondary);
}

.advice-risk-footer {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  font-size: 14px;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .advice-columns {
    grid-template-columns: 1fr;
  }
}
</style>
