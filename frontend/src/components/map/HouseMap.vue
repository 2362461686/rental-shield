<template>
  <div class="house-map-container" :class="{ 'map-compact': mode === 'detail' }">
    <div v-if="mode === 'district'" class="map-header">
      <h3>广州各区域房源分布</h3>
      <p class="map-subtitle">点击区域标记查看详情</p>
    </div>
    <div ref="mapContainer" class="map-wrapper"></div>

    <!-- District popup (mode='district') -->
    <div v-if="mode === 'district' && selectedDistrict" class="map-popup">
      <div class="popup-close" @click="selectedDistrict = null">&times;</div>
      <h4>{{ selectedDistrict.district }}</h4>
      <div class="popup-stats">
        <div class="popup-stat">
          <span class="popup-stat-label">房源数</span>
          <span class="popup-stat-value">{{ selectedDistrict.house_count }}</span>
        </div>
        <div class="popup-stat">
          <span class="popup-stat-label">均价</span>
          <span class="popup-stat-value">{{ Math.round(selectedDistrict.avg_price) }}元</span>
        </div>
        <div class="popup-stat">
          <span class="popup-stat-label">采光</span>
          <span class="popup-stat-value">{{ selectedDistrict.avg_sunlight?.toFixed(1) }}h</span>
        </div>
        <div class="popup-stat">
          <span class="popup-stat-label">隔音</span>
          <span class="popup-stat-value">{{ selectedDistrict.avg_noise?.toFixed(0) }}dB</span>
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
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { fetchDistrictStats, fetchSubwayLineDetail } from '../../api/client.js'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const router = useRouter()
const mapContainer = ref(null)
const selectedDistrict = ref(null)

const props = defineProps({
  mode: { type: String, default: 'district' },
  houses: { type: Array, default: () => [] },
  houseDetail: { type: Object, default: null },
  workplace: { type: Object, default: null },
  commuteCache: { type: Object, default: () => ({}) },
  showCommuteRoutes: { type: Boolean, default: false },
  showSubway: { type: Boolean, default: false },
  subwayLine: { type: String, default: '' },
})

const emit = defineEmits(['house-click', 'map-click'])

let map = null
let subwayLayerGroup = null
const markers = []
const commuteLines = []

// 广州各区坐标和颜色
const DISTRICT_COORDS = {
  '天河': [23.125, 113.361], '海珠': [23.083, 113.317],
  '番禺': [22.938, 113.354], '越秀': [23.129, 113.267],
  '荔湾': [23.115, 113.243], '白云': [23.158, 113.275],
}
const DISTRICT_COLORS = {
  '天河': '#667eea', '海珠': '#27ae60', '番禺': '#e67e22',
  '越秀': '#e74c3c', '荔湾': '#9b59b6', '白云': '#3498db',
}

function createDistrictIcon(color, size = 40) {
  return L.divIcon({
    className: 'custom-district-marker',
    html: `<div style="background:${color};width:${size}px;height:${size}px;border-radius:50%;border:3px solid #fff;box-shadow:0 3px 12px ${color}66;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:12px"></div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  })
}

function createHouseIcon(house) {
  const price = house.price || 0
  const riskLabel = house.risk_label || ''
  let color = '#27ae60'
  if (riskLabel.includes('中')) color = '#e67e22'
  if (riskLabel.includes('高')) color = '#e74c3c'

  return L.divIcon({
    className: 'house-marker',
    html: `<div style="background:${color};color:#fff;padding:3px 8px;border-radius:4px;font-size:12px;font-weight:700;white-space:nowrap;border:2px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,0.3)">${price}</div>`,
    iconSize: [60, 28],
    iconAnchor: [30, 14],
  })
}

function createWorkspaceIcon() {
  return L.divIcon({
    className: 'workspace-marker',
    html: `<div style="background:#e74c3c;color:#fff;width:24px;height:24px;border-radius:50%;border:3px solid #fff;box-shadow:0 2px 8px rgba(231,76,60,0.5);display:flex;align-items:center;justify-content:center;font-size:14px">&#x1F3E2;</div>`,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
  })
}

function createPopupContent(house, commuteData = null) {
  let html = `<div style="min-width:180px"><strong style="font-size:14px">${house.community || ''}</strong>`
  html += `<p style="margin:4px 0;color:#666">${house.layout} · ${house.area}m²</p>`
  html += `<p style="font-size:16px;font-weight:700;color:#e74c3c;margin:4px 0">${house.price}元/月</p>`
  if (commuteData && commuteData.commute_duration != null) {
    html += `<p style="font-size:12px;color:#999">通勤约${commuteData.commute_duration}分钟</p>`
  }
  html += `<button onclick="window.__houseMapClick && window.__houseMapClick(${house.id})" style="margin-top:6px;padding:4px 12px;background:#667eea;color:#fff;border:none;border-radius:4px;cursor:pointer">查看详情</button></div>`
  return html
}

onMounted(async () => {
  if (!mapContainer.value) return
  await nextTick()

  map = L.map(mapContainer.value, {
    center: [23.13, 113.30],
    zoom: 11,
    zoomControl: true,
    attributionControl: false,
  })

  L.tileLayer('https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}', {
    subdomains: ['1', '2', '3', '4'],
    maxZoom: 18,
    minZoom: 8,
  }).addTo(map)

  // Global click handler for popup buttons
  window.__houseMapClick = (houseId) => {
    emit('house-click', { id: houseId })
  }

  if (props.mode === 'district') {
    await loadDistrictMarkers()
  } else if (props.mode === 'houses') {
    loadHouseMarkers()
  } else if (props.mode === 'detail') {
    loadDetailMarker()
  }

  // 加载地铁线路
  if (props.showSubway) {
    await loadSubwayLayer()
  }
})

watch(() => props.subwayLine, async (newLine) => {
  if (subwayLayerGroup) { subwayLayerGroup.clearLayers(); subwayLayerGroup.remove() }
  if (!newLine) return
  await loadSubwayLayer()
})

onBeforeUnmount(() => {
  if (map) { map.remove(); map = null }
  delete window.__houseMapClick
})

async function loadDistrictMarkers() {
  try {
    const data = await fetchDistrictStats()
    if (data && data.districts) {
      data.districts.forEach(d => {
        const coords = DISTRICT_COORDS[d.district]
        if (!coords) return
        const color = DISTRICT_COLORS[d.district] || '#999'
        const icon = createDistrictIcon(color, Math.min(30 + d.house_count * 2, 56))
        const marker = L.marker(coords, { icon }).addTo(map)
          .bindTooltip(`${d.district} · ${d.house_count}套房`, {
            direction: 'top', offset: [0, -8], className: 'district-tooltip',
          })
        marker.on('click', () => { selectedDistrict.value = d })
        markers.push(marker)
      })
      const bounds = L.latLngBounds(markers.map(m => m.getLatLng()))
      map.fitBounds(bounds.pad(0.15))
    }
  } catch (e) {
    console.error('Failed to load district stats:', e)
  }
}

function loadHouseMarkers() {
  if (!props.houses.length) return
  const validHouses = props.houses.filter(h => h.latitude && h.longitude)

  validHouses.forEach(house => {
    const icon = createHouseIcon(house)
    const commuteData = props.commuteCache[house.id]
    const marker = L.marker([house.latitude, house.longitude], { icon }).addTo(map)
    marker.bindPopup(createPopupContent(house, commuteData), { offset: [1, -14] })
    marker.on('click', () => { emit('house-click', house) })
    markers.push(marker)
  })

  // Add workplace marker and commute lines
  if (props.workplace && props.workplace.lat && props.workplace.lng) {
    L.marker([props.workplace.lat, props.workplace.lng], { icon: createWorkspaceIcon() })
      .addTo(map)
      .bindTooltip(props.workplace.name || '公司', { direction: 'top' })

    if (props.showCommuteRoutes) {
      Object.entries(props.commuteCache).forEach(([houseId, data]) => {
        if (!data.commute_duration) return
        const house = props.houses.find(h => h.id === Number(houseId))
        if (!house?.latitude || !house?.longitude) return
        const line = L.polyline(
          [[house.latitude, house.longitude], [props.workplace.lat, props.workplace.lng]],
          { color: '#667eea', weight: 2, opacity: 0.5, dashArray: '8, 8' }
        ).addTo(map)
        commuteLines.push(line)
      })
    }
  }

  // Fit bounds
  const allCoords = markers.map(m => m.getLatLng())
  if (props.workplace && props.workplace.lat) {
    allCoords.push([props.workplace.lat, props.workplace.lng])
  }
  if (allCoords.length) {
    map.fitBounds(L.latLngBounds(allCoords).pad(0.1))
  }
}

function loadDetailMarker() {
  const house = props.houseDetail
  if (!house || !house.latitude || !house.longitude) return

  L.marker([house.latitude, house.longitude], {
    icon: L.divIcon({
      className: '',
      html: `<div style="background:#667eea;color:#fff;width:32px;height:32px;border-radius:50%;border:3px solid #fff;box-shadow:0 2px 8px rgba(102,126,234,0.5);display:flex;align-items:center;justify-content:center">&#x1F3E0;</div>`,
      iconSize: [38, 38],
      iconAnchor: [19, 19],
    })
  }).addTo(map).bindPopup(`<strong>${house.community}</strong><br/>${house.layout} · ${house.area}m² · ${house.price}元/月`)

  // Workplace marker + line
  if (props.workplace && props.workplace.lat && props.workplace.lng) {
    L.marker([props.workplace.lat, props.workplace.lng], { icon: createWorkspaceIcon() }).addTo(map)
      .bindTooltip(props.workplace.name || '公司')
    L.polyline([[house.latitude, house.longitude], [props.workplace.lat, props.workplace.lng]],
      { color: '#e74c3c', weight: 2, dashArray: '6, 4' }).addTo(map)
    map.fitBounds(L.latLngBounds([
      [house.latitude, house.longitude],
      [props.workplace.lat, props.workplace.lng],
    ]).pad(0.2))
  } else {
    map.setView([house.latitude, house.longitude], 14)
  }
}

function goDistrict(district) {
  router.push({ path: '/search', query: { districts: district } })
}

async function loadSubwayLayer() {
  const lineName = props.subwayLine
  if (!lineName || !map) return

  if (subwayLayerGroup) { subwayLayerGroup.clearLayers(); subwayLayerGroup.remove() }
  subwayLayerGroup = L.layerGroup().addTo(map)

  try {
    const data = await fetchSubwayLineDetail(lineName)
    if (!data || !data.stations) return

    const color = data.color || '#667eea'
    const coords = data.stations.map(s => [s.latitude, s.longitude])

    // 绘制地铁线路
    L.polyline(coords, { color, weight: 4, opacity: 0.8 }).addTo(subwayLayerGroup)

    // 绘制地铁站点
    data.stations.forEach(s => {
      L.circleMarker([s.latitude, s.longitude], {
        radius: 5,
        color: '#fff',
        fillColor: color,
        fillOpacity: 1,
        weight: 2,
      }).addTo(subwayLayerGroup)
        .bindTooltip(s.name, { direction: 'top', className: 'station-tooltip' })
    })

    // 自动适应视野
    if (coords.length > 0) {
      map.fitBounds(L.latLngBounds(coords).pad(0.1))
    }
  } catch (e) {
    console.error('Failed to load subway line:', e)
  }
}
</script>

<style scoped>
.house-map-container {
  background: #fff;
  border-radius: 12px;
  box-shadow: var(--shadow);
  overflow: hidden;
  position: relative;
}
.house-map-container.map-compact { border-radius: 8px; }
.map-header { padding: 16px 20px 0; }
.map-header h3 { font-size: 16px; margin-bottom: 2px; color: var(--text); }
.map-subtitle { font-size: 13px; color: var(--text-secondary); margin-bottom: 0; }
.map-wrapper { width: 100%; height: 380px; z-index: 1; }
.map-compact .map-wrapper { height: 280px; }

.map-popup {
  position: absolute; top: 60px; right: 12px; background: #fff;
  border-radius: 10px; padding: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  width: 220px; z-index: 1000;
}
.popup-close { position: absolute; top: 4px; right: 10px; font-size: 20px; cursor: pointer; color: var(--text-secondary); line-height: 1; }
.map-popup h4 { font-size: 15px; margin-bottom: 10px; color: var(--text); padding-right: 20px; }
.popup-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px; }
.popup-stat { text-align: center; }
.popup-stat-label { display: block; font-size: 11px; color: var(--text-secondary); }
.popup-stat-value { font-size: 14px; font-weight: 700; color: var(--text); }
.popup-risk { display: flex; gap: 4px; margin-bottom: 10px; flex-wrap: wrap; }
.risk-badge { font-size: 11px; padding: 2px 8px; border-radius: 10px; font-weight: 600; }
.risk-low { background: #d4edda; color: #155724; }
.risk-medium { background: #fff3cd; color: #856404; }
.risk-high { background: #f8d7da; color: #721c24; }
.popup-btn { width: 100%; padding: 8px; background: var(--accent); color: #fff; border: none; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; }
.popup-btn:hover { background: var(--accent2); }

@media (max-width: 768px) {
  .map-wrapper { height: 280px; }
  .map-popup { position: relative; top: 0; right: 0; width: 100%; border-radius: 0; box-shadow: none; border-top: 1px solid var(--border); }
}
</style>

<style>
.custom-district-marker { background: transparent !important; border: none !important; }
.house-marker { background: transparent !important; border: none !important; }
.district-tooltip { background: rgba(0,0,0,0.75) !important; border: none !important; border-radius: 6px !important; color: #fff !important; padding: 4px 10px !important; font-size: 13px !important; font-family: inherit !important; }
.district-tooltip::before { border-top-color: rgba(0,0,0,0.75) !important; }
.station-tooltip { background: rgba(0,0,0,0.75) !important; border: none !important; border-radius: 6px !important; color: #fff !important; padding: 3px 8px !important; font-size: 12px !important; }
.station-tooltip::before { border-top-color: rgba(0,0,0,0.75) !important; }
</style>
