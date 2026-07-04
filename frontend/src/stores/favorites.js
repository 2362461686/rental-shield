import { defineStore } from 'pinia'
import { fetchFavorites, toggleFavorite, checkFavorite } from '../api/client.js'

export const useFavoriteStore = defineStore('favorites', {
  state: () => ({
    favorites: [],
    favoritedIds: new Set(),
    loading: false,
  }),
  actions: {
    async loadFavorites() {
      this.loading = true
      try {
        this.favorites = await fetchFavorites()
        this.favoritedIds = new Set(this.favorites.map(f => f.house_id))
      } finally {
        this.loading = false
      }
    },
    async toggle(houseId) {
      const result = await toggleFavorite(houseId)
      if (result.favorited) {
        this.favoritedIds.add(houseId)
      } else {
        this.favoritedIds.delete(houseId)
      }
      await this.loadFavorites()
      return result.favorited
    },
    async checkStatus(houseId) {
      try {
        const result = await checkFavorite(houseId)
        if (result.favorited) this.favoritedIds.add(houseId)
        else this.favoritedIds.delete(houseId)
        return result.favorited
      } catch {
        return false
      }
    },
    isFavorited(houseId) {
      return this.favoritedIds.has(houseId)
    },
  },
})
