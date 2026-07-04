<template>
  <div class="district-overview">
    <div class="overview-header">
      <h3>广州各区房源对比</h3>
      <p class="overview-subtitle">点击区域卡片开始筛选</p>
    </div>

    <div v-if="loading" class="overview-loading">
      <div class="skeleton" style="height:120px" v-for="n in 6" :key="n"></div>
    </div>

    <div v-else class="district-grid">
      <div
        v-for="d in districts"
        :key="d.district"
        class="district-card"
        :style="{ borderTopColor: colors[d.district] || '#999' }"
        @click="goDistrict(d.district)"
      >
        <div class="district-card-header">
          <h4>{{ d.district }}</h4>
          <span class="district-count">{{ d.house_count }} 套</span>
        </div>
        <div class="district-card-stats">
          <div class="district-card-stat">
            <span class="dcs-label">均价</span>
            <span class="dcs-value">{{ d.avg_price }}<small>元/月</small></span>
          </div>
          <div class="district-card-stat">
            <span class="dcs-label">采光</span>
            <span class="dcs-value">{{ d.avg_sunlight }}<small>h/天</small></span>
          </div>
          <div class="district-card-stat">
            <span class="dcs-label">隔音</span>
            <span class="dcs-value">{{ d.avg_noise }}<small>dB</small></span>
          </div>
        </div>
        <div class="district-card-risk">
          <div class="risk-bar">
            <div
              class="risk-bar-seg risk-bar-low"
              :style="{ flex: d.risk_breakdown?.low || 0 }"
              :title="'低风险: ' + (d.risk_breakdown?.low || 0)"
            ></div>
            <div
              class="risk-bar-seg risk-bar-medium"
              :style="{ flex: d.risk_breakdown?.medium || 0 }"
              :title="'中风险: ' + (d.risk_breakdown?.medium || 0)"
            ></div>
            <div
              class="risk-bar-seg risk-bar-high"
              :style="{ flex: d.risk_breakdown?.high || 0 }"
              :title="'高风险: ' + (d.risk_breakdown?.high || 0)"
            ></div>
          </div>
          <div class="risk-legend">
            <span class="risk-legend-item"><span class="dot dot-green"></span>低</span>
            <span class="risk-legend-item"><span class="dot dot-yellow"></span>中</span>
            <span class="risk-legend-item"><span class="dot dot-red"></span>高</span>
          </div>
        </div>
        <button class="district-card-btn">查看房源 &rarr;</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchDistrictStats } from '../../api/client.js'

const router = useRouter()
const districts = ref([])
const loading = ref(true)

const colors = {
  '天河': '#667eea',
  '海珠': '#27ae60',
  '番禺': '#e67e22',
  '越秀': '#e74c3c',
  '荔湾': '#9b59b6',
  '白云': '#3498db',
}

onMounted(async () => {
  try {
    const data = await fetchDistrictStats()
    if (data && data.districts) {
      districts.value = data.districts.sort((a, b) => b.house_count - a.house_count)
    }
  } catch (e) {
    console.error('Failed to load district stats:', e)
  } finally {
    loading.value = false
  }
})

function goDistrict(district) {
  router.push({ path: '/search', query: { districts: district } })
}
</script>

<style scoped>
.district-overview {
  padding: 0;
}

.overview-header {
  margin-bottom: 20px;
}

.overview-header h3 {
  font-size: 20px;
  margin-bottom: 4px;
}

.overview-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
}

.overview-loading {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.district-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.district-card {
  background: #fff;
  border-radius: 12px;
  padding: 18px;
  box-shadow: var(--shadow);
  border-top: 4px solid #999;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.district-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-hover);
}

.district-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.district-card-header h4 {
  font-size: 16px;
  color: var(--text);
  font-weight: 700;
}

.district-count {
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  background: var(--accent);
  padding: 2px 10px;
  border-radius: 10px;
}

.district-card-stats {
  display: flex;
  gap: 12px;
  margin-bottom: 14px;
}

.district-card-stat {
  text-align: center;
  flex: 1;
}

.dcs-label {
  display: block;
  font-size: 11px;
  color: var(--text-secondary);
  margin-bottom: 2px;
}

.dcs-value {
  font-size: 16px;
  font-weight: 800;
  color: var(--text);
}

.dcs-value small {
  font-size: 10px;
  font-weight: 400;
  color: var(--text-secondary);
}

.district-card-risk {
  margin-bottom: 14px;
}

.risk-bar {
  display: flex;
  height: 6px;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 6px;
}

.risk-bar-seg {
  min-width: 0;
}

.risk-bar-low {
  background: var(--success);
}

.risk-bar-medium {
  background: var(--warning);
}

.risk-bar-high {
  background: var(--danger);
}

.risk-legend {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: var(--text-secondary);
}

.risk-legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.dot-green { background: var(--success); }
.dot-yellow { background: var(--warning); }
.dot-red { background: var(--danger); }

.district-card-btn {
  width: 100%;
  padding: 8px;
  background: #f5f7fa;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 13px;
  color: var(--accent);
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.district-card-btn:hover {
  background: var(--accent);
  color: #fff;
}

@media (max-width: 768px) {
  .district-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
