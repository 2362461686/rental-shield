<template>
  <div class="search-view">
    <div class="search-layout">
      <aside class="search-sidebar">
        <SearchPanel @search="handleSearch" />
        <!-- Workspace config -->
        <div class="workspace-bar">
          <button v-if="houseStore.workspace.configured" class="workspace-btn configured" @click="showWorkspaceModal = true">
            &#x1F3E2; 通勤: {{ houseStore.workspace.name }}
          </button>
          <button v-else class="workspace-btn" @click="showWorkspaceModal = true">
            &#x1F4CD; 设置通勤地点
          </button>
          <button v-if="houseStore.workspace.configured" class="workspace-clear" @click="houseStore.clearWorkspace()" title="清除">&#x2716;</button>
        </div>
      </aside>
      <section class="search-main">
        <!-- View toggle -->
        <div class="view-toggle" v-if="houseStore.searched && !houseStore.loading">
          <button :class="{ active: viewMode === 'list' }" @click="viewMode = 'list'">&#x1F4CB; 列表</button>
          <button :class="{ active: viewMode === 'map' }" @click="viewMode = 'map'">&#x1F5FA; 地图</button>
        </div>

        <!-- District comparison bar (when no specific filters applied) -->
        <DistrictComparisonBar
          v-if="!hasFilters && houseStore.searched"
          @select-district="selectDistrict"
        />

        <!-- Map mode -->
        <template v-if="viewMode === 'map' && houseStore.searched && !houseStore.loading">
          <div v-if="houseStore.houses.length === 0" class="empty-state">
            <p>没有找到匹配的房源</p>
          </div>
          <HouseMap
            v-else
            mode="houses"
            :houses="houseStore.houses"
            :workplace="houseStore.workspace"
            :commute-cache="houseStore.commuteCache"
            :show-commute-routes="houseStore.workspace.configured"
            :show-subway="!!houseStore.selectedSubwayLine"
            :subway-line="houseStore.selectedSubwayLine"
            @house-click="navigateToDetail"
          />
        </template>

        <!-- List mode -->
        <template v-if="viewMode === 'list'">
          <div v-if="!houseStore.searched && !houseStore.loading" class="empty-state">
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
              <p>没有找到匹配的房源</p>
              <p style="font-size:13px;margin-top:8px">试试调整筛选条件</p>
            </div>
            <div v-else>
              <p class="results-count">共找到 <strong>{{ houseStore.houses.length }}</strong> 套房源</p>
              <HouseCard v-for="h in houseStore.houses" :key="h.id" :house="h" />
            </div>
          </template>
        </template>
      </section>
    </div>

    <WorkspaceModal v-if="showWorkspaceModal" @close="showWorkspaceModal = false" @save="onWorkspaceSaved" />
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useHouseStore } from '../stores/house.js'
import SearchPanel from '../components/search/SearchPanel.vue'
import HouseCard from '../components/house/HouseCard.vue'
import HouseMap from '../components/map/HouseMap.vue'
import DistrictComparisonBar from '../components/search/DistrictComparisonBar.vue'
import WorkspaceModal from '../components/search/WorkspaceModal.vue'

const route = useRoute()
const router = useRouter()
const houseStore = useHouseStore()

const viewMode = ref('list')
const showWorkspaceModal = ref(false)

const hasFilters = computed(() => {
  const f = houseStore.filters
  return f.districts.length > 0 || f.layout || f.minPrice > 0 || f.maxPrice < 8000 || f.keyword
})

onMounted(() => {
  const qDistricts = route.query.districts
  if (qDistricts) {
    const districts = typeof qDistricts === 'string'
      ? qDistricts.split(',').map(d => d.trim()).filter(Boolean)
      : qDistricts
    if (districts.length > 0) {
      houseStore.updateFilter('districts', districts)
      houseStore.search()
    }
  }
})

function handleSearch() {
  houseStore.search()
}

function selectDistrict(district) {
  houseStore.updateFilter('districts', [district])
  houseStore.search()
}

function navigateToDetail(data) {
  const houseId = data.id != null ? data.id : data
  router.push(`/house/${houseId}`)
}

function onWorkspaceSaved() {
  showWorkspaceModal.value = false
}
</script>

<style scoped>
.search-view{margin:-24px -20px;padding:24px 20px}
.search-layout{display:flex;gap:24px;align-items:flex-start}
.search-sidebar{width:280px;flex-shrink:0;position:sticky;top:84px}
.search-main{flex:1;min-width:0}
@media(max-width:768px){.search-layout{flex-direction:column}.search-sidebar{width:100%;position:static}}
</style>
