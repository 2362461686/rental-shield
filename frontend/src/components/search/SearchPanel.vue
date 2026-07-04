<template>
  <div class="search-panel">
    <h3>筛选条件</h3>

    <!-- Keyword search -->
    <div class="filter-group">
      <label>关键词</label>
      <input
        v-model="localFilters.keyword"
        type="text"
        class="filter-input"
        placeholder="搜索小区名、标题..."
        @keyup.enter="handleSearch"
        @input="syncToStore"
      />
    </div>

    <!-- District multi-select -->
    <div class="filter-group">
      <label>区域</label>
      <div class="filter-districts">
        <button
          v-for="district in districtOptions"
          :key="district"
          :class="{ active: isDistrictActive(district) }"
          @click="toggleDistrict(district)"
        >
          {{ district }}
          <span v-if="districtCounts[district]" class="district-badge">
            {{ districtCounts[district] }}
          </span>
        </button>
      </div>
    </div>

    <!-- Layout select -->
    <div class="filter-group">
      <label>户型</label>
      <select
        v-model="localFilters.layout"
        class="filter-select"
        @change="syncToStore"
      >
        <option :value="null">不限</option>
        <option value="一室">一室</option>
        <option value="两室">两室</option>
        <option value="三室及以上">三室及以上</option>
      </select>
    </div>

    <!-- Price range -->
    <div class="filter-group">
      <label>价格范围 (元/月)</label>
      <div class="price-inputs">
        <input
          v-model.number="localFilters.minPrice"
          type="number"
          class="price-input"
          placeholder="最低"
          min="0"
          max="8000"
        />
        <span class="price-sep">—</span>
        <input
          v-model.number="localFilters.maxPrice"
          type="number"
          class="price-input"
          placeholder="最高"
          min="0"
          max="8000"
        />
      </div>
      <input
        type="range"
        class="filter-slider"
        min="0"
        max="8000"
        step="100"
        :value="localFilters.maxPrice"
        @input="localFilters.maxPrice = Number($event.target.value)"
      />
    </div>

    <!-- Sort selector -->
    <div class="filter-group">
      <label>排序方式</label>
      <div class="sort-options">
        <button
          v-for="sort in sortOptions"
          :key="sort"
          :class="{ active: localFilters.sortBy === sort }"
          @click="selectSort(sort)"
        >
          {{ sort }}
        </button>
      </div>
    </div>

    <!-- Subway line filter -->
    <div class="filter-group">
      <label>地铁线路</label>
      <select
        v-model="localSubwayLine"
        class="filter-select"
        @change="selectSubwayLine"
      >
        <option value="">不限</option>
        <option v-for="line in subwayLines" :key="line.name" :value="line.name">
          {{ line.name }}
        </option>
      </select>
    </div>

    <!-- Search button -->
    <button class="search-btn" @click="handleSearch">
      搜索房源
    </button>
  </div>
</template>

<script setup>
import { reactive, ref, watch, onMounted } from 'vue'
import { useHouseStore } from '../../stores/house.js'
import { fetchDistrictList, fetchSubwayLines } from '../../api/client.js'

const emit = defineEmits(['search'])

const houseStore = useHouseStore()

const districtOptions = ['天河', '海珠', '番禺', '越秀', '荔湾', '白云']
const sortOptions = ['综合推荐', '价格从低到高', '价格从高到低', '光照最优', '隔音最优']
const districtCounts = ref({})
const subwayLines = ref([])
const localSubwayLine = ref('')

const localFilters = reactive({
  keyword: houseStore.filters.keyword || '',
  districts: [...houseStore.filters.districts],
  layout: houseStore.filters.layout,
  minPrice: houseStore.filters.minPrice,
  maxPrice: houseStore.filters.maxPrice,
  sortBy: houseStore.filters.sortBy,
})

onMounted(async () => {
  try {
    const list = await fetchDistrictList()
    list.forEach(item => {
      districtCounts.value[item.district] = item.count
    })
  } catch (e) {
    console.error('Failed to load district counts:', e)
  }
  try {
    subwayLines.value = await fetchSubwayLines()
  } catch (e) {
    console.error('Failed to load subway lines:', e)
  }
})

function isDistrictActive(district) {
  return localFilters.districts.includes(district)
}

function toggleDistrict(district) {
  if (isDistrictActive(district)) {
    localFilters.districts = localFilters.districts.filter((d) => d !== district)
  } else {
    localFilters.districts = [...localFilters.districts, district]
  }
  syncToStore()
}

function selectSort(sort) {
  localFilters.sortBy = sort
  syncToStore()
}

function syncToStore() {
  houseStore.updateFilter('keyword', localFilters.keyword)
  houseStore.updateFilter('districts', [...localFilters.districts])
  houseStore.updateFilter('layout', localFilters.layout)
  houseStore.updateFilter('minPrice', localFilters.minPrice)
  houseStore.updateFilter('maxPrice', localFilters.maxPrice)
  houseStore.updateFilter('sortBy', localFilters.sortBy)
}

function selectSubwayLine() {
  houseStore.setSubwayLine(localSubwayLine.value)
}

function handleSearch() {
  syncToStore()
  emit('search')
}

// Sync store changes back to local
watch(
  () => houseStore.filters,
  (filters) => {
    localFilters.keyword = filters.keyword || ''
    localFilters.districts = [...filters.districts]
    localFilters.layout = filters.layout
    localFilters.minPrice = filters.minPrice
    localFilters.maxPrice = filters.maxPrice
    localFilters.sortBy = filters.sortBy
  },
  { deep: true }
)
</script>

<style scoped>
.filter-input {
  width: 100%; padding: 10px 12px;
  border: 1.5px solid var(--border); border-radius: 8px;
  font-size: 14px; outline: none; background: #fff; box-sizing: border-box;
}
.filter-input:focus { border-color: var(--accent); }

.price-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.price-input {
  flex: 1;
  padding: 8px 12px;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  background: #fff;
}

.price-input:focus {
  border-color: var(--accent);
}

.price-sep {
  color: var(--text-secondary);
  font-size: 14px;
}

.district-badge {
  display: inline-block;
  background: rgba(102, 126, 234, 0.15);
  color: var(--accent);
  padding: 0 5px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 700;
  margin-left: 4px;
  min-width: 18px;
  text-align: center;
}

.filter-districts button.active .district-badge {
  background: rgba(255, 255, 255, 0.35);
  color: #fff;
}
</style>
