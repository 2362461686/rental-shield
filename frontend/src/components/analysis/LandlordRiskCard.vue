<template>
  <div :class="['landlord-risk-card card', riskCardClass]">
    <div class="lr-header">
      <h3>房东风险评估</h3>
      <span :class="['lr-badge', riskLevelBadge]">{{ landlordRisk.risk_level || '未知' }}</span>
    </div>

    <div v-if="house" class="lr-info">
      <span class="lr-name">{{ house.landlord_name || '未知房东' }}</span>
      <span v-if="house.landlord_phone_hash" class="lr-hash">{{ house.landlord_phone_hash.substring(0, 8) }}***</span>
    </div>

    <!-- Cross-property view -->
    <div v-if="landlordHouses.length > 1" class="lr-cross">
      <div class="lr-cross-title">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
        此房东共有 <strong>{{ landlordHouses.length }}</strong> 套房源出租
      </div>
      <div class="lr-house-list">
        <div v-for="h in landlordHouses" :key="h.id" class="lr-house-item" :class="{ current: h.id === house?.id }" @click="goHouse(h.id)">
          <span class="lr-h-community">{{ h.community }}</span>
          <span class="lr-h-price">{{ h.price }}元</span>
        </div>
      </div>
    </div>

    <div v-if="landlordRisk.risk_items && landlordRisk.risk_items.length" class="lr-items">
      <div v-for="(item, i) in landlordRisk.risk_items" :key="i" :class="['lr-item', `lr-${item.type || 'warning'}`]">
        <span class="lr-item-type">{{ typeLabel(item.type) }}</span>
        <span class="lr-item-desc">{{ item.description || item.desc || '--' }}</span>
      </div>
    </div>
    <p v-else class="lr-empty">暂无风险项记录</p>

    <div v-if="landlordRisk.summary" class="lr-summary">
      <h4>风险评估总结</h4>
      <p>{{ landlordRisk.summary }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchLandlordHouses } from '../../api/client.js'

const props = defineProps({
  landlordRisk: { type: Object, default: () => ({ risk_level: '', risk_items: [], summary: '' }) },
  house: { type: Object, default: () => ({}) },
})

const router = useRouter()
const landlordHouses = ref([])

onMounted(async () => {
  if (props.house?.landlord_phone_hash) {
    try { landlordHouses.value = await fetchLandlordHouses(props.house.landlord_phone_hash) } catch (e) { /* */ }
  }
})

const riskCardClass = computed(() => {
  const l = props.landlordRisk?.risk_level || ''
  if (l.includes('低')) return 'lr-low'; if (l.includes('中')) return 'lr-mid'; if (l.includes('高')) return 'lr-high'
  return ''
})
const riskLevelBadge = computed(() => {
  const l = props.landlordRisk?.risk_level || ''
  if (l.includes('低')) return 'badge-ok'; if (l.includes('中')) return 'badge-warn'; if (l.includes('高')) return 'badge-bad'
  return 'badge-warn'
})

function typeLabel(t) {
  const m = { warning: '警告', info: '提示', danger: '风险', safe: '安全', complication: '复杂' }
  return m[t] || t || '提示'
}
function goHouse(id) { router.push(`/house/${id}`) }
</script>

<style scoped>
.landlord-risk-card { padding: 20px; }
.lr-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.lr-header h3 { font-size: 16px; font-weight: 700; }
.lr-badge { padding: 3px 12px; border-radius: var(--radius-full); font-size: 12px; font-weight: 600; }
.badge-ok { background: var(--success-light); color: #065F46; }
.badge-warn { background: var(--warning-light); color: #92400E; }
.badge-bad { background: var(--danger-light); color: #991B1B; }

.lr-info { font-size: 13px; color: var(--text-secondary); margin-bottom: 12px; padding: 10px; background: #F9FAFB; border-radius: var(--radius-sm); }
.lr-name { font-weight: 600; color: var(--text); }

.lr-cross { margin-bottom: 14px; padding: 12px; background: #F0F9FF; border-radius: var(--radius-sm); border: 1px solid #BAE6FD; }
.lr-cross-title { font-size: 13px; color: var(--text-secondary); display: flex; align-items: center; gap: 6px; margin-bottom: 8px; }
.lr-house-list { display: flex; flex-direction: column; gap: 6px; }
.lr-house-item { display: flex; justify-content: space-between; padding: 6px 10px; background: #fff; border-radius: var(--radius-xs); cursor: pointer; transition: box-shadow var(--transition); font-size: 13px; }
.lr-house-item:hover { box-shadow: var(--shadow-sm); }
.lr-house-item.current { border: 1.5px solid var(--primary); background: var(--bg-warm); }
.lr-h-community { font-weight: 600; color: var(--text); }
.lr-h-price { color: var(--text-secondary); }

.lr-items { display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px; }
.lr-item { display: flex; gap: 10px; padding: 8px 12px; border-radius: var(--radius-xs); font-size: 13px; }
.lr-item-type { font-weight: 700; white-space: nowrap; min-width: 36px; }
.lr-warning { background: #FEF3C7; color: #92400E; }
.lr-danger { background: #FEE2E2; color: #991B1B; }
.lr-info { background: #DBEAFE; color: #1E40AF; }
.lr-safe { background: var(--success-light); color: #065F46; }
.lr-empty { font-size: 13px; color: var(--text-muted); text-align: center; padding: 12px; }

.lr-summary { background: #F9FAFB; border-radius: var(--radius-sm); padding: 12px; }
.lr-summary h4 { font-size: 13px; font-weight: 700; margin-bottom: 6px; }
.lr-summary p { font-size: 13px; line-height: 1.6; color: var(--text-secondary); }

.lr-low { border-left: 4px solid var(--success); }
.lr-mid { border-left: 4px solid var(--warning); }
.lr-high { border-left: 4px solid var(--danger); }
</style>
