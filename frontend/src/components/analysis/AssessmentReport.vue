<template>
  <div class="assessment-report">
    <!-- Loading -->
    <div v-if="loading" class="assess-loading">
      <Spinner text="正在分析评论…" />
    </div>

    <!-- No Reviews / No Data -->
    <div v-else-if="source === 'none' || !assessment" class="assess-empty">
      <div class="assess-empty-icon">📝</div>
      <p>暂无评价证据，建议补充评论后再分析</p>
    </div>

    <!-- Analysis Result -->
    <template v-else>
      <!-- Recommendation Banner -->
      <div class="assess-recommendation" :class="recClass">
        <span class="rec-icon">{{ recIcon }}</span>
        <div>
          <strong>{{ recLabel }}</strong>
          <span class="rec-meta">
            整体风险：{{ levelLabel(assessment.overall_risk_level) }}（{{ assessment.overall_risk_score }} 分）
            <span class="rec-source" v-if="assessment.source">· {{ sourceLabel(assessment.source) }}</span>
          </span>
        </div>
      </div>

      <!-- Category Cards -->
      <div class="assess-cards">
        <div
          v-for="cat in categoryList"
          :key="cat.key"
          class="assess-card"
          :class="'card-' + cat.level"
        >
          <div class="card-header">
            <span class="card-label">{{ cat.label }}</span>
            <span class="card-level" :class="'level-' + cat.level">{{ cat.levelText }}</span>
          </div>
          <div class="card-score">{{ cat.score }}<small>分</small></div>
          <div class="card-evidence" v-if="cat.evidence.length">
            <div v-for="(ev, ei) in cat.evidence" :key="ei" class="evidence-item">
              "{{ ev }}"
            </div>
          </div>
          <div class="card-evidence-empty" v-else>未提及</div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import Spinner from '../ui/Spinner.vue'

const props = defineProps({
  assessment: { type: Object, default: null },
  loading: { type: Boolean, default: false },
})

const CATEGORY_KEYS = ['noise', 'sunlight', 'landlord', 'deposit', 'commute', 'safety']
const CATEGORY_LABELS = {
  noise: '噪音', sunlight: '采光', landlord: '房东',
  deposit: '押金', commute: '通勤', safety: '安全',
}
const LEVEL_MAP = { low: '低风险', medium: '中风险', high: '高风险', unknown: '未提及' }

const REC_CONFIG = {
  recommend:  { label: '推荐',     cls: 'rec-green',  icon: '✅' },
  consider:   { label: '谨慎考虑', cls: 'rec-yellow', icon: '⚠️' },
  reject:     { label: '不建议',   cls: 'rec-red',    icon: '❌' },
  unknown:    { label: '信息不足', cls: 'rec-gray',   icon: 'ℹ️' },
}

const source = computed(() => props.assessment?.source || 'none')

const recCfg = computed(() => {
  const rec = props.assessment?.recommendation
  return REC_CONFIG[rec] || REC_CONFIG.unknown
})
const recClass = computed(() => recCfg.value.cls)
const recIcon = computed(() => recCfg.value.icon)
const recLabel = computed(() => recCfg.value.label)

const categoryList = computed(() => {
  const cats = props.assessment?.categories || {}
  return CATEGORY_KEYS.map(key => {
    const c = cats[key] || { level: 'unknown', score: 0, evidence: [] }
    return {
      key,
      label: CATEGORY_LABELS[key] || key,
      level: c.level || 'unknown',
      levelText: LEVEL_MAP[c.level] || '未提及',
      score: c.score ?? 0,
      evidence: c.evidence || [],
    }
  })
})

function levelLabel(v) { return LEVEL_MAP[v] || v }
function sourceLabel(s) { return s === 'deepseek' ? 'AI 分析' : s === 'rules' ? '规则分析' : s }
</script>

<style scoped>
.assessment-report {
  background: #fff; border-radius: var(--radius); padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}

/* ── Loading / Empty ── */
.assess-loading { padding: 24px 0; }
.assess-empty { text-align: center; padding: 32px 20px; color: var(--text-secondary); }
.assess-empty-icon { font-size: 32px; margin-bottom: 8px; }
.assess-empty p { font-size: 14px; margin: 0; }

/* ── Recommendation ── */
.assess-recommendation {
  display: flex; align-items: center; gap: 12px;
  padding: 14px 18px; border-radius: var(--radius-sm); margin-bottom: 20px;
}
.assess-recommendation strong { font-size: 16px; display: block; }
.rec-icon { font-size: 24px; flex-shrink: 0; }
.rec-meta { font-size: 13px; color: inherit; opacity: 0.85; }
.rec-source { opacity: 0.7; }
.rec-green  { background: #D1FAE5; color: #065F46; }
.rec-yellow { background: #FEF3C7; color: #92400E; }
.rec-red    { background: #FEE2E2; color: #991B1B; }
.rec-gray   { background: #F3F4F6; color: #6B7280; }

/* ── Category Cards Grid ── */
.assess-cards {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;
}
.assess-card {
  border: 1.5px solid var(--border); border-radius: var(--radius-sm);
  padding: 14px 16px; background: #FAFAFA;
}
.assess-card.card-low    { border-color: #A7F3D0; background: #F0FDF4; }
.assess-card.card-medium { border-color: #FDE68A; background: #FFFBEB; }
.assess-card.card-high   { border-color: #FECACA; background: #FEF2F2; }
.assess-card.card-unknown { border-color: #E5E7EB; background: #F9FAFB; }

.card-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;
}
.card-label { font-size: 14px; font-weight: 700; color: var(--text); }
.card-level { font-size: 12px; font-weight: 600; padding: 2px 8px; border-radius: var(--radius-full); }
.level-low     { background: #D1FAE5; color: #065F46; }
.level-medium  { background: #FEF3C7; color: #92400E; }
.level-high    { background: #FEE2E2; color: #991B1B; }
.level-unknown { background: #F3F4F6; color: #6B7280; }

.card-score { font-size: 20px; font-weight: 800; margin-bottom: 10px; }
.card-score small { font-size: 12px; font-weight: 400; color: var(--text-secondary); margin-left: 2px; }

.card-evidence { display: flex; flex-direction: column; gap: 4px; }
.evidence-item {
  font-size: 12px; color: var(--text-secondary); line-height: 1.5;
  padding-left: 8px; border-left: 2px solid var(--border-strong);
  word-break: break-all;
}
.card-evidence-empty { font-size: 12px; color: var(--text-muted); }

@media (max-width: 768px) {
  .assess-cards { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 480px) {
  .assess-cards { grid-template-columns: 1fr; }
}
</style>
