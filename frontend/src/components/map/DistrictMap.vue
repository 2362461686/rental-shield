<template>
  <div class="district-map-container">
    <div class="map-header">
      <h3>广州各区域房源分布</h3>
      <p class="map-subtitle">点击区域标记查看详情</p>
    </div>
    <div ref="mapContainer" class="map-wrapper"></div>
    <div v-if="selectedDistrict" class="map-popup">
      <div class="popup-close" @click="selectedDistrict = null">&times;</div>
      <h4>{{ selectedDistrict.district }}</h4>
      <div class="popup-stats">
        <div class="popup-stat">
          <span class="popup-stat-label">房源数</span>
          <span class="popup-stat-value">{{ selectedDistrict.house_count }}</span>
        </div>
        <div class="popup-stat">
          <span class="popup-stat-label">均价</span>
          <span class="popup-stat-value">{{ selectedDistrict.avg_price }}元</span>
        </div>
        <div class="popup-stat">
          <span class="popup-stat-label">采光</span>
          <span class="popup-stat-value">{{ selectedDistrict.avg_sunlight }}h</span>
        </div>
        <div class="popup-stat">
          <span class="popup-stat-label">隔音</span>
          <span class="popup-stat-value">{{ selectedDistrict.avg_noise }}dB</span>
        </div>
      </div>
      <div class="popup-risk">
        <span class="risk-badge risk-low">低风险 {{ selectedDistrict.risk_breakdown?.low || 0 }}</span>
        <span class="risk-badge risk-medium">中风险 {{ selectedDistrict.risk_breakdown?.medium || 0 }}</span>
        <span class="risk-badge risk-high">高风险 {{ selectedDistrict.risk_breakdown?.high || 0 }}</span>
      </div>
      <button class="popup-btn" @click="goDistrict(selectedDistrict.district)">
        查看{{ selectedDistrict.district }}房源 &rarr;
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'
import { fetchDistrictStats } from '../../api/client.js'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const router = useRouter()
const mapContainer = ref(null)
const selectedDistrict = ref(null)

let map = null
const markers = []

// 广州各区近似坐标
const DISTRICT_COORDS = {
  '天河': [23.125, 113.361],
  '海珠': [23.083, 113.317],
  '番禺': [22.938, 113.354],
  '越秀': [23.129, 113.267],
  '荔湾': [23.115, 113.243],
  '白云': [23.158, 113.275],
}

// 区域颜色映射
const DISTRICT_COLORS = {
  '天河': '#667eea',
  '海珠': '#27ae60',
  '番禺': '#e67e22',
  '越秀': '#e74c3c',
  '荔湾': '#9b59b6',
  '白云': '#3498db',
}

function createDistrictIcon(color, size = 40) {
  return L.divIcon({
    className: 'custom-district-marker',
    html: `<div style="
      background: ${color};
      width: ${size}px;
      height: ${size}px;
      border-radius: 50%;
      border: 3px solid #fff;
      box-shadow: 0 3px 12px ${color}66;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-weight: 700;
      font-size: 12px;
      transition: transform 0.2s;
    "></div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  })
}

onMounted(async () => {
  if (!mapContainer.value) return

  map = L.map(mapContainer.value, {
    center: [23.13, 113.30],
    zoom: 11,
    zoomControl: true,
    attributionControl: false,
  })

  // 使用高德地图瓦片（公开可用）
  L.tileLayer('https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}', {
    subdomains: ['1', '2', '3', '4'],
    maxZoom: 18,
    minZoom: 8,
  }).addTo(map)

  try {
    const data = await fetchDistrictStats()
    if (data && data.districts) {
      data.districts.forEach(d => {
        const coords = DISTRICT_COORDS[d.district]
        if (!coords) return

        const color = DISTRICT_COLORS[d.district] || '#999'
        const icon = createDistrictIcon(color, Math.min(30 + d.house_count * 2, 56))

        const marker = L.marker(coords, { icon })
          .addTo(map)
          .bindTooltip(`${d.district} · ${d.house_count}套房`, {
            direction: 'top',
            offset: [0, -8],
            className: 'district-tooltip',
          })

        marker.on('click', () => {
          selectedDistrict.value = d
        })

        markers.push(marker)
      })

      // Fit bounds to show all markers
      const bounds = L.latLngBounds(
        markers.map(m => m.getLatLng())
      )
      map.fitBounds(bounds.pad(0.15))
    }
  } catch (e) {
    console.error('Failed to load district stats:', e)
  }
})

onBeforeUnmount(() => {
  if (map) {
    map.remove()
    map = null
  }
})

function goDistrict(district) {
  router.push({ path: '/search', query: { districts: district } })
}
</script>

<style scoped>
.district-map-container {
  background: #fff;
  border-radius: 12px;
  box-shadow: var(--shadow);
  overflow: hidden;
  position: relative;
}

.map-header {
  padding: 16px 20px 0;
}

.map-header h3 {
  font-size: 16px;
  margin-bottom: 2px;
  color: var(--text);
}

.map-subtitle {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 0;
}

.map-wrapper {
  width: 100%;
  height: 380px;
  z-index: 1;
}

.map-popup {
  position: absolute;
  top: 60px;
  right: 12px;
  background: #fff;
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 220px;
  z-index: 1000;
}

.popup-close {
  position: absolute;
  top: 4px;
  right: 10px;
  font-size: 20px;
  cursor: pointer;
  color: var(--text-secondary);
  line-height: 1;
}

.map-popup h4 {
  font-size: 15px;
  margin-bottom: 10px;
  color: var(--text);
  padding-right: 20px;
}

.popup-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 10px;
}

.popup-stat {
  text-align: center;
}

.popup-stat-label {
  display: block;
  font-size: 11px;
  color: var(--text-secondary);
}

.popup-stat-value {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
}

.popup-risk {
  display: flex;
  gap: 4px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.risk-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 600;
}

.risk-low {
  background: #d4edda;
  color: #155724;
}

.risk-medium {
  background: #fff3cd;
  color: #856404;
}

.risk-high {
  background: #f8d7da;
  color: #721c24;
}

.popup-btn {
  width: 100%;
  padding: 8px;
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.popup-btn:hover {
  background: var(--accent2);
}

@media (max-width: 768px) {
  .map-wrapper {
    height: 280px;
  }

  .map-popup {
    position: relative;
    top: 0;
    right: 0;
    width: 100%;
    border-radius: 0;
    box-shadow: none;
    border-top: 1px solid var(--border);
  }
}
</style>

<style>
/* Global overrides for Leaflet within this component */
.custom-district-marker {
  background: transparent !important;
  border: none !important;
}
.district-tooltip {
  background: rgba(0, 0, 0, 0.75) !important;
  border: none !important;
  border-radius: 6px !important;
  color: #fff !important;
  padding: 4px 10px !important;
  font-size: 13px !important;
  font-family: inherit !important;
}
.district-tooltip::before {
  border-top-color: rgba(0, 0, 0, 0.75) !important;
}
</style>
