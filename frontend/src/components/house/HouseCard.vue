<template>
  <div class="house-card card" @click="goDetail">
    <!-- 风险角标 -->
    <span v-if="house.risk_label" class="risk-corner" :class="riskClass">
      {{ house.risk_label }}
    </span>

    <!-- 图片区 -->
    <div class="hc-img-box">
      <img v-if="imgUrl" :src="imgUrl" :alt="house.title" class="hc-img" @error="onImgError" />
      <div v-else class="hc-img-placeholder" :style="{ background: placeholderBg }">
        <svg viewBox="0 0 40 32" width="36" height="28" fill="none">
          <rect x="1" y="12" width="38" height="19" rx="2" fill="rgba(255,255,255,0.3)"/>
          <polygon points="20,1 1,12 39,12" fill="rgba(255,255,255,0.35)"/>
          <rect x="8" y="18" width="6" height="7" rx="1" fill="rgba(255,255,255,0.2)"/>
          <rect x="17" y="18" width="6" height="7" rx="1" fill="rgba(255,255,255,0.15)"/>
          <rect x="26" y="18" width="6" height="7" rx="1" fill="rgba(255,255,255,0.2)"/>
        </svg>
      </div>
    </div>

    <!-- 信息区 -->
    <div class="hc-body">
      <div class="hc-top">
        <h3 class="hc-title">{{ house.title }}</h3>
        <button
          class="hc-fav"
          :class="{ active: favStore.isFavorited(house.id) }"
          @click.stop="handleToggleFavorite"
          :title="favStore.isFavorited(house.id) ? '取消收藏' : '收藏'"
        >{{ favStore.isFavorited(house.id) ? '★' : '☆' }}</button>
      </div>

      <div class="hc-meta">
        <span class="hc-district">{{ house.district }}</span>
        <span class="hc-sep">·</span>
        <span>{{ house.community }}</span>
        <span class="hc-sep">·</span>
        <span>{{ house.layout }}</span>
        <span class="hc-sep">·</span>
        <span>{{ house.area }}m²</span>
      </div>

      <div class="hc-tags">
        <span v-if="house.sunlight_level" class="tag" :class="'tag--' + sLevel">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
          采光{{ house.sunlight_level }}
        </span>
        <span v-if="house.noise_level" class="tag" :class="'tag--' + nLevel">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
          隔音{{ house.noise_level }}
        </span>
        <span class="tag tag--info">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
          {{ house.review_count || 0 }}条评价
        </span>
      </div>
    </div>

    <!-- 价格区 -->
    <div class="hc-price-col">
      <div class="hc-price">
        <span class="hc-price-num">{{ formatPrice(house.price) }}</span>
        <span class="hc-price-unit">元/月</span>
      </div>
      <span v-if="house.risk_score != null" class="hc-score-tag" :class="scoreClass">
        {{ scoreText }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useFavoriteStore } from '../../stores/favorites.js'

const props = defineProps({ house: { type: Object, required: true } })
const router = useRouter()
const favStore = useFavoriteStore()

const imgUrl = computed(() => {
  const raw = props.house.primary_image_url
  if (!raw) return ''
  const n = raw.replace(/\\/g, '/').replace(/^images\//, '')
  return n.startsWith('http') ? n : `/api/v1/images/${n}`
})

const placeholderBg = computed(() => {
  let h = 0; for (let i = 0; i < (props.house.community || '').length; i++) h = props.house.community.charCodeAt(i) + ((h << 5) - h)
  const hue = Math.abs(h) % 360
  return `linear-gradient(135deg, hsl(${hue},50%,65%), hsl(${hue},45%,40%))`
})

const riskClass = computed(() => {
  const l = props.house.risk_label || ''
  if (l.includes('低')) return 'risk-low'
  if (l.includes('中')) return 'risk-mid'
  if (l.includes('高')) return 'risk-high'
  return 'risk-low'
})

const scoreClass = computed(() => {
  const s = props.house.risk_score
  if (s == null) return 'score-unknown'
  return s >= 80 ? 'score-good' : s >= 60 ? 'score-mid' : 'score-bad'
})

const scoreText = computed(() => {
  const s = props.house.risk_score
  if (s == null) return '待评估'
  return s >= 80 ? '推荐' : s >= 60 ? '一般' : '谨慎'
})

const sLevel = computed(() => {
  const l = props.house.sunlight_level; if (!l) return 'info'
  return l === '优' ? 'good' : l === '良' ? 'mid' : l === '中' ? 'warn' : 'bad'
})

const nLevel = computed(() => {
  const l = props.house.noise_level; if (!l) return 'info'
  return l === '优' ? 'good' : l === '良' ? 'mid' : l === '中' ? 'warn' : 'bad'
})

function formatPrice(p) {
  if (!p && p !== 0) return '--'
  const n = Number(p); return isNaN(n) ? p : n.toLocaleString('zh-CN')
}

function goDetail() { router.push(`/house/${props.house.id}`) }
function handleToggleFavorite() { favStore.toggle(props.house.id) }
function onImgError(e) { e.target.style.display = 'none' }
</script>

<style scoped>
.house-card {
  display: flex; gap: 0; cursor: pointer; position: relative;
  padding: 0; overflow: hidden; margin-bottom: 16px;
  transition: transform var(--transition), box-shadow var(--transition);
}
.house-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-lg); }

/* Risk corner badge */
.risk-corner {
  position: absolute; top: 0; left: 0; z-index: 5;
  padding: 3px 12px 4px; border-radius: 0 0 var(--radius-sm) 0;
  font-size: 12px; font-weight: 700;
}
.risk-low { background: var(--success-light); color: #065F46; }
.risk-mid { background: var(--warning-light); color: #92400E; }
.risk-high { background: var(--danger-light); color: #991B1B; }

/* Image box */
.hc-img-box { width: 200px; flex-shrink: 0; overflow: hidden; }
.hc-img { width: 100%; height: 100%; object-fit: cover; }
.hc-img-placeholder {
  width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
}
.hc-img-placeholder svg { opacity: 0.8; }

/* Body */
.hc-body { flex: 1; padding: 16px 20px; display: flex; flex-direction: column; justify-content: space-between; min-width: 0; }
.hc-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; }
.hc-title { font-size: 15px; font-weight: 700; color: var(--text); line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.hc-fav { background: none; border: none; font-size: 18px; color: var(--text-muted); padding: 2px 6px; border-radius: var(--radius-xs); transition: color var(--transition); flex-shrink: 0; }
.hc-fav:hover, .hc-fav.active { color: #F59E0B; }

.hc-meta { font-size: 13px; color: var(--text-secondary); margin-top: 6px; display: flex; align-items: center; flex-wrap: wrap; }
.hc-district { font-weight: 600; color: var(--primary-dark); }
.hc-sep { color: var(--text-muted); margin: 0 4px; }

.hc-tags { display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap; }
.tag { display: inline-flex; align-items: center; gap: 4px; font-size: 12px; padding: 2px 10px; border-radius: var(--radius-full); font-weight: 500; }
.tag--good { background: var(--success-light); color: #065F46; }
.tag--mid { background: var(--warning-light); color: #92400E; }
.tag--warn { background: #FFEDD5; color: #9A3412; }
.tag--bad { background: var(--danger-light); color: #991B1B; }
.tag--info { background: #F3F4F6; color: var(--text-secondary); }

/* Price column */
.hc-price-col { width: 120px; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 16px 12px; border-left: 1px solid var(--border); flex-shrink: 0; }
.hc-price { text-align: center; }
.hc-price-num { font-size: 22px; font-weight: 800; color: var(--danger); }
.hc-price-unit { font-size: 12px; color: var(--text-secondary); }
.hc-score-tag { padding: 3px 12px; border-radius: var(--radius-full); font-size: 12px; font-weight: 600; margin-top: 6px; }
.score-good { background: var(--success-light); color: #065F46; }
.score-mid { background: var(--warning-light); color: #92400E; }
.score-bad { background: var(--danger-light); color: #991B1B; }
.score-unknown { background: #F3F4F6; color: #6B7280; }

@media (max-width: 768px) {
  .house-card { flex-direction: row; }
  .hc-img-box { width: 130px; min-height: 130px; }
  .hc-body { padding: 12px; }
  .hc-price-col { width: auto; padding: 12px; }
  .hc-price-num { font-size: 18px; }
}
@media (max-width: 480px) {
  .hc-img-box { width: 100px; min-height: 100px; }
  .hc-title { font-size: 13px; }
}
</style>
