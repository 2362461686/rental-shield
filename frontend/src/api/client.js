import axios from 'axios'

const api = axios.create({
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
export const fetchHouses = (params) => api.get('/houses', { params })
export const fetchHouseDetail = (id) => api.get(`/houses/${id}`)
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

// --- Agents ---
export const runReviewMining = (id) => api.post(`/agents/review-mining/${id}`)
export const runLandlordRisk = (hash) => api.post(`/agents/landlord-risk/${encodeURIComponent(hash)}`)
export const runFinalAdvice = (id) => api.post(`/agents/final-advice/${id}`)

export default api
