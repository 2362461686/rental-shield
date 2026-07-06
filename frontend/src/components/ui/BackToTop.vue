<template>
  <button
    v-show="visible"
    class="back-to-top"
    @click="scrollToTop"
    title="回到顶部"
  >
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="18 15 12 9 6 15"></polyline>
    </svg>
  </button>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const visible = ref(false)

function handleScroll() {
  visible.value = window.scrollY > 400
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.back-to-top {
  position: fixed; bottom: 28px; right: 28px; z-index: 1000;
  width: 44px; height: 44px; border-radius: 50%;
  background: #fff; border: 1.5px solid var(--border-strong);
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  cursor: pointer; display: flex; align-items: center;
  justify-content: center; color: var(--text-secondary);
  transition: all .2s; padding: 0;
}
.back-to-top:hover {
  border-color: var(--primary); color: var(--primary);
  box-shadow: 0 4px 16px rgba(245,158,11,0.2);
  transform: translateY(-2px);
}
</style>
