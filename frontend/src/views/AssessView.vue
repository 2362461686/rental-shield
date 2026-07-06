<template>
  <div class="assess-new">
    <!-- Hero -->
    <section class="an-hero">
      <div class="an-hero-badge">AI 风险评估</div>
      <h1>输入房源信息，<span>AI 帮你判别风险</span></h1>
      <p>粘贴 58 / 贝壳链接自动抓取房屋信息，或手动填写 → AI 综合分析 → 生成风险报告</p>
    </section>

    <div class="an-body">
      <!-- Step Progress Indicator -->
      <div class="step-progress" v-if="showManual || scrapedData">
        <div class="step-dot completed">1</div>
        <div class="step-line" :class="{ completed: currentStep >= 2 }"></div>
        <div class="step-dot" :class="{ completed: currentStep >= 2, active: currentStep === 2 }">2</div>
        <div class="step-line" :class="{ completed: currentStep >= 3 }"></div>
        <div class="step-dot" :class="{ completed: currentStep >= 3, active: currentStep === 3 }">3</div>
      </div>

      <!-- ===== Step 1: URL 抓取 ===== -->
      <div class="an-card an-url-card">
        <div class="an-step-label">Step 1</div>
        <h3>粘贴房源链接</h3>
        <p>支持 58同城、贝壳找房、链家</p>
        <div class="an-url-row">
          <input
            v-model="urlInput"
            type="url"
            placeholder="https://gz.58.com/zufang/xxx 或 https://gz.ke.com/zufang/xxx"
            :disabled="scraping"
            @keydown.enter="handleScrape"
          />
          <button class="an-btn-primary" :disabled="scraping || !urlInput.trim()" @click="handleScrape">
            <span v-if="scraping" class="an-spin"></span>
            {{ scraping ? '抓取中…' : '自动抓取' }}
          </button>
          <button class="an-btn-text" @click="showManual = true">手动填写</button>
        </div>
        <div v-if="scrapeError" class="an-msg an-msg-warn">{{ scrapeError }}</div>
      </div>

      <!-- ===== Step 2: 房源信息 ===== -->
      <div class="an-card" v-if="showManual || scrapedData">
        <div class="an-step-label">Step 2</div>
        <h3>房源信息</h3>
        <p v-if="scrapedData" class="an-hint">以下数据已自动抓取，可核对修改</p>

        <div class="an-grid an-grid-3">
          <div class="an-field">
            <label>平台链接</label>
            <input v-model="form.url" type="url" placeholder="自动填入" />
          </div>
          <div class="an-field">
            <label>小区名称 <span class="an-req">*</span></label>
            <input v-model="form.community" type="text" placeholder="如：骏景花园" />
          </div>
          <div class="an-field">
            <label>区域</label>
            <select v-model="form.district">
              <option value="">请选择</option>
              <option value="天河">天河</option><option value="海珠">海珠</option>
              <option value="番禺">番禺</option><option value="越秀">越秀</option>
              <option value="荔湾">荔湾</option><option value="白云">白云</option>
            </select>
          </div>
        </div>

        <div class="an-grid an-grid-3">
          <div class="an-field">
            <label>月租（元）</label>
            <input v-model.number="form.rent" type="number" placeholder="2800" min="0" />
          </div>
          <div class="an-field">
            <label>户型</label>
            <select v-model="form.layout">
              <option value="">请选择</option>
              <option value="1室0厅">1室0厅</option><option value="1室1厅">1室1厅</option>
              <option value="2室1厅">2室1厅</option><option value="2室2厅">2室2厅</option>
              <option value="3室1厅">3室1厅</option><option value="3室2厅">3室2厅</option>
              <option value="4室2厅">4室2厅</option>
            </select>
          </div>
          <div class="an-field">
            <label>面积（㎡）</label>
            <input v-model.number="form.area" type="number" placeholder="85" min="0" />
          </div>
        </div>

        <div class="an-grid an-grid-4">
          <div class="an-field">
            <label>楼层</label>
            <input v-model="form.floor" type="text" placeholder="12" />
          </div>
          <div class="an-field">
            <label>总楼层</label>
            <input v-model="form.total_floors" type="text" placeholder="30" />
          </div>
          <div class="an-field">
            <label>朝向</label>
            <select v-model="form.orientation">
              <option value="">请选择</option>
              <option value="东">东</option><option value="南">南</option>
              <option value="西">西</option><option value="北">北</option>
              <option value="东南">东南</option><option value="西南">西南</option>
              <option value="东北">东北</option><option value="西北">西北</option>
              <option value="南北">南北</option>
            </select>
          </div>
          <div class="an-field">
            <label>通勤目的地</label>
            <input v-model="form.commute_destination" type="text" placeholder="如：体育西路" />
          </div>
        </div>

        <div class="an-grid an-grid-2">
          <div class="an-field">
            <label>临街情况</label>
            <div class="an-toggle">
              <button :class="{ active: form.street_facing === true }" @click="form.street_facing = true">临街</button>
              <button :class="{ active: form.street_facing === false }" @click="form.street_facing = false">不临街</button>
              <button :class="{ active: form.street_facing === null }" @click="form.street_facing = null">未知</button>
            </div>
          </div>
          <div class="an-field">
            <label>楼下商铺</label>
            <div class="an-toggle">
              <button :class="{ active: form.ground_floor_shop === true }" @click="form.ground_floor_shop = true">有</button>
              <button :class="{ active: form.ground_floor_shop === false }" @click="form.ground_floor_shop = false">无</button>
              <button :class="{ active: form.ground_floor_shop === null }" @click="form.ground_floor_shop = null">未知</button>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== Step 3: 评价补充 ===== -->
      <div class="an-card" v-if="showManual || scrapedData">
        <div class="an-step-label">Step 3</div>
        <h3>补充评价</h3>
        <p>从 58同城评论区、小红书、抖音等平台收集的租客真实评价，粘贴到这里。越多越好，AI 能分析得更准。</p>
        <textarea
          v-model="form.review_text"
          class="an-textarea"
          rows="5"
          placeholder="从各平台收集到的真实租客评价，粘贴到这里…&#10;例如：&#10;· 小红书用户 @xxx：这个小区楼下有烧烤摊晚上很吵&#10;· 58评论：房东人不错维修及时，但押金退房扣了300&#10;· 抖音评论区：附近没地铁站，通勤不太方便"
        ></textarea>
      </div>

      <!-- ===== 错误提示 ===== -->
      <div v-if="errorMessage" class="an-card an-card-error">
        <span class="an-error-icon">⚠️</span>
        <span>{{ errorMessage }}</span>
      </div>

      <!-- ===== 提交 ===== -->
      <div class="an-actions" v-if="showManual || scrapedData">
        <button class="an-btn-outline" @click="handleReset" :disabled="submitting">清空重填</button>
        <button class="an-btn-primary an-btn-lg" :disabled="submitting" @click="handleSubmit">
          <span v-if="submitting" class="an-spin"></span>
          {{ submitting ? 'AI 分析中…' : '开始 AI 风险评估' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { createAssessment } from '../api/client.js'

const router = useRouter()

const urlInput = ref('')
// Track which step user has reached
const currentStep = computed(() => {
  if (form.community || form.district || form.rent) return 3
  if (showManual.value || scrapedData.value) return 2
  return 1
})
const scraping = ref(false)
const scrapeError = ref('')
const scrapedData = ref(null)
const showManual = ref(false)
const submitting = ref(false)
const errorMessage = ref('')

const form = reactive({
  url: '', community: '', district: '', rent: null,
  layout: '', area: null, floor: '', total_floors: '',
  orientation: '', street_facing: null, ground_floor_shop: null,
  commute_destination: '', review_text: '',
})

function applyScraped(data) {
  if (!data) return
  if (data.url) form.url = data.url
  if (data.community) form.community = data.community
  if (data.district) form.district = data.district
  if (data.price) form.rent = data.price
  if (data.layout) form.layout = data.layout
  if (data.area) form.area = data.area
  if (data.floor) form.floor = data.floor
  if (data.total_floors) form.total_floors = data.total_floors
  if (data.orientation) form.orientation = data.orientation
  if (data.reviews && data.reviews.length) {
    form.review_text = data.reviews.map(r => `· [${r.platform}] ${r.content}`).join('\n')
  }
}

async function handleScrape() {
  scrapeError.value = ''
  scraping.value = true
  try {
    const resp = await fetch('/api/v1/assessments/scrape', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: urlInput.value.trim() }),
    })
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}))
      throw new Error(err.detail || '抓取失败')
    }
    const data = await resp.json()
    scrapedData.value = data
    applyScraped(data)
    showManual.value = true
  } catch (e) {
    scrapeError.value = e.message || '链接抓取失败，请手动填写信息'
    showManual.value = true
  } finally {
    scraping.value = false
  }
}

function toNum(v) {
  if (v === null || v === undefined || v === '') return undefined
  const n = Number(v)
  return Number.isNaN(n) ? undefined : n
}

function buildPayload() {
  const p = {}
  if (form.url) p.source_url = form.url
  if (form.community) p.community = form.community
  if (form.district) p.district = form.district
  if (form.rent !== null && form.rent !== '') p.price = toNum(form.rent)
  if (form.layout) p.layout = form.layout
  if (form.area !== null && form.area !== '') p.area = toNum(form.area)
  if (form.floor && form.floor !== '') p.floor = toNum(form.floor)
  if (form.total_floors && form.total_floors !== '') p.total_floors = toNum(form.total_floors)
  if (form.orientation) p.orientation = form.orientation
  if (form.street_facing === true) p.distance_to_street = 20
  else if (form.street_facing === false) p.distance_to_street = 200
  if (form.ground_floor_shop !== null) p.has_business_below = form.ground_floor_shop
  if (form.commute_destination) p.commute_destination = form.commute_destination
  if (form.review_text) p.reviews = [{ platform: 'user_input', content: form.review_text }]
  // title auto-gen
  const community = form.community || ''
  const district = form.district || ''
  p.title = [district, community].filter(Boolean).join('') + '租房评估'
  return p
}

async function handleSubmit() {
  errorMessage.value = ''
  submitting.value = true
  try {
    const payload = buildPayload()
    const result = await createAssessment(payload)
    router.push(result.detail_url)
  } catch (err) {
    const detail = err?.response?.data?.detail
    if (Array.isArray(detail)) errorMessage.value = detail.map(d => d.msg).join('；')
    else if (typeof detail === 'string') errorMessage.value = detail
    else errorMessage.value = err.message || '提交失败'
  } finally {
    submitting.value = false
  }
}

function handleReset() {
  Object.assign(form, {
    url: '', community: '', district: '', rent: null,
    layout: '', area: null, floor: '', total_floors: '',
    orientation: '', street_facing: null, ground_floor_shop: null,
    commute_destination: '', review_text: '',
  })
  urlInput.value = ''
  scrapedData.value = null
  scrapeError.value = ''
  errorMessage.value = ''
}
</script>

<style scoped>
.assess-new { margin: -24px -20px; }

/* ── Hero ── */
.an-hero {
  background: linear-gradient(160deg, #FEF9E7 0%, #FFF7ED 40%, #FFFBF5 70%, #fff 100%);
  padding: 56px 24px 60px; text-align: center; position: relative; overflow: hidden;
  border-bottom: 1px solid #FDE68A33;
}
.an-hero::before {
  content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
  background: radial-gradient(circle at 30% 40%, rgba(251,191,36,0.06) 0%, transparent 50%),
              radial-gradient(circle at 70% 60%, rgba(245,158,11,0.04) 0%, transparent 50%);
}
.an-hero > * { position: relative; z-index: 1; }
.an-hero-badge {
  display: inline-block; padding: 5px 18px; margin-bottom: 16px;
  background: rgba(245,158,11,0.12); color: #B45309;
  border-radius: 100px; font-size: 13px; font-weight: 700;
  letter-spacing: 0.5px;
}
.an-hero h1 { font-size: 34px; font-weight: 800; color: #1F2937; margin-bottom: 12px; }
.an-hero h1 span { background: linear-gradient(135deg, #F59E0B, #EA580C); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.an-hero p { font-size: 16px; color: #9CA3AF; max-width: 540px; margin: 0 auto; line-height: 1.8; }

/* ── Body ── */
.an-body { max-width: 780px; margin: 0 auto; padding: 36px 24px 64px; }

/* ── Step Progress ── */
.step-progress {
  display: flex; align-items: center; justify-content: center;
  gap: 0; margin-bottom: 24px; padding: 0 40px;
}
.step-dot {
  width: 34px; height: 34px; border-radius: 50%;
  background: #F3F4F6; color: #9CA3AF;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700; transition: all .3s;
  flex-shrink: 0;
}
.step-dot.completed { background: var(--primary); color: #fff; }
.step-dot.active { background: #fff; border: 2px solid var(--primary); color: var(--primary); }
.step-line {
  height: 2px; flex: 1; min-width: 30px;
  background: #E5E7EB; transition: background .3s;
}
.step-line.completed { background: var(--primary); }

/* ── Card ── */
.an-card {
  background: #fff; border-radius: 16px; padding: 28px 32px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.04);
  margin-bottom: 20px;
}
.an-card-error { background: #FEF2F2; border: 1px solid #FECACA; color: #991B1B; display: flex; gap: 10px; align-items: flex-start; }
.an-error-icon { flex-shrink: 0; margin-top: 2px; }
.an-step-label {
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 1.5px; color: #F59E0B; margin-bottom: 6px;
}
.an-card h3 { font-size: 18px; font-weight: 700; margin-bottom: 4px; color: #1F2937; }
.an-card > p { font-size: 14px; color: #9CA3AF; margin-bottom: 18px; }
.an-hint { color: #10B981 !important; font-weight: 500; }

/* ── URL Row ── */
.an-url-card { padding-bottom: 24px; }
.an-url-row {
  display: flex; gap: 10px; margin-top: 16px;
}
.an-url-row input {
  flex: 1; padding: 13px 18px; border: 1.5px solid #E5E7EB;
  border-radius: 12px; font-size: 15px; outline: none; color: #1F2937;
  transition: border-color .2s, box-shadow .2s; font-family: inherit;
}
.an-url-row input:focus { border-color: #F59E0B; box-shadow: 0 0 0 3px rgba(245,158,11,0.1); }
.an-url-row input::placeholder { color: #D1D5DB; }
.an-url-row input:disabled { background: #F9FAFB; }

/* ── Buttons ── */
.an-btn-primary {
  padding: 13px 28px; border: none; border-radius: 12px;
  background: linear-gradient(135deg, #F59E0B, #EA580C); color: #fff;
  font-size: 15px; font-weight: 700; cursor: pointer; white-space: nowrap;
  transition: transform .15s, box-shadow .2s;
}
.an-btn-primary:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(245,158,11,0.3); }
.an-btn-primary:disabled { opacity: 0.55; cursor: not-allowed; }
.an-btn-lg { padding: 16px 48px; font-size: 17px; border-radius: 14px; }
.an-btn-outline {
  padding: 13px 28px; border: 1.5px solid #E5E7EB; border-radius: 12px;
  background: #fff; font-size: 15px; font-weight: 600; color: #6B7280; cursor: pointer;
  transition: all .2s;
}
.an-btn-outline:hover:not(:disabled) { border-color: #9CA3AF; color: #1F2937; }
.an-btn-outline:disabled { opacity: 0.5; cursor: not-allowed; }
.an-btn-text {
  padding: 13px 20px; border: none; background: none; font-size: 14px;
  color: #9CA3AF; cursor: pointer; transition: color .2s; white-space: nowrap;
}
.an-btn-text:hover { color: #6B7280; }

/* ── Form Grid ── */
.an-grid { display: grid; gap: 14px; margin-bottom: 14px; }
.an-grid-2 { grid-template-columns: 1fr 1fr; }
.an-grid-3 { grid-template-columns: repeat(3, 1fr); }
.an-grid-4 { grid-template-columns: repeat(4, 1fr); }
.an-field {
  display: flex; flex-direction: column; min-width: 0;
}
.an-field label {
  font-size: 13px; font-weight: 600; color: #6B7280; margin-bottom: 6px;
}
.an-req { color: #EF4444; }
.an-field input, .an-field select {
  padding: 11px 14px; border: 1.5px solid #E5E7EB; border-radius: 10px;
  font-size: 14px; outline: none; color: #1F2937; font-family: inherit;
  background: #fff; transition: border-color .2s, box-shadow .2s;
}
.an-field input:focus, .an-field select:focus { border-color: #F59E0B; box-shadow: 0 0 0 3px rgba(245,158,11,0.08); }
.an-field input::placeholder { color: #D1D5DB; }

/* ── Toggle ── */
.an-toggle { display: flex; gap: 4px; background: #F3F4F6; border-radius: 10px; padding: 4px; }
.an-toggle button {
  flex: 1; padding: 8px 12px; border: none; background: none;
  border-radius: 8px; font-size: 13px; font-weight: 600; color: #6B7280;
  cursor: pointer; transition: all .2s;
}
.an-toggle button.active { background: #fff; color: #1F2937; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }

/* ── Textarea ── */
.an-textarea {
  width: 100%; padding: 14px 16px; border: 1.5px solid #E5E7EB; border-radius: 12px;
  font-size: 14px; outline: none; color: #1F2937; font-family: inherit;
  resize: vertical; min-height: 120px; line-height: 1.8; box-sizing: border-box;
  transition: border-color .2s, box-shadow .2s;
}
.an-textarea:focus { border-color: #F59E0B; box-shadow: 0 0 0 3px rgba(245,158,11,0.08); }
.an-textarea::placeholder { color: #D1D5DB; font-size: 13px; }

/* ── Messages ── */
.an-msg { font-size: 14px; padding: 10px 14px; border-radius: 10px; margin-top: 14px; }
.an-msg-warn { background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }

/* ── Actions ── */
.an-actions { display: flex; justify-content: flex-end; gap: 12px; }

/* ── Spinner ── */
.an-spin {
  display: inline-block; width: 15px; height: 15px;
  border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff;
  border-radius: 50%; animation: an-spin .6s linear infinite;
  margin-right: 8px; vertical-align: middle;
}
@keyframes an-spin { to { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .an-hero { padding: 40px 20px 44px; }
  .an-hero h1 { font-size: 26px; }
  .an-grid-2, .an-grid-3, .an-grid-4 { grid-template-columns: 1fr 1fr; }
  .an-url-row { flex-wrap: wrap; }
  .an-url-row .an-btn-primary, .an-url-row .an-btn-text { flex: 1; text-align: center; justify-content: center; }
  .an-card { padding: 22px 18px; }
  .an-actions { flex-direction: column; }
  .an-actions .an-btn-primary, .an-actions .an-btn-outline { width: 100%; text-align: center; }
}
@media (max-width: 480px) {
  .an-grid-2, .an-grid-3, .an-grid-4 { grid-template-columns: 1fr; }
}
</style>
