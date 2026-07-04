<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="workspace-modal">
      <h3>设置通勤地点</h3>
      <p class="modal-desc">输入您的工作/学校地址，用于计算通勤时间</p>
      <div class="form-group">
        <label>地点名称</label>
        <input v-model="name" placeholder="例如：天河软件园、琶洲会展中心" />
      </div>
      <div class="form-group">
        <label>详细地址</label>
        <input v-model="address" placeholder="输入地址后点击搜索" @keyup.enter="searchAddress" />
      </div>
      <button class="btn-geocode" :disabled="!address || searching" @click="searchAddress">
        {{ searching ? '搜索中...' : '搜索地址' }}
      </button>
      <div v-if="selectedLat !== null" class="coords-info">
        已定位: ({{ selectedLat.toFixed(6) }}, {{ selectedLng.toFixed(6) }})
      </div>
      <div class="modal-actions">
        <button class="btn-cancel" @click="$emit('close')">取消</button>
        <button class="btn-save" :disabled="!name || selectedLat === null" @click="save">保存</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { geocodeAddress } from '../../api/client.js'
import { useHouseStore } from '../../stores/house.js'

const emit = defineEmits(['save', 'close'])
const houseStore = useHouseStore()

const name = ref(houseStore.workspace.name || '')
const address = ref('')
const searching = ref(false)
const selectedLat = ref(null)
const selectedLng = ref(null)

async function searchAddress() {
  if (!address.value.trim()) return
  searching.value = true
  try {
    const result = await geocodeAddress(address.value.trim())
    if (result && result.latitude != null) {
      selectedLat.value = result.latitude
      selectedLng.value = result.longitude
    } else {
      alert('未找到该地址，请检查输入')
    }
  } catch {
    alert('地址搜索失败，请重试')
  } finally {
    searching.value = false
  }
}

function save() {
  houseStore.setWorkspace({
    name: name.value || '我的公司',
    lat: selectedLat.value,
    lng: selectedLng.value,
    configured: true,
  })
  emit('save', houseStore.workspace)
  emit('close')
}
</script>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 2000; }
.workspace-modal { background: #fff; border-radius: 12px; padding: 28px; width: 420px; max-width: 90vw; box-shadow: 0 8px 32px rgba(0,0,0,0.2); }
.workspace-modal h3 { font-size: 18px; margin-bottom: 4px; }
.modal-desc { font-size: 13px; color: var(--text-secondary); margin-bottom: 16px; }
.form-group { margin-bottom: 14px; }
.form-group label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 4px; color: var(--text); }
.form-group input { width: 100%; padding: 10px 12px; border: 1.5px solid var(--border); border-radius: 8px; font-size: 14px; outline: none; box-sizing: border-box; }
.form-group input:focus { border-color: var(--accent); }
.btn-geocode { width: 100%; padding: 10px; background: var(--accent); color: #fff; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; margin-bottom: 10px; }
.btn-geocode:disabled { background: #ccc; cursor: not-allowed; }
.coords-info { font-size: 13px; color: var(--accent); margin-bottom: 12px; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; }
.btn-cancel { padding: 8px 20px; background: #f0f0f0; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; }
.btn-save { padding: 8px 24px; background: var(--accent); color: #fff; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; }
.btn-save:disabled { background: #ccc; cursor: not-allowed; }
</style>
