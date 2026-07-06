<template>
  <div class="detail-page">
    <!-- Loading Skeleton -->
    <div v-if="detailStore.loading.house" class="detail-skeleton">
      <div class="skeleton" style="height: 200px; width: 100%; margin-bottom: 16px;"></div>
      <div class="skeleton" style="height: 32px; width: 60%; margin-bottom: 12px;"></div>
      <div class="skeleton" style="height: 32px; width: 40%; margin-bottom: 24px;"></div>
      <div class="skeleton" style="height: 300px; width: 100%; margin-bottom: 16px;"></div>
      <div class="info-grid">
        <div v-for="n in 8" :key="n" class="info-item">
          <div class="skeleton" style="height: 16px; width: 40%; margin-bottom: 6px;"></div>
          <div class="skeleton" style="height: 20px; width: 70%;"></div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="detailStore.errors.house" class="empty-state">
      <div class="icon">&#x26A0;&#xFE0F;</div>
      <h3>加载失败</h3>
      <p>{{ detailStore.errors.house }}</p>
    </div>

    <!-- Loaded Content -->
    <template v-else-if="detailStore.house">
      <!-- Detail Header -->
      <div class="detail-header">
        <div class="detail-breadcrumb">
          <button @click="goBack">&larr; 返回搜索</button>
          <button class="fav-header-btn" :class="{ 'is-faved': favStore.isFavorited(Number(props.id)) }" @click="handleFavorite">
            {{ favStore.isFavorited(Number(props.id)) ? '❤️ 已收藏' : '🤍 收藏' }}
          </button>
        </div>
        <h2>{{ detailStore.house.title }}</h2>
        <div class="detail-header-meta">
          <span class="detail-header-price">{{ formatPrice(detailStore.house.price) }}{{ detailStore.house.price_unit || '元/月' }}</span>
          <span>{{ detailStore.house.district }}</span>
          <span>-</span>
          <span>{{ detailStore.house.community }}</span>
          <span>-</span>
          <span>{{ detailStore.house.layout }}</span>
          <span>{{ detailStore.house.area }}m&#178;</span>
        </div>
      </div>

      <!-- Location Mini Map -->
      <div class="section" v-if="detailStore.house.latitude && detailStore.house.longitude">
        <h3 class="section-title">位置地图</h3>
        <HouseMap
          mode="detail"
          :house-detail="detailStore.house"
          :workplace="houseStore.workspace.configured ? houseStore.workspace : null"
        />
      </div>

      <!-- Commute Info -->
      <div class="section">
        <h3 class="section-title">通勤分析</h3>
        <div v-if="detailStore.house.commute_duration != null" class="commute-card">
          <div class="commute-metric primary">
            <span class="commute-label">预估通勤</span>
            <span class="commute-value" :class="commuteLevel">
              {{ detailStore.house.commute_duration }}<small>分钟</small>
            </span>
          </div>
          <div class="commute-metric" v-if="detailStore.house.commute_score != null">
            <span class="commute-label">通勤评分</span>
            <span class="commute-value">{{ detailStore.house.commute_score }}<small>/100</small></span>
          </div>
          <div class="commute-badge" :class="commuteLevel">
            {{ commuteLabel }}
          </div>
        </div>
        <div v-else-if="houseStore.workspace.configured" class="commute-card muted">
          <p>正在为你计算到 "<strong>{{ houseStore.workspace.name }}</strong>" 的通勤时间...</p>
        </div>
        <div v-else class="commute-card muted">
          <p>&#x1F4CD; 设置通勤地点后即可计算通勤时间</p>
          <button class="commute-set-btn" @click="goToSearch">设置通勤地点</button>
        </div>
      </div>

      <!-- Image Gallery -->
      <ImageGallery
        :images="detailStore.images"
        :community="detailStore.house.community"
      />

      <!-- House Info Table -->
      <div class="section">
        <h3 class="section-title">房屋信息</h3>
        <HouseInfoTable :house="detailStore.house" />
      </div>

      <!-- Price Analysis -->
      <div class="section" v-if="detailStore.house">
        <h3 class="section-title">价格分析</h3>
        <div class="price-section">
          <div class="price-summary-cards">
            <div class="price-metric">
              <span class="price-metric-label">月租金</span>
              <span class="price-metric-value">{{ formatPrice(detailStore.house.price) }}<small>元/月</small></span>
            </div>
            <div class="price-metric">
              <span class="price-metric-label">市场均价</span>
              <span class="price-metric-value market">{{ formatPrice(detailStore.house.market_price) }}<small>元/月</small></span>
            </div>
            <div class="price-metric">
              <span class="price-metric-label">价格偏差</span>
              <span class="price-metric-value" :class="priceDevClass">
                {{ priceDevText }}
              </span>
            </div>
            <div class="price-metric">
              <span class="price-metric-label">价格合理</span>
              <span class="price-metric-value" :class="detailStore.house.is_price_reasonable ? 'reasonable' : 'unreasonable'">
                {{ detailStore.house.is_price_reasonable ? '合理' : '偏高' }}
              </span>
            </div>
          </div>
          <!-- Price comparison bar -->
          <div class="price-comparison-bar">
            <div class="bar-labels">
              <span>0</span><span>{{ formatPrice(detailStore.house.market_price) }}</span><span>{{ formatPrice(maxBarPrice) }}</span>
            </div>
            <div class="bar-track">
              <div class="bar-fill market-fill" :style="{ width: marketBarPct + '%' }"></div>
              <div class="bar-fill current-fill" :style="{ width: currentBarPct + '%' }" :class="detailStore.house.is_price_reasonable ? 'bar-ok' : 'bar-high'"></div>
              <div class="bar-marker" :style="{ left: marketBarPct + '%' }" title="市场均价"></div>
              <div class="bar-marker current-marker" :style="{ left: currentBarPct + '%' }" title="本房源"></div>
            </div>
            <div class="bar-caption">本房源 vs {{ detailStore.house.community || detailStore.house.district }}市场均价</div>
          </div>
        </div>
      </div>

      <!-- Price History Chart -->
      <div class="section" v-if="detailStore.priceHistory.length > 0">
        <h3 class="section-title">价格走势</h3>
        <PriceHistoryChart
          :data="detailStore.priceHistory"
          :market-price="detailStore.house.market_price"
        />
      </div>

      <!-- Sunlight + Noise side by side -->
      <div class="section">
        <h3 class="section-title">居住环境分析</h3>
        <div class="metric-cards">
          <SunlightCard
            v-if="detailStore.house.sunlight"
            :sunlight="detailStore.house.sunlight"
            :orientation="detailStore.house.orientation"
            :floor="detailStore.house.floor"
            :total-floors="detailStore.house.total_floors"
            :window-type="detailStore.house.window_type"
          />
          <NoiseCard
            v-if="detailStore.house.noise"
            :noise="detailStore.house.noise"
            :building-type="detailStore.house.building_type"
            :building-year="detailStore.house.building_year"
            :floor="detailStore.house.floor"
            :total-floors="detailStore.house.total_floors"
            :distance-to-street="detailStore.house.distance_to_street"
            :has-business-below="detailStore.house.has_business_below"
          />
        </div>
      </div>

      <!-- 评论风险分析 -->
      <div class="section">
        <h3 class="section-title">评论风险分析</h3>
        <AssessmentReport
          :assessment="detailStore.assessment"
          :loading="detailStore.loading.assessment"
        />
      </div>

      <!-- 补充评价 -->
      <div class="section">
        <h3 class="section-title">补充评价</h3>
        <div class="review-add-box">
          <textarea
            v-model="reviewContent"
            class="review-textarea"
            rows="4"
            placeholder="输入你的看房体验或租住感受，补充评价后风险分析会自动更新…"
            :disabled="reviewSubmitting"
          ></textarea>
          <div class="review-add-footer">
            <div v-if="reviewError" class="review-msg review-msg-error">{{ reviewError }}</div>
            <div v-else-if="reviewSuccess" class="review-msg review-msg-success">评价已添加，分析已更新</div>
            <div v-else class="review-msg"></div>
            <button
              class="btn-add-review"
              :disabled="reviewSubmitting || !reviewContent.trim()"
              @click="handleAddReview"
            >
              <span v-if="reviewSubmitting" class="spinner-inline"></span>
              {{ reviewSubmitting ? '提交中…' : '提交评价' }}
            </button>
          </div>
        </div>
      </div>

      <!-- AI Analysis Sections -->
      <template v-if="detailStore.loading.ai">
        <div class="loading">
          <Spinner text="AI 分析中，请稍候..." />
        </div>
      </template>
      <template v-else>
        <div class="section" v-if="detailStore.reviewMining">
          <h3 class="section-title">评论挖掘</h3>
          <ReviewMiningCard
            :review-data="detailStore.reviewMining"
            :reviews="detailStore.reviews"
          />
        </div>

        <div class="section" v-if="detailStore.landlordRisk">
          <h3 class="section-title">房东风险评估</h3>
          <LandlordRiskCard
            :landlord-risk="detailStore.landlordRisk"
            :house="detailStore.house"
          />
        </div>

        <div class="section" v-if="detailStore.finalAdvice">
          <h3 class="section-title">最终建议</h3>
          <AdvicePanel :advice="detailStore.finalAdvice" />
        </div>
      </template>
    </template>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useDetailStore } from '../stores/detail.js'
import ImageGallery from '../components/house/ImageGallery.vue'
import HouseInfoTable from '../components/house/HouseInfoTable.vue'
import SunlightCard from '../components/analysis/SunlightCard.vue'
import NoiseCard from '../components/analysis/NoiseCard.vue'
import ReviewMiningCard from '../components/analysis/ReviewMiningCard.vue'
import LandlordRiskCard from '../components/analysis/LandlordRiskCard.vue'
import AdvicePanel from '../components/analysis/AdvicePanel.vue'
import AssessmentReport from '../components/analysis/AssessmentReport.vue'
import HouseMap from '../components/map/HouseMap.vue'
import PriceHistoryChart from '../components/house/PriceHistoryChart.vue'
import Spinner from '../components/ui/Spinner.vue'
import { useFavoriteStore } from '../stores/favorites.js'
import { useHouseStore } from '../stores/house.js'

const props = defineProps({
  id: { type: [String, Number], required: true },
})

const router = useRouter()
const detailStore = useDetailStore()
const favStore = useFavoriteStore()
const houseStore = useHouseStore()

// ── 补充评价 ──
const reviewContent = ref('')
const reviewSubmitting = ref(false)
const reviewError = ref('')
const reviewSuccess = ref(false)

async function handleAddReview() {
  const text = reviewContent.value.trim()
  if (!text) return
  reviewError.value = ''
  reviewSuccess.value = false
  reviewSubmitting.value = true
  try {
    await detailStore.addReviewAndRefresh(props.id, text)
    reviewContent.value = ''
    reviewSuccess.value = true
    setTimeout(() => { reviewSuccess.value = false }, 3000)
  } catch (err) {
    reviewError.value = err?.response?.data?.detail || err.message || '提交失败'
  } finally {
    reviewSubmitting.value = false
  }
}

onMounted(() => {
  detailStore.load(props.id)
  favStore.checkStatus(Number(props.id))
})

onBeforeUnmount(() => {
  detailStore.clear()
})

function goBack() {
  router.push('/search')
}

// ── Price analysis computed ──
const maxBarPrice = computed(() => {
  const h = detailStore.house
  if (!h) return 8000
  const mp = h.market_price || 0
  const p = h.price || 0
  return Math.max(mp, p) * 1.3
})
const marketBarPct = computed(() => {
  const h = detailStore.house
  if (!h || !maxBarPrice.value) return 50
  return ((h.market_price || 0) / maxBarPrice.value) * 100
})
const currentBarPct = computed(() => {
  const h = detailStore.house
  if (!h || !maxBarPrice.value) return 50
  return ((h.price || 0) / maxBarPrice.value) * 100
})
const priceDevText = computed(() => {
  const h = detailStore.house
  if (!h || h.price_deviation == null) return '--'
  const pct = Math.round(h.price_deviation * 100)
  return pct > 0 ? `+${pct}%` : `${pct}%`
})
const priceDevClass = computed(() => {
  const h = detailStore.house
  if (!h || h.price_deviation == null) return ''
  return h.is_price_reasonable ? 'reasonable' : 'unreasonable'
})

function formatPrice(price) {
  if (!price) return '--'
  const num = Number(price)
  return isNaN(num) ? price : num.toLocaleString('zh-CN')
}

// ── Commute computed ──
const commuteLevel = computed(() => {
  const d = detailStore.house?.commute_duration
  if (d == null) return 'unknown'
  if (d <= 30) return 'good'
  if (d <= 60) return 'ok'
  return 'bad'
})
const commuteLabel = computed(() => {
  const d = detailStore.house?.commute_duration
  if (d == null) return '未计算'
  if (d <= 30) return '通勤便利'
  if (d <= 60) return '通勤适中'
  return '通勤较远'
})

function goToSearch() {
  router.push('/search')
}

async function handleFavorite() {
  await favStore.toggle(Number(props.id))
}
</script>

<style scoped>
.detail-page { padding: 0; }
.detail-skeleton { padding: 0; }

/* Price Analysis Section */
.price-section { background: #fff; border-radius: var(--radius); padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.04); }
.price-summary-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
.price-metric { text-align: center; }
.price-metric-label { display: block; font-size: 12px; color: var(--text-muted); margin-bottom: 4px; }
.price-metric-value { font-size: 20px; font-weight: 700; color: var(--text); }
.price-metric-value small { font-size: 12px; font-weight: 400; color: var(--text-secondary); }
.price-metric-value.market { color: var(--text-secondary); }
.price-metric-value.reasonable { color: #16A34A; }
.price-metric-value.unreasonable { color: var(--danger); }
.price-comparison-bar { margin-top: 8px; }
.bar-labels { display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted); margin-bottom: 6px; }
.bar-track { position: relative; height: 24px; background: #F3F4F6; border-radius: 12px; overflow: hidden; }
.bar-fill { position: absolute; top: 0; left: 0; height: 100%; border-radius: 12px; transition: width .4s ease; }
.market-fill { background: rgba(156,163,175,0.4); z-index: 1; }
.current-fill { z-index: 2; opacity: 0.7; }
.current-fill.bar-ok { background: var(--primary); }
.current-fill.bar-high { background: var(--danger); }
.bar-marker { position: absolute; top: 0; width: 3px; height: 100%; background: var(--text-secondary); z-index: 3; transition: left .4s ease; }
.bar-marker.current-marker { background: var(--text); width: 3px; }
.bar-caption { text-align: center; font-size: 12px; color: var(--text-muted); margin-top: 8px; }

@media (max-width: 768px) {
  .price-summary-cards { grid-template-columns: repeat(2, 1fr); }
}

/* Commute Card */
.commute-card {
  background: #fff; border-radius: var(--radius); padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  display: flex; gap: 24px; align-items: center; flex-wrap: wrap;
}
.commute-card.muted { background: #FAFAFA; justify-content: center; text-align: center; }
.commute-card.muted p { margin: 0; font-size: 14px; color: var(--text-secondary); line-height: 1.8; }
.commute-metric { text-align: center; }
.commute-metric.primary { min-width: 120px; }
.commute-label { display: block; font-size: 12px; color: var(--text-muted); margin-bottom: 4px; }
.commute-value { font-size: 28px; font-weight: 800; color: var(--text); }
.commute-value small { font-size: 14px; font-weight: 400; color: var(--text-secondary); }
.commute-value.good { color: #16A34A; }
.commute-value.ok { color: var(--primary); }
.commute-value.bad { color: var(--danger); }
.commute-badge {
  padding: 6px 16px; border-radius: var(--radius-full);
  font-size: 13px; font-weight: 600;
}
.commute-badge.good { background: #DCFCE7; color: #166534; }
.commute-badge.ok { background: #FEF3C7; color: #92400E; }
.commute-badge.bad { background: #FEE2E2; color: #991B1B; }
.commute-set-btn {
  margin-top: 10px; padding: 8px 20px; border: none;
  border-radius: var(--radius-full); background: var(--primary-gradient);
  color: #fff; font-size: 13px; font-weight: 600; cursor: pointer;
  transition: transform .15s;
}
.commute-set-btn:hover { transform: scale(1.03); }

/* ── 补充评价 ── */
.review-add-box {
  background: #fff; border-radius: var(--radius); padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.review-textarea {
  width: 100%; padding: 12px 14px; border: 1.5px solid var(--border-strong);
  border-radius: var(--radius-xs); font-size: 14px; outline: none;
  background: #fff; color: var(--text); font-family: inherit;
  resize: vertical; min-height: 80px; line-height: 1.7;
  transition: border-color .2s, box-shadow .2s;
  box-sizing: border-box;
}
.review-textarea:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(245,158,11,0.1);
}
.review-textarea:disabled { background: #F9FAFB; }
.review-textarea::placeholder { color: var(--text-muted); font-size: 13px; }

.review-add-footer {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 12px; gap: 12px;
}
.review-msg { font-size: 13px; flex: 1; }
.review-msg-error { color: #991B1B; }
.review-msg-success { color: #065F46; }

.btn-add-review {
  padding: 10px 28px; border: none; border-radius: var(--radius-sm);
  background: var(--primary-gradient); color: #fff;
  font-size: 14px; font-weight: 700; cursor: pointer;
  transition: transform .15s, box-shadow .2s;
  white-space: nowrap; flex-shrink: 0;
}
.btn-add-review:hover:not(:disabled) { transform: scale(1.02); box-shadow: 0 4px 16px rgba(245,158,11,0.35); }
.btn-add-review:disabled { opacity: 0.6; cursor: not-allowed; }

.spinner-inline {
  display: inline-block; width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff; border-radius: 50%;
  animation: rspin .6s linear infinite;
  margin-right: 6px; vertical-align: middle;
}
@keyframes rspin { to { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .detail-header h2 { font-size: 20px; }
}
</style>
