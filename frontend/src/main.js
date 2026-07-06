import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router/index.js'
import App from './App.vue'
import './assets/styles/main.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')

// Global unhandled promise rejection handler
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled Promise Rejection:', event.reason)
  // Prevent default browser console error for known API errors
  if (event.reason && event.reason.name === 'AxiosError') {
    event.preventDefault()
  }
})

// Global Vue error handler
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue Error:', err.message, info)
}
