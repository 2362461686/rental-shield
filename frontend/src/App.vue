<template>
  <div>
    <AppHeader />
    <main class="page-container">
      <ErrorBoundary>
        <router-view />
      </ErrorBoundary>
    </main>
    <AppFooter />
    <BackToTop />
    <AiChat />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from './components/layout/AppHeader.vue'
import AppFooter from './components/layout/AppFooter.vue'
import ErrorBoundary from './components/ui/ErrorBoundary.vue'
import BackToTop from './components/ui/BackToTop.vue'
import AiChat from './components/ui/AiChat.vue'

// Load persisted workspace on startup
import { useHouseStore } from './stores/house.js'
import { fetchWorkspace } from './api/client.js'

const houseStore = useHouseStore()

onMounted(async () => {
  try {
    const ws = await fetchWorkspace()
    if (ws && ws.name) {
      houseStore.setWorkspace({
        name: ws.name,
        lat: ws.workplace_lat || ws.lat,
        lng: ws.workplace_lng || ws.lng,
        configured: true,
      })
    }
  } catch (e) {
    // workspace not configured — silently ignore
  }
})
</script>
