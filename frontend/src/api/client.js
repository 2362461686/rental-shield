import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// rawAxios 用于需要读取响应头的场景
const rawAxios = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// 响应拦截器：错误处理
api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    console.error('API Error:', err.message)
    return Promise.reject(err)
  }
)

// --- Houses ---
export const fetchHouses = async (params) => {
  const res = await rawAxios.get('/houses', { params })
  return {
    items: res.data,
    total: parseInt(res.headers['x-total-count']) || res.data.length,
    page: parseInt(res.headers['x-page']) || 1,
    pageSize: parseInt(res.headers['x-page-size']) || res.data.length,
  }
}
export const fetchCommunityStats = () => api.get('/houses/communities/stats')
export const fetchLandlordHouses = (hash) => api.get(`/houses/landlords/${encodeURIComponent(hash)}`)
export const fetchHouseDetail = (id) => api.get(`/houses/${id}`)
export const fetchPriceHistory = (id) => api.get(`/houses/${id}/price-history`)
export const fetchReviews = (id) => api.get(`/houses/${id}/reviews`)
export const fetchImages = (id) => api.get(`/houses/${id}/images`)

// --- Districts ---
export const fetchDistrictStats = () => api.get('/districts/stats')
export const fetchDistrictStatsByName = (district) => api.get(`/districts/stats/${encodeURIComponent(district)}`)
export const fetchDistrictList = () => api.get('/districts/list')
export const geocodeAddress = (address) => api.get('/districts/geocode', { params: { address } })

// --- Commute ---
export const calcCommute = (params) => api.get('/commute/calculate', { params })
export const saveWorkspace = (data) => api.post('/commute/workspace', data)
export const fetchWorkspace = () => api.get('/commute/workspace')
export const clearWorkspace = () => api.delete('/commute/workspace')

// --- Subway ---
export const fetchSubwayLines = () => api.get('/subway/lines')
export const fetchSubwayLineDetail = (lineName) => api.get(`/subway/lines/${encodeURIComponent(lineName)}`)
export const fetchSubwayStations = () => api.get('/subway/stations')
export const fetchNearbyStations = (lat, lng, maxDistance = 1.5) => api.get('/subway/nearby', { params: { lat, lng, max_distance: maxDistance } })
export const fetchNearbyLines = (lat, lng) => api.get('/subway/nearby-lines', { params: { lat, lng } })
export const calcMetroCommute = (params) => api.get('/subway/commute', { params })

// --- Favorites ---
export const fetchFavorites = () => api.get('/favorites')
export const toggleFavorite = (houseId) => api.post(`/favorites/${houseId}`)
export const checkFavorite = (houseId) => api.get(`/favorites/check/${houseId}`)

// --- Assessments ---
export const createAssessment = (data) => api.post('/assessments', data)
export const analyzeReviews = (houseId) => api.post(`/assessments/${houseId}/analyze-reviews`)
export const addReview = (houseId, data) => api.post(`/assessments/${houseId}/reviews`, { content: data.content, platform: 'user_input' })

// --- Agents ---
export const runReviewMining = (id) => api.post(`/agents/review-mining/${id}`)
export const runLandlordRisk = (hash) => api.post(`/agents/landlord-risk/${encodeURIComponent(hash)}`)
export const runFinalAdvice = (id) => api.post(`/agents/final-advice/${id}`)

export default api
