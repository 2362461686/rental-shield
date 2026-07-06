<template>
  <div class="favorites-view">
    <h2>我的收藏</h2>
    <Spinner v-if="favStore.loading" text="加载收藏列表..." />
    <EmptyState
      v-else-if="favStore.favorites.length === 0"
      icon="&#x2B50;"
      title="还没有收藏的房源"
      description="在搜索页面发现心仪房源，点击收藏按钮即可保存"
    >
      <router-link to="/search" class="go-search-btn">去搜索房源</router-link>
    </EmptyState>
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
import EmptyState from '../components/ui/EmptyState.vue'
import Spinner from '../components/ui/Spinner.vue'

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
