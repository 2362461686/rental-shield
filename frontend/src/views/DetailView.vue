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

      <!-- Price Card (inline, market comparison) -->
      <div class="section" v-if="detailStore.house">
        <h3 class="section-title">价格分析</h3>
        <div class="metric-card price-card">
          <h3>月租金</h3>
          <div class="value" style="color: var(--danger);">{{ detailStore.house.price }}<span style="font-size:16px;">元/月</span></div>
          <p style="color:var(--text-secondary);font-size:13px;">
            {{ detailStore.house.community }}小区均价：{{ detailStore.house.avg_price ?? '--' }}元/月
          </p>
        </div>
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
import { onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useDetailStore } from '../stores/detail.js'
import ImageGallery from '../components/house/ImageGallery.vue'
import HouseInfoTable from '../components/house/HouseInfoTable.vue'
import SunlightCard from '../components/analysis/SunlightCard.vue'
import NoiseCard from '../components/analysis/NoiseCard.vue'
import ReviewMiningCard from '../components/analysis/ReviewMiningCard.vue'
import LandlordRiskCard from '../components/analysis/LandlordRiskCard.vue'
import AdvicePanel from '../components/analysis/AdvicePanel.vue'
import Spinner from '../components/ui/Spinner.vue'

const props = defineProps({
  id: { type: [String, Number], required: true },
})

const router = useRouter()
const detailStore = useDetailStore()

onMounted(() => {
  detailStore.load(props.id)
})

onBeforeUnmount(() => {
  detailStore.clear()
})

function goBack() {
  router.push('/search')
}

function formatPrice(price) {
  if (!price) return '--'
  const num = Number(price)
  return isNaN(num) ? price : num.toLocaleString('zh-CN')
}
</script>

<style scoped>
.detail-page {
  padding: 0;
}

.detail-skeleton {
  padding: 0;
}

.detail-header {
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  color: #fff;
  padding: 32px;
  border-radius: var(--radius);
  margin-bottom: 24px;
  position: relative;
}

.detail-header h2 {
  font-size: 26px;
  margin-bottom: 12px;
}

.detail-breadcrumb {
  margin-bottom: 16px;
}

.detail-breadcrumb button {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  border: none;
  padding: 8px 18px;
  border-radius: 20px;
  font-size: 14px;
  transition: background 0.2s;
  cursor: pointer;
}

.detail-breadcrumb button:hover {
  background: rgba(255, 255, 255, 0.35);
}

.detail-header-meta {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
  font-size: 14px;
  opacity: 0.9;
}

.detail-header-price {
  font-size: 22px;
  font-weight: 800;
  margin-right: 8px;
  opacity: 1;
}

.price-card {
  max-width: 400px;
}

@media (max-width: 768px) {
  .detail-header {
    padding: 20px;
  }

  .detail-header h2 {
    font-size: 20px;
  }
}
</style>
