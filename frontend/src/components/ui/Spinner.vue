<template>
  <div class="spinner-wrapper">
    <div class="spinner"></div>
    <p v-if="text" class="spinner-text">{{ text }}</p>
  </div>
</template>

<script setup>
defineProps({
  text: { type: String, default: '加载中...' },
})
</script>

<style scoped>
.spinner-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.spinner-text {
  margin-top: 14px;
  font-size: 14px;
  color: var(--text-secondary);
}
</style>
