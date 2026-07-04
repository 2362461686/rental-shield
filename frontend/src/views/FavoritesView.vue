<template>
  <div class="favorites-view">
    <h2>我的收藏</h2>
    <div v-if="favStore.loading" class="loading">
      <p>加载中...</p>
    </div>
    <div v-else-if="favStore.favorites.length === 0" class="empty-state">
      <div class="icon">&#x2B50;</div>
      <p>还没有收藏的房源</p>
      <p style="font-size:13px;margin-top:8px">在搜索页面发现心仪房源，点击收藏按钮即可保存</p>
      <router-link to="/search" class="go-search-btn">去搜索房源</router-link>
    </div>
    <div v-else>
      <p class="results-count">共收藏 <strong>{{ favStore.favorites.length }}</strong> 套房源</p>
      <HouseCard
        v-for="fav in favStore.favorites"
        :key="fav.id"
        :house="fav.house"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useFavoriteStore } from '../stores/favorites.js'
import HouseCard from '../components/house/HouseCard.vue'

const favStore = useFavoriteStore()

onMounted(() => {
  favStore.loadFavorites()
})
</script>

<style scoped>
.favorites-view { padding: 0; }
.favorites-view h2 { font-size: 22px; margin-bottom: 20px; }
.results-count { font-size: 14px; color: var(--text-secondary); margin-bottom: 16px; }
.results-count strong { color: var(--text); font-weight: 700; }
.go-search-btn {
  display: inline-block; margin-top: 16px; padding: 10px 24px;
  background: var(--accent); color: #fff; border-radius: 8px;
  font-size: 14px; font-weight: 600; text-decoration: none;
}
</style>
