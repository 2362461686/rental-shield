<template>
  <div class="assess-view">
    <!-- 页面标题 -->
    <section class="assess-hero">
      <h1>新建租房<span>评估</span></h1>
      <p>填写房源信息，AI 帮你做一次全面的风险体检</p>
    </section>

    <!-- 表单区域 -->
    <div class="assess-form-wrapper">
      <form class="assess-form" @submit.prevent="handleSubmit">

        <!-- 一、基本信息 -->
        <fieldset class="form-section">
          <legend class="form-section-title">基本信息</legend>

          <div class="form-group form-group-full">
            <label>房源标题 <span class="optional">（选填）</span></label>
            <input v-model="form.title" type="text" placeholder="如：天河区骏景花园精装三房 近BRT" />
          </div>

          <div class="form-group form-group-full">
            <label>房源链接 <span class="optional">（选填）</span></label>
            <input v-model="form.url" type="url" placeholder="如：https://gz.58.com/zufang/..." />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>小区名</label>
              <input v-model="form.community" type="text" placeholder="如：骏景花园" />
            </div>
            <div class="form-group">
              <label>区域</label>
              <select v-model="form.district">
                <option value="">请选择</option>
                <option value="天河">天河</option>
                <option value="海珠">海珠</option>
                <option value="番禺">番禺</option>
                <option value="越秀">越秀</option>
                <option value="荔湾">荔湾</option>
                <option value="白云">白云</option>
              </select>
            </div>
            <div class="form-group">
              <label>月租（元）</label>
              <input v-model.number="form.rent" type="number" placeholder="如：2800" min="0" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>户型</label>
              <select v-model="form.layout">
                <option value="">请选择</option>
                <option value="1室0厅">1室0厅</option>
                <option value="1室1厅">1室1厅</option>
                <option value="2室1厅">2室1厅</option>
                <option value="2室2厅">2室2厅</option>
                <option value="3室1厅">3室1厅</option>
                <option value="3室2厅">3室2厅</option>
                <option value="4室2厅">4室2厅</option>
              </select>
            </div>
            <div class="form-group">
              <label>面积（㎡）</label>
              <input v-model.number="form.area" type="number" placeholder="如：85" min="0" />
            </div>
            <div class="form-group">
              <label>楼层</label>
              <input v-model="form.floor" type="text" placeholder="如：12" />
            </div>
            <div class="form-group">
              <label>总楼层</label>
              <input v-model="form.total_floors" type="text" placeholder="如：30" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>朝向</label>
              <select v-model="form.orientation">
                <option value="">请选择</option>
                <option value="东">东</option>
                <option value="南">南</option>
                <option value="西">西</option>
                <option value="北">北</option>
                <option value="东南">东南</option>
                <option value="西南">西南</option>
                <option value="东北">东北</option>
                <option value="西北">西北</option>
                <option value="南北">南北</option>
              </select>
            </div>
          </div>
        </fieldset>

        <!-- 二、环境因素 -->
        <fieldset class="form-section">
          <legend class="form-section-title">环境因素</legend>

          <div class="form-row">
            <div class="form-group">
              <label>是否临街</label>
              <div class="radio-group">
                <label class="radio-option">
                  <input v-model="form.street_facing" type="radio" :value="true" />
                  <span class="radio-label">是</span>
                </label>
                <label class="radio-option">
                  <input v-model="form.street_facing" type="radio" :value="false" />
                  <span class="radio-label">否</span>
                </label>
              </div>
            </div>
            <div class="form-group">
              <label>是否楼下商铺</label>
              <div class="radio-group">
                <label class="radio-option">
                  <input v-model="form.ground_floor_shop" type="radio" :value="true" />
                  <span class="radio-label">是</span>
                </label>
                <label class="radio-option">
                  <input v-model="form.ground_floor_shop" type="radio" :value="false" />
                  <span class="radio-label">否</span>
                </label>
              </div>
            </div>
          </div>
        </fieldset>

        <!-- 三、通勤信息 -->
        <fieldset class="form-section">
          <legend class="form-section-title">通勤信息</legend>
          <div class="form-group form-group-full">
            <label>通勤目的地 <span class="optional">（选填）</span></label>
            <input v-model="form.commute_destination" type="text" placeholder="如：天河区体育西路地铁站" />
          </div>
        </fieldset>

        <!-- 四、评价文本 -->
        <fieldset class="form-section">
          <legend class="form-section-title">评价文本</legend>
          <div class="form-group form-group-full">
            <label>租客评价 / 看房笔记 <span class="optional">（选填）</span></label>
            <textarea v-model="form.review_text" rows="6" placeholder="粘贴你在各平台看到的租客评价，或者你实地看房后的笔记……多段文本分行输入即可，AI 会自动提取关键信息。"></textarea>
          </div>
        </fieldset>

        <!-- 提交按钮 -->
        <div class="form-actions">
          <button type="button" class="btn-reset" @click="handleReset">重置</button>
          <button type="submit" class="btn-submit">提交评估</button>
        </div>

        <!-- 提交后的 payload 展示 -->
        <div v-if="submittedPayload" class="payload-display">
          <h3>提交的 Payload（前端打印，未接后端）</h3>
          <pre>{{ submittedPayload }}</pre>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'

const form = reactive({
  title: '',
  url: '',
  community: '',
  district: '',
  rent: null,
  layout: '',
  area: null,
  floor: '',
  total_floors: '',
  orientation: '',
  street_facing: null,
  ground_floor_shop: null,
  commute_destination: '',
  review_text: '',
})

const submittedPayload = ref(null)

function buildPayload() {
  const p = {}
  if (form.title) p.title = form.title
  if (form.url) p.url = form.url
  if (form.community) p.community = form.community
  if (form.district) p.district = form.district
  if (form.rent !== null) p.rent = form.rent
  if (form.layout) p.layout = form.layout
  if (form.area !== null) p.area = form.area
  if (form.floor) p.floor = form.floor
  if (form.total_floors) p.total_floors = form.total_floors
  if (form.orientation) p.orientation = form.orientation
  if (form.street_facing !== null) p.street_facing = form.street_facing
  if (form.ground_floor_shop !== null) p.ground_floor_shop = form.ground_floor_shop
  if (form.commute_destination) p.commute_destination = form.commute_destination
  if (form.review_text) p.review_text = form.review_text
  return p
}

function handleSubmit() {
  const payload = buildPayload()
  submittedPayload.value = JSON.stringify(payload, null, 2)
  console.log('[AssessView] 提交的 payload:', payload)
}

function handleReset() {
  Object.assign(form, {
    title: '', url: '', community: '', district: '', rent: null,
    layout: '', area: null, floor: '', total_floors: '',
    orientation: '', street_facing: null, ground_floor_shop: null,
    commute_destination: '', review_text: '',
  })
  submittedPayload.value = null
}
</script>

<style scoped>
.assess-view { margin: -24px -20px; }

/* ===== Hero ===== */
.assess-hero {
  background: linear-gradient(160deg, #FEF3C7 0%, #FFEDD5 40%, #FEF7ED 70%, #fff 100%);
  padding: 48px 24px 52px; text-align: center; position: relative; overflow: hidden;
}
.assess-hero::before {
  content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
  background: radial-gradient(circle at 30% 40%, rgba(251,191,36,0.1) 0%, transparent 50%),
              radial-gradient(circle at 70% 60%, rgba(245,158,11,0.06) 0%, transparent 50%);
}
.assess-hero > * { position: relative; z-index: 1; }
.assess-hero h1 { font-size: 32px; font-weight: 800; color: var(--text); margin-bottom: 10px; }
.assess-hero h1 span { background: var(--primary-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.assess-hero p { font-size: 16px; color: var(--text-secondary); }

/* ===== Form Wrapper ===== */
.assess-form-wrapper { max-width: 800px; margin: -28px auto 48px; padding: 0 24px; position: relative; z-index: 2; }

.assess-form {
  background: #fff; border-radius: var(--radius); padding: 36px 32px;
  box-shadow: var(--shadow-lg);
}

/* ===== Form Sections ===== */
.form-section {
  border: none; padding: 0; margin-bottom: 32px;
}
.form-section-title {
  font-size: 16px; font-weight: 700; color: var(--text);
  padding-left: 14px; border-left: 4px solid var(--primary);
  margin-bottom: 20px;
}

/* ===== Form Groups ===== */
.form-group {
  display: flex; flex-direction: column; min-width: 0;
}
.form-group-full { grid-column: 1 / -1; }
.form-group label {
  font-size: 13px; font-weight: 600; color: var(--text-secondary);
  margin-bottom: 6px;
}
.form-group .optional { font-weight: 400; color: var(--text-muted); font-size: 12px; }
.form-group input[type="text"],
.form-group input[type="url"],
.form-group input[type="number"],
.form-group textarea,
.form-group select {
  padding: 10px 14px; border: 1.5px solid var(--border-strong);
  border-radius: var(--radius-xs); font-size: 14px; outline: none;
  background: #fff; color: var(--text);
  font-family: inherit; transition: border-color .2s, box-shadow .2s;
}
.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(245,158,11,0.1);
}
.form-group input::placeholder,
.form-group textarea::placeholder { color: var(--text-muted); font-size: 13px; }
.form-group textarea { resize: vertical; min-height: 100px; line-height: 1.7; }

/* ===== Form Row (multi-column) ===== */
.form-row {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px; margin-bottom: 18px;
}

/* ===== Radio Group ===== */
.radio-group { display: flex; gap: 16px; padding: 2px 0; }
.radio-option {
  display: flex; align-items: center; gap: 6px; cursor: pointer;
  font-size: 14px; color: var(--text);
}
.radio-option input[type="radio"] {
  accent-color: var(--primary); width: 16px; height: 16px; margin: 0;
}
.radio-label { user-select: none; }

/* ===== Actions ===== */
.form-actions {
  display: flex; justify-content: flex-end; gap: 12px;
  padding-top: 8px; border-top: 1px solid var(--border);
}
.btn-reset {
  padding: 12px 28px; border: 1.5px solid var(--border-strong);
  border-radius: var(--radius-sm); background: #fff;
  font-size: 14px; font-weight: 600; color: var(--text-secondary);
  transition: all .2s;
}
.btn-reset:hover { border-color: var(--text-secondary); color: var(--text); }
.btn-submit {
  padding: 12px 36px; border: none; border-radius: var(--radius-sm);
  background: var(--primary-gradient); color: #fff;
  font-size: 15px; font-weight: 700;
  transition: transform .15s, box-shadow .2s;
}
.btn-submit:hover { transform: scale(1.02); box-shadow: 0 4px 16px rgba(245,158,11,0.35); }

/* ===== Payload Display ===== */
.payload-display {
  margin-top: 28px; padding: 20px 24px;
  background: #F9FAFB; border-radius: var(--radius-sm);
  border: 1px solid var(--border-strong);
}
.payload-display h3 {
  font-size: 14px; font-weight: 700; color: var(--text); margin-bottom: 12px;
}
.payload-display pre {
  font-size: 13px; font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
  line-height: 1.7; color: var(--text); white-space: pre-wrap;
  overflow-x: auto;
}

@media (max-width: 768px) {
  .assess-hero { padding: 36px 20px 44px; }
  .assess-hero h1 { font-size: 26px; }
  .assess-form { padding: 24px 18px; }
  .form-row { grid-template-columns: 1fr; }
  .form-actions { flex-direction: column; }
  .btn-reset, .btn-submit { width: 100%; }
}
</style>
