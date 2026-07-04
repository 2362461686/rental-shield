import { defineStore } from 'pinia'
import { fetchHouses } from '../api/client.js'

export const useHouseStore = defineStore('house', {
  state: () => ({
    filters: {
      districts: [],
      layout: null,
      minPrice: 0,
      maxPrice: 8000,
      sortBy: '综合推荐',
    },
    houses: [],
    loading: false,
    searched: false,
  }),
  actions: {
    updateFilter(key, value) {
      this.filters[key] = value
    },
    async search() {
      this.loading = true
      this.searched = true
      try {
        const params = {
          min_price: this.filters.minPrice,
          max_price: this.filters.maxPrice,
          sort_by: this.filters.sortBy,
        }
        if (this.filters.districts.length > 0) params.districts = this.filters.districts.join(',')
        if (this.filters.layout) params.layout = this.filters.layout
        this.houses = await fetchHouses(params)
      } finally {
        this.loading = false
      }
    },
  },
})
