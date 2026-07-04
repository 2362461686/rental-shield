<template>
  <div :class="['landlord-risk-card', riskCardClass]">
    <!-- Header -->
    <div class="risk-header">
      <h3>房东风险评估</h3>
      <span :class="['badge', riskLevelBadgeClass]">{{ landlordRisk.risk_level || '未知' }}</span>
    </div>

    <!-- Landlord Info -->
    <div v-if="house" class="landlord-info">
      <span class="landlord-name">{{ house.landlord_name || '未知房东' }}</span>
      <span v-if="house.landlord_phone_hash" class="landlord-hash">
        {{ house.landlord_phone_hash.substring(0, 8) }}***
      </span>
    </div>

    <!-- Risk Items -->
    <div v-if="landlordRisk.risk_items && landlordRisk.risk_items.length > 0" class="risk-items">
      <div
        v-for="(item, index) in landlordRisk.risk_items"
        :key="index"
        :class="['risk-item', `risk-${item.type || 'warning'}`]"
      >
        <span class="risk-item-type">{{ riskTypeLabel(item.type) }}</span>
        <span class="risk-item-desc">{{ item.description || item.desc || '--' }}</span>
      </div>
    </div>
    <p v-else class="risk-empty">暂无风险项记录</p>

    <!-- Summary -->
    <div v-if="landlordRisk.summary" class="risk-summary">
      <h4>风险评估总结</h4>
      <p>{{ landlordRisk.summary }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  landlordRisk: { type: Object, default: () => ({ risk_level: '', risk_items: [], summary: '' }) },
  house: { type: Object, default: () => ({}) },
})

const riskCardClass = computed(() => {
  const level = props.landlordRisk?.risk_level || ''
  if (level.includes('低')) return 'risk-low'
  if (level.includes('中')) return 'risk-medium'
  if (level.includes('高')) return 'risk-high'
  return ''
})

const riskLevelBadgeClass = computed(() => {
  const level = props.landlordRisk?.risk_level || ''
  if (level.includes('低')) return 'badge-green'
  if (level.includes('中')) return 'badge-yellow'
  if (level.includes('高')) return 'badge-red'
  return 'badge-yellow'
})

function riskTypeLabel(type) {
  const map = {
    warning: '警告',
    info: '提示',
    danger: '风险',
    safe: '安全',
    complication: '复杂',
  }
  return map[type] || type || '提示'
}
</script>

<style scoped>
.landlord-risk-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow);
  border-left: 4px solid var(--border);
}

.risk-low {
  border-left-color: var(--success);
}

.risk-medium {
  border-left-color: var(--warning);
}

.risk-high {
  border-left-color: var(--danger);
}

.risk-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.risk-header h3 {
  font-size: 17px;
  font-weight: 700;
  color: var(--text);
}

.landlord-info {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 14px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 8px;
}

.landlord-name {
  font-weight: 600;
  color: var(--text);
}

.landlord-hash {
  margin-left: 12px;
  font-family: monospace;
  color: var(--text-secondary);
}

.risk-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.risk-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 13px;
}

.risk-warning {
  background: #fff3cd;
  color: #856404;
}

.risk-danger {
  background: #f8d7da;
  color: #721c24;
}

.risk-info {
  background: #d1ecf1;
  color: #0c5460;
}

.risk-safe {
  background: #d4edda;
  color: #155724;
}

.risk-complication {
  background: #e2d9f3;
  color: #4b2d7d;
}

.risk-item-type {
  font-weight: 700;
  white-space: nowrap;
  min-width: 36px;
}

.risk-item-desc {
  flex: 1;
}

.risk-empty {
  font-size: 13px;
  color: var(--text-secondary);
  text-align: center;
  padding: 12px;
}

.risk-summary {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 14px;
}

.risk-summary h4 {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 8px;
}

.risk-summary p {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-secondary);
}
</style>
