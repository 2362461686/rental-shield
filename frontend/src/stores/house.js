import { defineStore } from 'pinia'
import { fetchHouses, saveWorkspace } from '../api/client.js'

export const useHouseStore = defineStore('house', {
  state: () => ({
    filters: {
      districts: [],
      layout: null,
      minPrice: 0,
      maxPrice: 8000,
      sortBy: '综合推荐',
      keyword: '',
    },
    houses: [],
    loading: false,
    searched: false,
    // Pagination
    page: 1,
    pageSize: 20,
    totalCount: 0,
    // Subway filter
    selectedSubwayLine: '',
    // Workspace / commute
    workspace: {
      name: '',
      lat: null,
      lng: null,
      configured: false,
    },
    commuteCache: {},
    commuteLoading: false,
  }),
  getters: {
    totalPages: (state) => Math.max(1, Math.ceil(state.totalCount / state.pageSize)),
    hasMore: (state) => state.page * state.pageSize < state.totalCount,
  },
  actions: {
    updateFilter(key, value) {
      this.filters[key] = value
    },
    setSubwayLine(line) {
      this.selectedSubwayLine = line
    },
    async search() {
      this.loading = true
      this.searched = true
      this.page = 1
      try {
        const params = {
          min_price: this.filters.minPrice,
          max_price: this.filters.maxPrice,
          sort_by: this.filters.sortBy,
          page: this.page,
          page_size: this.pageSize,
        }
        if (this.filters.districts.length > 0) params.districts = this.filters.districts.join(',')
        if (this.filters.layout) params.layout = this.filters.layout
        if (this.filters.keyword) params.keyword = this.filters.keyword
        const result = await fetchHouses(params)
        this.houses = result.items
        this.totalCount = result.total
        this.page = result.page
      } finally {
        this.loading = false
      }
    },
    async loadPage(page) {
      this.loading = true
      try {
        const params = {
          min_price: this.filters.minPrice,
          max_price: this.filters.maxPrice,
          sort_by: this.filters.sortBy,
          page: page,
          page_size: this.pageSize,
        }
        if (this.filters.districts.length > 0) params.districts = this.filters.districts.join(',')
        if (this.filters.layout) params.layout = this.filters.layout
        if (this.filters.keyword) params.keyword = this.filters.keyword
        const result = await fetchHouses(params)
        this.houses = result.items
        this.totalCount = result.total
        this.page = result.page
        // 滚动到顶部
        window.scrollTo({ top: 0, behavior: 'smooth' })
      } finally {
        this.loading = false
      }
    },
    setWorkspace(workspace) {
      this.workspace = { ...workspace }
      this.commuteCache = {}
      // Persist to backend
      if (workspace.lat != null) {
        saveWorkspace({ name: workspace.name, lat: workspace.lat, lng: workspace.lng }).catch(() => {})
      }
    },
    clearWorkspace() {
      this.workspace = { name: '', lat: null, lng: null, configured: false }
      this.commuteCache = {}
    },
    setCommuteData(houseId, data) {
      this.commuteCache[houseId] = data
    },
  },
})
