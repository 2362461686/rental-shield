import { defineStore } from 'pinia'
import {
  fetchHouseDetail, fetchReviews, fetchImages,
  runReviewMining, runLandlordRisk, runFinalAdvice,
  analyzeReviews, addReview,
} from '../api/client.js'

export const useDetailStore = defineStore('detail', {
  state: () => ({
    house: null,
    reviews: [],
    images: [],
    reviewMining: null,
    landlordRisk: null,
    finalAdvice: null,
    assessment: null,
    loading: { house: false, reviews: false, images: false, ai: false, assessment: false },
    errors: {},
  }),

  actions: {
    async load(houseId) {
      // Reset
      this.house = null; this.reviews = []; this.images = []
      this.reviewMining = null; this.landlordRisk = null; this.finalAdvice = null
      this.assessment = null

      // Phase 1: Load fast data + assessment in parallel
      this.loading.house = this.loading.reviews = this.loading.images = this.loading.assessment = true
      try {
        const [house, reviews, images, assessment] = await Promise.all([
          fetchHouseDetail(houseId).catch(e => { this.errors.house = e.message; return null }),
          fetchReviews(houseId).catch(e => { this.errors.reviews = e.message; return [] }),
          fetchImages(houseId).catch(e => { this.errors.images = e.message; return [] }),
          analyzeReviews(houseId).catch(() => null),
        ])
        this.house = house
        this.reviews = reviews
        this.images = images
        this.assessment = assessment
      } finally {
        this.loading.house = this.loading.reviews = this.loading.images = this.loading.assessment = false
      }

      if (!this.house) return

      // Phase 2: Load AI data in parallel
      this.loading.ai = true
      try {
        const phoneHash = this.house.landlord_phone_hash

        const promises = [
          runReviewMining(houseId).catch(() => null),
          phoneHash ? runLandlordRisk(phoneHash).catch(() => null) : Promise.resolve(null),
        ]

        const [mining, landlord] = await Promise.all(promises)
        this.reviewMining = mining
        this.landlordRisk = landlord || { risk_level: '未知', risk_items: [], summary: '无法加载' }

        this.finalAdvice = await runFinalAdvice(houseId).catch(() => null)
      } finally {
        this.loading.ai = false
      }
    },

    async addReviewAndRefresh(houseId, content) {
      await addReview(houseId, { content })
      // 重新加载评论列表和分析结果
      this.loading.assessment = true
      try {
        const [reviews, assessment] = await Promise.all([
          fetchReviews(houseId).catch(() => []),
          analyzeReviews(houseId).catch(() => null),
        ])
        this.reviews = reviews
        this.assessment = assessment
      } finally {
        this.loading.assessment = false
      }
    },

    clear() {
      this.house = null; this.reviews = []; this.images = []
      this.reviewMining = null; this.landlordRisk = null; this.finalAdvice = null
      this.assessment = null
    },
  },
})
