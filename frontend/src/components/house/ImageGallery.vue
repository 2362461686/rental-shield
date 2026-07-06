<template>
  <div class="image-gallery">
    <!-- Main Image -->
    <div class="image-gallery-main" :class="{ 'has-image': !!currentImageUrl }">
      <img
        v-if="currentImageUrl"
        :src="currentImageUrl"
        :alt="community"
        @error="handleImageError"
      />
      <div v-else class="image-gallery-placeholder" :style="{ background: gradientStyle }">
        <div class="placeholder-content">
          <div class="placeholder-icon">
            <svg viewBox="0 0 80 64" width="64" height="48" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="2" y="24" width="76" height="38" rx="3" fill="white" fill-opacity="0.3"/>
              <polygon points="40,2 2,24 78,24" fill="white" fill-opacity="0.35"/>
              <rect x="18" y="36" width="12" height="14" rx="1" fill="white" fill-opacity="0.25"/>
              <rect x="34" y="36" width="12" height="14" rx="1" fill="white" fill-opacity="0.2"/>
              <rect x="50" y="36" width="12" height="14" rx="1" fill="white" fill-opacity="0.25"/>
            </svg>
          </div>
          <p class="placeholder-community">{{ community || '房源图片' }}</p>
          <p class="placeholder-hint">点击下方模拟图查看不同角度</p>
        </div>
      </div>
    </div>

    <!-- Placeholder Thumbnails (when no real images) -->
    <div v-if="resolvedImages.length === 0 && community" class="image-gallery-thumbs placeholder-thumbs">
      <div
        v-for="(thumb, idx) in placeholderThumbs"
        :key="idx"
        :class="['image-gallery-thumb', 'placeholder-thumb', { active: idx === activePlaceholder }]"
        :style="{ background: thumb.bg }"
        @click="activePlaceholder = idx"
      >
        <span>{{ thumb.label }}</span>
      </div>
    </div>

    <!-- Real Thumbnail Row -->
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
const activePlaceholder = ref(0)
const imageErrors = ref(new Set())

const resolvedImages = computed(() => {
  if (!props.images || !Array.isArray(props.images)) return []
  return props.images.filter(img => {
    const path = typeof img === 'string' ? img : img.image_path || img.url || ''
    return path && !imageErrors.value.has(path)
  })
})

const currentImageUrl = computed(() => {
  if (resolvedImages.value.length === 0) return null
  const image = resolvedImages.value[activeIndex.value]
  return getImageUrl(image)
})

function handleImageError() {
  if (resolvedImages.value.length > 0) {
    const image = resolvedImages.value[activeIndex.value]
    const path = typeof image === 'string' ? image : image.image_path || image.url || ''
    if (path) imageErrors.value.add(path)
  }
}

// Generate gradient background from community name hash
const gradientHue = computed(() => {
  let hash = 0
  const str = props.community || 'default'
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash)
  }
  return Math.abs(hash) % 360
})

const gradientStyle = computed(() => {
  const h = gradientHue.value
  return `linear-gradient(135deg, hsl(${h}, 50%, 65%), hsl(${h}, 45%, 40%))`
})

const placeholderThumbs = computed(() => {
  const colors = [
    { label: '客厅', bg: 'linear-gradient(135deg, #6ee7b7, #3b82f6)' },
    { label: '卧室', bg: 'linear-gradient(135deg, #93c5fd, #6366f1)' },
    { label: '厨房', bg: 'linear-gradient(135deg, #fcd34d, #f59e0b)' },
    { label: '阳台', bg: 'linear-gradient(135deg, #a5f3fc, #06b6d4)' },
    { label: '卫浴', bg: 'linear-gradient(135deg, #c4b5fd, #8b5cf6)' },
  ]
  return colors
})

function getImageUrl(image) {
  if (!image) return ''
  const raw = typeof image === 'string' ? image : image.image_path || image.url || image.path || ''
  if (!raw) return ''
  const normalized = raw.replace(/\\/g, '/')
  const clean = normalized.replace(/^images\//, '')
  if (clean.startsWith('http://') || clean.startsWith('https://')) return clean
  return `/api/v1/images/${clean}`
}
</script>

<style scoped>
.image-gallery { margin-bottom: 24px; }
.image-gallery-main {
  border-radius: var(--radius); overflow: hidden; margin-bottom: 10px;
  max-height: 420px; background: #f0f2f5;
}
.image-gallery-main.has-image { max-height: 500px; }
.image-gallery-main img { width: 100%; height: 100%; object-fit: cover; display: block; }
.image-gallery-placeholder {
  display: flex; align-items: center; justify-content: center;
  height: 300px; color: rgba(255,255,255,0.85);
}
.placeholder-content { text-align: center; }
.placeholder-icon { margin-bottom: 12px; }
.placeholder-community {
  font-size: 22px; font-weight: 700; margin: 0 0 4px;
  text-shadow: 0 1px 3px rgba(0,0,0,0.15);
}
.placeholder-hint {
  font-size: 12px; opacity: 0.7; margin: 6px 0 0;
}
.image-gallery-thumbs { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 4px; }
.image-gallery-thumb {
  width: 80px; height: 60px; border-radius: 8px; object-fit: cover;
  cursor: pointer; border: 2px solid transparent;
  transition: border-color .2s, opacity .2s; flex-shrink: 0; opacity: 0.6;
}
.image-gallery-thumb:hover, .image-gallery-thumb.active {
  border-color: var(--primary); opacity: 1;
}
.placeholder-thumb {
  display: flex; align-items: center; justify-content: center;
}
.placeholder-thumb span {
  color: rgba(255,255,255,0.9); font-size: 12px; font-weight: 600;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}
@media (max-width: 768px) {
  .image-gallery-placeholder { height: 220px; }
  .placeholder-community { font-size: 18px; }
}
</style>
