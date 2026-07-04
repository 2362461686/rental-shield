<template>
  <div class="home-view">
    <!-- Hero Section -->
    <section class="hero">
      <h1>🏠 应届生租房防坑决策引擎</h1>
      <p>基于 AI 和物理模拟的智能租房分析，帮你避开黑中介和问题房源</p>
      <form class="hero-search" @submit.prevent="handleSearch">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="输入小区名称或地址开始搜索..."
        />
        <button type="submit">开始分析</button>
      </form>
    </section>

    <!-- Feature Cards -->
    <section class="features">
      <div class="feature-card">
        <div class="feature-icon">🤖</div>
        <h3>AI分析</h3>
        <p>智能分析房源评论，识别房东套路与潜在风险点</p>
        <router-link to="/search">了解更多 &rarr;</router-link>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🔬</div>
        <h3>物理模拟</h3>
        <p>日照采光与隔音效果的真实物理仿真分析</p>
        <router-link to="/search">了解更多 &rarr;</router-link>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🕵️</div>
        <h3>房东画像</h3>
        <p>基于历史数据的房东风险评估与信用画像</p>
        <router-link to="/search">了解更多 &rarr;</router-link>
      </div>
      <div class="feature-card">
        <div class="feature-icon">📊</div>
        <h3>综合决策</h3>
        <p>多维数据融合，给出客观理性的租房决策建议</p>
        <router-link to="/search">了解更多 &rarr;</router-link>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const searchQuery = ref('')

function handleSearch() {
  const query = searchQuery.value.trim()
  router.push({ path: '/search', query: query ? { q: query } : {} })
}
</script>

<style scoped>
.home-view {
  margin: -24px -20px;
}

.feature-card a {
  display: inline-block;
  margin-top: 10px;
  font-size: 13px;
  font-weight: 600;
}
</style>
