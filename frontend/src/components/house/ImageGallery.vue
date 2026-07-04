<template>
  <div class="image-gallery">
    <!-- Main Image -->
    <div class="image-gallery-main">
      <img
        v-if="currentImageUrl"
        :src="currentImageUrl"
        :alt="community"
      />
      <div v-else class="image-gallery-placeholder">
        <span>&#x1F3E0;</span>
        <p>暂无图片</p>
      </div>
    </div>

    <!-- Thumbnail Row -->
    <div v-if="resolvedImages.length > 1" class="image-gallery-thumbs">
      <img
        v-for="(image, index) in resolvedImages"
        :key="index"
        :src="getImageUrl(image)"
        :class="['image-gallery-thumb', { active: index === activeIndex }]"
        :alt="`${community} 图片 ${index + 1}`"
        @click="activeIndex = index"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  images: { type: Array, default: () => [] },
  community: { type: String, default: '' },
})

const activeIndex = ref(0)

const resolvedImages = computed(() => {
  if (!props.images || !Array.isArray(props.images)) return []
  return props.images
})

const currentImageUrl = computed(() => {
  if (resolvedImages.value.length === 0) return null
  const image = resolvedImages.value[activeIndex.value]
  return getImageUrl(image)
})

function getImageUrl(image) {
  if (!image) return ''
  const raw = typeof image === 'string' ? image : image.url || image.path || ''
  if (!raw) return ''

  // In production, use the path directly; in dev, prefix with /api/v1/images/
  if (import.meta.env.PROD) {
    return raw
  }
  // If path starts with http, it's already a full URL
  if (raw.startsWith('http://') || raw.startsWith('https://')) {
    return raw
  }
  // Prepend /api/v1/images/ for local dev paths
  return `/api/v1/images/${raw.replace(/^\//, '')}`
}
</script>

<style scoped>
.image-gallery {
  margin-bottom: 24px;
}

.image-gallery-main {
  border-radius: var(--radius);
  overflow: hidden;
  margin-bottom: 10px;
  max-height: 420px;
  background: #f0f2f5;
}

.image-gallery-main img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.image-gallery-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: var(--text-secondary);
  font-size: 15px;
}

.image-gallery-placeholder span {
  font-size: 48px;
  margin-bottom: 8px;
}

.image-gallery-thumbs {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.image-gallery-thumb {
  width: 80px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color 0.2s, opacity 0.2s;
  flex-shrink: 0;
  opacity: 0.6;
}

.image-gallery-thumb:hover,
.image-gallery-thumb.active {
  border-color: var(--accent);
  opacity: 1;
}
</style>
