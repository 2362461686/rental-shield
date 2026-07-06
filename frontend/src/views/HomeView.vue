<template>
  <div class="home-root">
    <!-- Hero -->
    <section class="hm-hero">
      <div class="hm-badge">AI 风险评估工具 · 广州站</div>
      <h1>租房前，先让 <span>AI 帮你探探路</span></h1>
      <p>物理模拟日照噪音 + AI 六维风险分析 + 250+ 真实房源数据<br/>DeepSeek 做不到的，我们来</p>
      <div class="hm-search">
        <input v-model="q" placeholder="输入小区名查风险，如：骏景花园、祈福新邨…" @keydown.enter="go" />
        <button @click="go">开始评估</button>
      </div>
      <div class="hm-stats">
        <div class="hm-stat"><em>{{ stats.houses }}</em> 房源</div>
        <div class="hm-dot">·</div>
        <div class="hm-stat"><em>{{ stats.reviews }}</em> 条评论</div>
        <div class="hm-dot">·</div>
        <div class="hm-stat"><em>{{ stats.districts }}</em> 个区域</div>
        <div class="hm-dot">·</div>
        <div class="hm-stat"><em>{{ stats.communities }}</em> 个社区</div>
      </div>
    </section>

    <!-- Hot communities -->
    <section class="hm-section">
      <h2 class="hm-section-title">热门社区</h2>
      <div class="hm-communities">
        <div
          v-for="c in hotCommunities"
          :key="c.name"
          class="hm-community-card"
          @click="searchCommunity(c.name)"
        >
          <span class="hm-comm-name">{{ c.name }}</span>
          <span class="hm-comm-district">{{ c.district }}</span>
          <span class="hm-comm-count">{{ c.count }}套</span>
        </div>
      </div>
    </section>

    <!-- Feature Cards -->
    <section class="hm-section">
      <h2 class="hm-section-title">为什么选择安租</h2>
      <div class="hm-features">
        <div class="hm-feat" v-for="f in features" :key="f.title">
          <div class="hm-feat-icon-wrap">
            <div class="hm-feat-icon">{{ f.icon }}</div>
          </div>
          <h4>{{ f.title }}</h4>
          <p>{{ f.desc }}</p>
          <span class="hm-feat-tag">{{ f.tag }}</span>
        </div>
      </div>
    </section>

    <!-- How it works -->
    <section class="hm-section hm-steps-section">
      <h2 class="hm-section-title">三步开始</h2>
      <div class="hm-steps">
        <div class="hm-step">
          <div class="hm-step-num">1</div>
          <h4>输入房源信息</h4>
          <p>粘贴链接或填写小区名，AI 自动抓取</p>
        </div>
        <div class="hm-step-arrow">&rarr;</div>
        <div class="hm-step">
          <div class="hm-step-num">2</div>
          <h4>模拟 + 分析</h4>
          <p>物理环境模拟 + AI 评论挖掘</p>
        </div>
        <div class="hm-step-arrow">&rarr;</div>
        <div class="hm-step">
          <div class="hm-step-num">3</div>
          <h4>查看评估报告</h4>
          <p>量化风险评分 + 房东历史 + 最终建议</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchCommunityStats, fetchDistrictStats } from '../api/client.js'

const router = useRouter()
const q = ref('')

const stats = ref({ houses: 250, reviews: 750, districts: 10, communities: 0 })
const hotCommunities = ref([])

onMounted(async () => {
  try {
    // Load community stats for hot communities
    const communities = await fetchCommunityStats()
    if (communities && communities.length) {
      stats.value.communities = new Set(communities.map(c => c.community)).size
      hotCommunities.value = communities
        .sort((a, b) => (b.count || 0) - (a.count || 0))
        .slice(0, 8)
        .map(c => ({ name: c.community, district: c.district, count: c.count }))
    }

    // Load district stats for hero numbers
    const districtData = await fetchDistrictStats()
    if (districtData) {
      stats.value.houses = districtData.total_houses || 250
      stats.value.reviews = Math.floor((districtData.total_houses || 250) * 3)
      stats.value.districts = districtData.districts ? districtData.districts.length : 10
    }
  } catch (e) {
    // fallback
    if (hotCommunities.value.length === 0) {
      hotCommunities.value = [
        { name: '骏景花园', district: '天河', count: 3 },
        { name: '祈福新邨', district: '番禺', count: 3 },
        { name: '光大花园', district: '海珠', count: 3 },
        { name: '锦城花园', district: '越秀', count: 3 },
        { name: '岭南新世界', district: '白云', count: 5 },
        { name: '万科东荟城', district: '黄埔', count: 5 },
        { name: '碧桂园凤凰城', district: '增城', count: 5 },
        { name: '星河山海湾', district: '南沙', count: 5 },
      ]
    }
  }
})

function go() {
  const val = q.value.trim()
  if (val && (val.startsWith('http://') || val.startsWith('https://'))) {
    router.push('/assess/new')
  } else if (val) {
    router.push(`/search?keyword=${encodeURIComponent(val)}`)
  } else {
    router.push('/assess/new')
  }
}

function searchCommunity(name) {
  router.push(`/search?keyword=${encodeURIComponent(name)}`)
}

const features = [
  { icon: '☀️', title: '日照模拟', desc: '基于朝向、楼层、窗型计算真实日照时长，不是 AI 猜的', tag: '物理模拟' },
  { icon: '🔇', title: '噪音分析', desc: '建筑类型、临街距离、底商影响，精确到分贝', tag: '物理模拟' },
  { icon: '📊', title: '价格对比', desc: '250+房源真实价格数据 + 历史走势图', tag: '数据驱动' },
  { icon: '👤', title: '房东透视', desc: '跨房源投诉聚合，一个房东所有房源的风险一览', tag: '数据聚合' },
  { icon: '🤖', title: '评论挖掘', desc: 'DeepSeek AI 六维分析 + 每条风险附原始评论证据', tag: 'AI 增强' },
  { icon: '🗺️', title: '通勤计算', desc: '高德地图实时通勤时间 + 广州9条地铁线数据', tag: '实用工具' },
]
</script>

<style scoped>
.home-root { margin: -24px -20px; }

/* Hero */
.hm-hero {
  background: linear-gradient(160deg, #FEF9E7 0%, #FFF7ED 40%, #FFFBF5 70%, #fff 100%);
  padding: 80px 24px 100px; text-align: center; position: relative; overflow: hidden;
}
.hm-hero::before {
  content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
  background: radial-gradient(circle at 30% 35%, rgba(251,191,36,0.08) 0%, transparent 50%),
              radial-gradient(circle at 70% 65%, rgba(245,158,11,0.05) 0%, transparent 50%);
}
.hm-hero > * { position: relative; z-index: 1; }
.hm-badge { display: inline-block; padding: 5px 18px; margin-bottom: 20px; background: rgba(245,158,11,0.12); color: #B45309; border-radius: 100px; font-size: 13px; font-weight: 700; letter-spacing: .3px; }
.hm-hero h1 { font-size: 44px; font-weight: 800; color: #1F2937; margin-bottom: 16px; line-height: 1.3; }
.hm-hero h1 span { background: linear-gradient(135deg, #F59E0B, #EA580C); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hm-hero > p { font-size: 17px; color: #9CA3AF; max-width: 560px; margin: 0 auto 36px; line-height: 1.8; }

.hm-search {
  max-width: 600px; margin: 0 auto; display: flex; gap: 6px;
  background: #fff; border-radius: 16px; padding: 6px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.06);
}
.hm-search input { flex: 1; border: none; outline: none; padding: 15px 22px; font-size: 16px; border-radius: 12px; color: #1F2937; }
.hm-search input::placeholder { color: #D1D5DB; font-size: 15px; }
.hm-search button { background: linear-gradient(135deg, #F59E0B, #EA580C); color: #fff; border: none; padding: 15px 32px; border-radius: 12px; font-size: 16px; font-weight: 700; white-space: nowrap; transition: transform .15s, box-shadow .2s; }
.hm-search button:hover { transform: scale(1.02); box-shadow: 0 4px 20px rgba(245,158,11,0.35); }

.hm-stats { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 32px; color: #9CA3AF; font-size: 15px; flex-wrap: wrap; }
.hm-stat em { font-style: normal; font-weight: 700; color: #6B7280; font-size: 18px; }
.hm-dot { font-size: 10px; color: #D1D5DB; }

/* Sections */
.hm-section { max-width: 1080px; margin: 0 auto; padding: 48px 24px; }
.hm-section-title { font-size: 22px; font-weight: 800; color: #1F2937; margin-bottom: 24px; text-align: center; }

/* Communities */
.hm-communities { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 8px; -webkit-overflow-scrolling: touch; }
.hm-community-card { background: #fff; border-radius: var(--radius); padding: 16px 20px; min-width: 160px; cursor: pointer; box-shadow: var(--shadow-sm); transition: transform var(--transition), box-shadow var(--transition); display: flex; flex-direction: column; gap: 4px; }
.hm-community-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-lg); }
.hm-comm-name { font-size: 15px; font-weight: 700; color: var(--text); }
.hm-comm-district { font-size: 12px; color: var(--text-muted); }
.hm-comm-count { font-size: 12px; color: var(--primary); font-weight: 600; }

/* Features */
.hm-features { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.hm-feat { background: #fff; border-radius: var(--radius); padding: 28px 24px; box-shadow: var(--shadow-sm); transition: transform var(--transition), box-shadow var(--transition); position: relative; overflow: hidden; }
.hm-feat:hover { transform: translateY(-4px); box-shadow: var(--shadow-lg); }
.hm-feat-icon-wrap { width: 48px; height: 48px; border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; margin-bottom: 14px; background: var(--bg-warm); }
.hm-feat-icon { font-size: 24px; }
.hm-feat h4 { font-size: 16px; font-weight: 700; color: #1F2937; margin-bottom: 6px; }
.hm-feat p { font-size: 13px; color: #9CA3AF; line-height: 1.6; margin-bottom: 12px; }
.hm-feat-tag { display: inline-block; padding: 2px 10px; border-radius: var(--radius-full); font-size: 11px; font-weight: 600; background: var(--bg-warm); color: var(--primary-dark); }

/* Steps */
.hm-steps-section { padding-bottom: 64px; }
.hm-steps { display: flex; align-items: flex-start; justify-content: center; gap: 24px; }
.hm-step { background: #fff; border-radius: var(--radius); padding: 32px 24px; text-align: center; flex: 1; max-width: 280px; box-shadow: var(--shadow-sm); }
.hm-step-num { width: 40px; height: 40px; border-radius: 50%; background: var(--primary-gradient); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 700; margin: 0 auto 14px; }
.hm-step h4 { font-size: 16px; font-weight: 700; color: #1F2937; margin-bottom: 6px; }
.hm-step p { font-size: 13px; color: #9CA3AF; }
.hm-step-arrow { font-size: 24px; color: #D1D5DB; padding-top: 40px; flex-shrink: 0; }

@media (max-width: 768px) {
  .hm-hero { padding: 48px 20px 64px; }
  .hm-hero h1 { font-size: 28px; }
  .hm-search { flex-direction: column; padding: 10px; }
  .hm-search input { padding: 14px 18px; border: 1.5px solid #E5E7EB; border-radius: 10px; }
  .hm-search button { width: 100%; padding: 14px; border-radius: 10px; }
  .hm-features { grid-template-columns: 1fr 1fr; }
  .hm-steps { flex-direction: column; align-items: center; }
  .hm-step { max-width: 100%; width: 100%; }
  .hm-step-arrow { transform: rotate(90deg); padding-top: 0; }
}
@media (max-width: 480px) {
  .hm-features { grid-template-columns: 1fr; }
}
</style>
