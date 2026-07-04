<template>
  <div class="info-grid">
    <div class="info-item">
      <div class="info-item-label">区域</div>
      <div class="info-item-value">{{ house.district || '--' }}</div>
    </div>
    <div class="info-item">
      <div class="info-item-label">小区</div>
      <div class="info-item-value">{{ house.community || '--' }}</div>
    </div>
    <div class="info-item">
      <div class="info-item-label">户型</div>
      <div class="info-item-value">{{ house.layout || '--' }}</div>
    </div>
    <div class="info-item">
      <div class="info-item-label">面积</div>
      <div class="info-item-value">{{ house.area ? house.area + ' m²' : '--' }}</div>
    </div>
    <div class="info-item">
      <div class="info-item-label">楼层</div>
      <div class="info-item-value">{{ formatFloor(house.floor, house.total_floors) }}</div>
    </div>
    <div class="info-item">
      <div class="info-item-label">朝向</div>
      <div class="info-item-value">{{ house.orientation || '--' }}</div>
    </div>
    <div class="info-item">
      <div class="info-item-label">窗户类型</div>
      <div class="info-item-value">{{ house.window_type || '--' }}</div>
    </div>
    <div class="info-item">
      <div class="info-item-label">建筑类型</div>
      <div class="info-item-value">{{ house.building_type || '--' }}</div>
    </div>
    <div class="info-item">
      <div class="info-item-label">建筑年代</div>
      <div class="info-item-value">{{ house.building_year || '--' }}</div>
    </div>
    <div class="info-item">
      <div class="info-item-label">距主街</div>
      <div class="info-item-value">{{ formatDistance(house.distance_to_street) }}</div>
    </div>
    <div class="info-item">
      <div class="info-item-label">底商</div>
      <div class="info-item-value">{{ house.has_business_below ? '有' : '无' }}</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  house: { type: Object, required: true },
})

function formatFloor(floor, totalFloors) {
  if (!floor && floor !== 0) return '--'
  const total = totalFloors ? ` / 共${totalFloors}层` : ''
  return `${floor}层${total}`
}

function formatDistance(distance) {
  if (!distance && distance !== 0) return '--'
  if (distance < 1000) return `${Math.round(distance)}m`
  return `${(distance / 1000).toFixed(1)}km`
}
</script>

<style scoped>
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}

.info-item {
  background: #fff;
  border-radius: 10px;
  padding: 14px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  border: 1px solid var(--border);
}

.info-item-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 2px;
}

.info-item-value {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
}

@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
