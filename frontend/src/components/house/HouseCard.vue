<template>
  <div class="house-card" @click="goDetail">
    <!-- 风险标签（左上角） -->
    <span v-if="house.risk_label" :class="riskClass" class="risk-badge-card">
      {{ riskEmoji }} {{ house.risk_label }}
    </span>

    <!-- 收藏按钮 -->
    <button class="fav-btn" :class="{ active: favStore.isFavorited(house.id) }"
      @click.stop="handleToggleFavorite"
      :title="favStore.isFavorited(house.id) ? '取消收藏' : '收藏'">
      {{ favStore.isFavorited(house.id) ? '★' : '☆' }}
    </button>

    <!-- 左侧缩略图 -->
    <img v-if="imgUrl" :src="imgUrl" :alt="house.title" class="house-card-img" @error="onImgError" />
    <div v-else class="house-card-img"><span>安租</span></div>

    <!-- 右侧信息区 -->
    <div class="house-card-body">
      <div class="house-card-info">
        <!-- 标题 -->
        <h3 class="house-card-title">{{ house.title }}</h3>

        <!-- 位置信息 -->
        <div class="house-card-meta">
          <span class="meta-district">{{ house.district }}</span>
          <span class="meta-dot">·</span>
          <span>{{ house.community }}</span>
          <span class="meta-dot">·</span>
          <span>{{ house.layout }}</span>
          <span class="meta-dot">·</span>
          <span>{{ house.area }}m²</span>
        </div>

        <!-- 快速指标行 -->
        <div class="house-card-indicators">
          <span v-if="house.sunlight_level" :class="'indicator indicator-' + sunlightLevel(house.sunlight_level)">
            &#x2600;&#xFE0F; 采光{{ house.sunlight_level }}
          </span>
          <span v-if="house.noise_level" :class="'indicator indicator-' + noiseLevel(house.noise_level)">
            &#x1F50A; 隔音{{ house.noise_level }}
          </span>
          <span class="indicator indicator-info">
            &#x1F4CB; {{ reviewCount }}条评价
          </span>
        </div>
      </div>

      <!-- 右侧价格 + 标签 -->
      <div class="house-card-right">
        <div class="house-card-price">
          <span class="price-num">{{ formatPrice(house.price) }}</span>
          <span class="price-unit">元/月</span>
        </div>
        <!-- 价格合理性标识 -->
        <span v-if="house.risk_score != null" class="price-tag" :class="priceTagClass">
          {{ priceTagText }}
        </span>
      </div>
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
  const normalized = raw.replace(/\\/g, '/')
  const clean = normalized.replace(/^images\//, '')
  if (clean.startsWith('http')) return clean
  return `/api/v1/images/${clean}`
})

const reviewCount = computed(() => props.house.review_count || 0)

const riskEmoji = computed(() => {
  const label = props.house.risk_label || ''
  if (label.includes('低')) return ''
  if (label.includes('中')) return ''
  if (label.includes('高')) return ''
  return ''
})

const riskClass = computed(() => {
  const label = props.house.risk_label || ''
  if (label.includes('低')) return 'risk-low'
  if (label.includes('中')) return 'risk-mid'
  if (label.includes('高')) return 'risk-high'
  return 'risk-low'
})

const priceTagClass = computed(() => {
  const score = props.house.risk_score || 100
  if (score >= 80) return 'price-fair'
  if (score >= 50) return 'price-warn'
  return 'price-expensive'
})

const priceTagText = computed(() => {
  const score = props.house.risk_score || 100
  if (score >= 80) return '价格合理'
  if (score >= 50) return '略贵'
  return '偏高'
})

function sunlightLevel(level) {
  if (level === '优') return 'good'
  if (level === '良') return 'mid'
  if (level === '中') return 'warn'
  return 'bad'
}

function noiseLevel(level) {
  if (level === '优') return 'good'
  if (level === '良') return 'mid'
  if (level === '中') return 'warn'
  return 'bad'
}

function formatPrice(price) {
  if (!price && price !== 0) return '--'
  const num = Number(price)
  return isNaN(num) ? price : num.toLocaleString('zh-CN')
}

function goDetail() { router.push(`/house/${props.house.id}`) }
function handleToggleFavorite() { favStore.toggle(props.house.id) }
function onImgError(e) { e.target.style.display = 'none' }
</script>

<style scoped>
.risk-badge-card {
  position: absolute; top: 0; left: 0; z-index: 10;
  padding: 4px 14px; border-radius: 0 0 var(--radius-sm) 0;
  font-size: 12px; font-weight: 700; white-space: nowrap;
}
.risk-badge-card.risk-low { background: #D1FAE5; color: #065F46; }
.risk-badge-card.risk-mid { background: #FEF3C7; color: #92400E; }
.risk-badge-card.risk-high { background: #FEE2E2; color: #991B1B; }

.house-card { position: relative; }
.house-card-img span { font-size: 28px; font-weight: 800; color: #D97706; }
.meta-district { font-weight: 600; color: var(--primary-dark); }
.meta-dot { color: var(--text-muted); margin: 0 2px; }

/* Indicators */
.house-card-indicators { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 6px; }
.indicator { font-size: 12px; padding: 3px 10px; border-radius: var(--radius-full); font-weight: 500; }
.indicator-good { background: #D1FAE5; color: #065F46; }
.indicator-mid { background: #FEF3C7; color: #92400E; }
.indicator-warn { background: #FFEDD5; color: #9A3412; }
.indicator-bad { background: #FEE2E2; color: #991B1B; }
.indicator-info { background: #F3F4F6; color: #6B7280; }

/* Price tags */
.price-num { font-size: 24px; font-weight: 800; color: var(--danger); }
.price-unit { font-size: 13px; color: var(--text-secondary); font-weight: 400; }
.price-tag { display: inline-block; padding: 3px 10px; border-radius: var(--radius-full); font-size: 12px; font-weight: 600; margin-top: 4px; }
.price-fair { background: #D1FAE5; color: #065F46; }
.price-warn { background: #FEF3C7; color: #92400E; }
.price-expensive { background: #FEE2E2; color: #991B1B; }

@media (max-width: 768px) {
  .price-num { font-size: 20px; }
  .house-card-indicators { gap: 8px; }
}
</style>
