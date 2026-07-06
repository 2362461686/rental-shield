<template>
  <div v-if="hasError" class="error-boundary">
    <div class="error-boundary-content">
      <div class="error-icon">&#x26A0;&#xFE0F;</div>
      <h2>页面出了点问题</h2>
      <p>{{ errorMessage || '组件渲染异常，请尝试刷新页面' }}</p>
      <div class="error-actions">
        <button class="eb-btn refresh" @click="handleRefresh">刷新页面</button>
        <router-link to="/" class="eb-btn home">返回首页</router-link>
      </div>
    </div>
  </div>
  <slot v-else></slot>
</template>

<script setup>
import { ref, onErrorCaptured } from 'vue'

const hasError = ref(false)
const errorMessage = ref('')

onErrorCaptured((err, instance, info) => {
  console.error('ErrorBoundary caught:', err.message, info)
  hasError.value = true
  errorMessage.value = err.message || '未知错误'
  return false // prevent error propagation
})

function handleRefresh() {
  window.location.reload()
}
</script>

<style scoped>
.error-boundary {
  display: flex; align-items: center; justify-content: center;
  min-height: 400px; padding: 40px 20px;
}
.error-boundary-content {
  text-align: center; max-width: 420px;
}
.error-icon { font-size: 56px; margin-bottom: 16px; }
.error-boundary-content h2 {
  font-size: 22px; font-weight: 700; color: var(--text);
  margin-bottom: 8px;
}
.error-boundary-content p {
  font-size: 14px; color: var(--text-secondary);
  margin-bottom: 24px; line-height: 1.6;
}
.error-actions { display: flex; gap: 12px; justify-content: center; }
.eb-btn {
  padding: 10px 24px; border-radius: var(--radius-full);
  font-size: 14px; font-weight: 600; cursor: pointer;
  border: none; text-decoration: none; display: inline-block;
}
.eb-btn.refresh {
  background: var(--primary); color: #fff;
}
.eb-btn.refresh:hover { opacity: 0.9; }
.eb-btn.home {
  background: #fff; color: var(--text);
  border: 1.5px solid var(--border-strong);
}
.eb-btn.home:hover { border-color: var(--primary); color: var(--primary); }
</style>
