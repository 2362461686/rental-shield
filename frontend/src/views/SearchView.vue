<template>
  <div class="search-view">
    <div class="search-layout">
      <aside class="search-sidebar">
        <SearchPanel @search="handleSearch" />
      </aside>
      <section class="search-main">
        <div v-if="!houseStore.searched && !houseStore.loading" class="empty-state">
          <div class="icon">🔍</div>
          <p>请设置筛选条件后点击"搜索"按钮</p>
          <p style="font-size:13px;margin-top:8px">选择区域、户型、价格范围，开始精准找房</p>
        </div>
        <div v-if="houseStore.loading" class="loading">
          <div class="skeleton" style="width:100%;height:150px;margin-bottom:16px"></div>
          <div class="skeleton" style="width:100%;height:150px;margin-bottom:16px"></div>
          <div class="skeleton" style="width:100%;height:150px;margin-bottom:16px"></div>
          <p style="margin-top:12px">正在搜索中...</p>
        </div>
        <template v-if="houseStore.searched && !houseStore.loading">
          <div v-if="houseStore.houses.length === 0" class="empty-state">
            <div class="icon">😔</div>
            <p>没有找到匹配的房源</p>
            <p style="font-size:13px;margin-top:8px">试试调整筛选条件</p>
          </div>
          <div v-else>
            <p class="results-count">共找到 <strong>{{ houseStore.houses.length }}</strong> 套房源</p>
            <HouseCard v-for="h in houseStore.houses" :key="h.id" :house="h" />
          </div>
        </template>
      </section>
    </div>
  </div>
</template>

<script setup>
import { useHouseStore } from '../stores/house.js'
import SearchPanel from '../components/search/SearchPanel.vue'
import HouseCard from '../components/house/HouseCard.vue'

const houseStore = useHouseStore()

function handleSearch() {
  houseStore.search()
}
</script>

<style scoped>
.search-view{margin:-24px -20px;padding:24px 20px}
.search-layout{display:flex;gap:24px;align-items:flex-start}
.search-sidebar{width:280px;flex-shrink:0;position:sticky;top:84px}
.search-main{flex:1;min-width:0}
.results-count{font-size:14px;color:var(--text-secondary);margin-bottom:16px}
.results-count strong{color:var(--text);font-weight:700}
@media(max-width:768px){.search-layout{flex-direction:column}.search-sidebar{width:100%;position:static}}
</style>
