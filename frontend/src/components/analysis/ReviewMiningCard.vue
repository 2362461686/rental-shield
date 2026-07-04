<template>
  <div class="review-mining-card">
    <!-- 6 Dimension Grid -->
    <div class="dimension-grid">
      <div
        v-for="dim in dimensions"
        :key="dim.key"
        class="dimension-section"
      >
        <h4 class="dimension-title">{{ dim.label }}</h4>
        <div v-if="dim.data" class="tag-cloud">
          <span
            v-for="tag in dim.data.positive_tags"
            :key="'pos-' + tag"
            class="tag-pos"
          >{{ tag }}</span>
          <span
            v-for="tag in dim.data.negative_tags"
            :key="'neg-' + tag"
            class="tag-neg"
          >{{ tag }}</span>
        </div>
        <p v-else class="dimension-empty">暂无数据</p>
      </div>
    </div>

    <!-- Expandable Reviews Section -->
    <button class="detail-btn review-toggle" @click="showReviews = !showReviews">
      {{ showReviews ? '收起评论' : `查看全部 ${reviews.length} 条评论` }}
    </button>

    <Transition name="expand">
      <div v-if="showReviews" class="reviews-list">
        <div
          v-for="(review, index) in reviews"
          :key="index"
          class="review-item"
        >
          <div class="review-header">
            <span class="review-platform">{{ review.platform || '未知平台' }}</span>
            <span class="review-rating">{{ '&#x2B50;'.repeat(review.rating || 0) }}{{ review.rating || '--' }}</span>
          </div>
          <p class="review-text">{{ review.content || review.text || '--' }}</p>
        </div>
        <p v-if="reviews.length === 0" class="empty-state" style="padding:20px;">暂无评论数据</p>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  reviewData: { type: Object, default: () => ({}) },
  reviews: { type: Array, default: () => [] },
})

const showReviews = ref(false)

const dimensionKeys = [
  { key: 'soundproof', label: '隔音' },
  { key: 'lighting', label: '采光' },
  { key: 'landlord', label: '房东' },
  { key: 'utilities', label: '水电' },
  { key: 'transportation', label: '交通' },
  { key: 'safety', label: '安全' },
]

const dimensions = computed(() => {
  return dimensionKeys.map((dim) => ({
    ...dim,
    data: getDimensionData(dim.key),
  }))
})

function getDimensionData(key) {
  const data = props.reviewData

  if (!data || data.state === 'rejected') return null

  // Support multiple possible structures:
  // 1. { soundproof: { positive_tags: [], negative_tags: [] } }
  // 2. { dimensions: { soundproof: ... } }
  // 3. data[key] object with positive_tags/negative_tags
  const dim = data[key] || data?.dimensions?.[key] || null
  if (dim) {
    // Validate it has the expected shape
    if (dim.positive_tags || dim.negative_tags) return dim
  }

  // Fallback: if reviewData itself is a dimension object
  if (data && typeof data === 'object') {
    if (data.positive_tags || data.negative_tags) return data
  }

  return null
}


</script>

<style scoped>
.review-mining-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow);
}

.dimension-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.dimension-section {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 14px;
  border: 1px solid var(--border);
}

.dimension-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 8px;
}

.dimension-empty {
  font-size: 12px;
  color: var(--text-secondary);
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-pos {
  background: #d4edda;
  color: #155724;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.tag-neg {
  background: #f8d7da;
  color: #721c24;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.review-toggle {
  display: block;
  margin: 0 auto 12px;
  text-align: center;
}

.reviews-list {
  max-height: 400px;
  overflow-y: auto;
  border-top: 1px solid var(--border);
  padding-top: 12px;
}

.review-item {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 14px;
  margin-bottom: 8px;
}

.review-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

.review-platform {
  font-weight: 600;
}

.review-rating {
  color: #f39c12;
}

.review-text {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text);
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
  max-height: 600px;
}
</style>
