<template>
  <div class="empty-state">
    <div class="icon">{{ icon }}</div>
    <h3>{{ title }}</h3>
    <p v-if="description">{{ description }}</p>
  </div>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '&#x1F50D;' },
  title: { type: String, default: '暂无数据' },
  description: { type: String, default: '' },
})
</script>

<style scoped>
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 8px;
}

.empty-state p {
  font-size: 14px;
  max-width: 400px;
  margin: 0 auto;
  line-height: 1.6;
}
</style>
