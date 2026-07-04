<template>
  <div class="house-card" @click="goDetail">
    <!-- Left: thumbnail image -->
    <img
      v-if="house.primary_image_url"
      :src="`/images/${house.primary_image_url}`"
      :alt="house.title"
      class="house-card-img"
      @error="onImgError"
    />
    <div v-else class="house-card-img">
      🏠
    </div>

    <!-- Right: card body -->
    <div class="house-card-body">
      <!-- Main info -->
      <div class="house-card-info">
        <h3 class="house-card-title">{{ house.title }}</h3>
        <p class="house-card-meta">{{ house.district }} · {{ house.community }}</p>
        <p class="house-card-meta">
          {{ house.layout }} · {{ house.area }}m²
        </p>

        <!-- Stats: sunlight & noise -->
        <div class="house-card-stats">
          <span v-if="house.sunlight_level" class="house-card-stat">
            ☀️ 采光 {{ house.sunlight_level }}
          </span>
          <span v-if="house.noise_level" class="house-card-stat">
            🔊 隔音 {{ house.noise_level }}
          </span>
        </div>
      </div>

      <!-- Right column: price & risk -->
      <div class="house-card-right">
        <div>
          <span class="house-card-price">{{ house.price }}</span>
          <span class="house-card-price-unit"> 元/月</span>
        </div>

        <!-- Risk badge -->
        <span v-if="house.risk_level" :class="riskBadgeClass" class="badge">
          {{ riskLabel }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  house: {
    type: Object,
    required: true,
  },
})

const router = useRouter()

const riskBadgeClass = computed(() => {
  const level = props.house.risk_level
  if (!level) return ''
  if (level === '低' || level === 'low') return 'badge-green'
  if (level === '中' || level === 'medium') return 'badge-yellow'
  if (level === '高' || level === 'high') return 'badge-red'
  return ''
})

const riskLabel = computed(() => {
  const level = props.house.risk_level
  if (!level) return ''
  if (level === '低' || level === 'low') return '低风险'
  if (level === '中' || level === 'medium') return '中风险'
  if (level === '高' || level === 'high') return '高风险'
  return level
})

function goDetail() {
  router.push(`/house/${props.house.id}`)
}

function onImgError(e) {
  e.target.style.display = 'none'
}
</script>
