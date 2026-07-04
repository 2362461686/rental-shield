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

// --- Agents ---
export const runReviewMining = (id) => api.post(`/agents/review-mining/${id}`)
export const runLandlordRisk = (hash) => api.post(`/agents/landlord-risk/${encodeURIComponent(hash)}`)
export const runFinalAdvice = (id) => api.post(`/agents/final-advice/${id}`)

export default api
