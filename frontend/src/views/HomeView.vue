<template>
  <div class="home-view">
    <!-- Hero: 产品定位声明 + 搜索入口 -->
    <section class="hero">
      <div class="hero-badge">租房风险体检工具</div>
      <h1>给你的房源做一次<span>风险体检</span></h1>
      <p>
        导入真实房源链接、上传图片、粘贴评价文本，<br />
        AI 自动完成信息结构化、风险挖掘与通勤评估，生成综合决策建议
      </p>
      <form class="hero-search" @submit.prevent="handleSearch">
        <input v-model="searchQuery" type="text" placeholder="粘贴房源链接或输入小区名，如：骏景花园" />
        <button type="submit">开始体检</button>
      </form>

      <!-- 导入方式指示条 -->
      <div class="import-methods">
        <div class="import-method">
          <span class="import-icon">&#x1F517;</span>
          <span>房源链接</span>
        </div>
        <div class="import-method">
          <span class="import-icon">&#x1F4F7;</span>
          <span>上传图片</span>
        </div>
        <div class="import-method">
          <span class="import-icon">&#x1F4DD;</span>
          <span>粘贴评价</span>
        </div>
      </div>

      <div class="hero-stats">
        <div class="hero-stat"><strong>50+</strong> 房源</div>
        <div class="hero-stat"><strong>6</strong> 个区域</div>
        <div class="hero-stat"><strong>145+</strong> 条评论</div>
        <div class="hero-stat"><strong>AI</strong> 分析</div>
      </div>
    </section>

    <!-- 核心能力 (4 cards) - 重新定位 -->
    <section class="core-features">
      <div class="core-feature card-structure">
        <div class="core-feature-icon">&#x1F3E0;</div>
        <h3>房源信息结构化</h3>
        <p>导入58、贝壳等平台房源链接，AI 自动提取户型、面积、价格、配套设施等结构化信息</p>
        <div class="core-feature-tags">
          <span>户型解析</span>
          <span>面积采集</span>
          <span>配套提取</span>
        </div>
      </div>
      <div class="core-feature card-review">
        <div class="core-feature-icon">&#x1F50D;</div>
        <h3>评价风险提取</h3>
        <p>智能分析租客真实评价，识别房东套路、押金纠纷、维修推诿等风险信号，告别"靠感觉"</p>
        <div class="core-feature-risk">
          <span class="risk-pill low">低风险</span>
          <span class="risk-pill mid">中风险</span>
          <span class="risk-pill high">高风险</span>
        </div>
      </div>
      <div class="core-feature card-commute">
        <div class="core-feature-icon">&#x1F698;</div>
        <h3>通勤与环境评估</h3>
        <p>计算通勤时长、评估日照采光与噪声环境，量化居住体验，支持地铁线路辅助分析</p>
        <div class="core-feature-env">
          <span>&#x2600;&#xFE0F; 日照 优/良/中/差</span>
          <span>&#x1F50A; 隔音 优/良/中/差</span>
          <span>&#x1F3E2; 通勤 便捷/一般/不便</span>
        </div>
      </div>
      <div class="core-feature card-advice">
        <div class="core-feature-icon">&#x1F4CA;</div>
        <h3>综合决策建议</h3>
        <p>综合各项指标，AI 生成是否值得租住的决策建议，并推荐同区域更优替代方案</p>
        <div class="core-feature-advice-info">
          决策：推荐 / 可接受 / 谨慎 / 不推荐
        </div>
      </div>
    </section>

    <!-- 区域概览：保留原有功能 -->
    <section class="district-overview-section">
      <h3 class="section-heading">广州各区房源速览</h3>
      <DistrictOverview />
    </section>

    <!-- 地铁通勤辅助：功能保留但降低首页权重 -->
    <section class="subway-section">
      <div class="section-header">
        <h3>通勤辅助 · 地铁线路</h3>
        <p>选择地铁线路查看沿线房源分布（通勤评估参考工具）</p>
      </div>
      <div class="subway-line-pills">
        <button
          v-for="line in subwayLines"
          :key="line.name"
          class="subway-pill"
          :class="{ active: selectedLine === line.name }"
          :style="selectedLine === line.name ? { background: line.color, borderColor: line.color, color: '#fff' } : {}"
          @click="selectLine(line.name)"
        >
          {{ line.name }}
        </button>
      </div>
      <HouseMap
        v-if="selectedLine"
        mode="houses"
        :houses="[]"
        :show-subway="true"
        :subway-line="selectedLine"
      />
      <div v-else class="subway-empty">点击上方线路查看地铁沿线房源分布</div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import HouseMap from '../components/map/HouseMap.vue'
import DistrictOverview from '../components/search/DistrictOverview.vue'
import { fetchSubwayLines } from '../api/client.js'

const router = useRouter()
const searchQuery = ref('')
const subwayLines = ref([])
const selectedLine = ref('')

onMounted(async () => {
  try { subwayLines.value = await fetchSubwayLines() } catch {}
})

function handleSearch() {
  router.push({ path: '/search', query: searchQuery.value.trim() ? { q: searchQuery.value.trim() } : {} })
}

function selectLine(line) {
  selectedLine.value = selectedLine.value === line ? '' : line
}
</script>

<style scoped>
.home-view { margin: -24px -20px; }

/* ===== Hero ===== */
.hero {
  background: linear-gradient(160deg, #FEF3C7 0%, #FFEDD5 35%, #FEF7ED 65%, #fff 100%);
  padding: 64px 24px 80px; text-align: center; position: relative; overflow: hidden;
}
.hero::before {
  content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
  background: radial-gradient(circle at 30% 40%, rgba(251,191,36,0.12) 0%, transparent 50%),
              radial-gradient(circle at 70% 60%, rgba(245,158,11,0.08) 0%, transparent 50%);
}
.hero>* { position: relative; z-index: 1; }

.hero-badge {
  display: inline-block; padding: 6px 18px; margin-bottom: 20px;
  background: rgba(245,158,11,0.15); color: var(--primary-dark);
  border-radius: var(--radius-full); font-size: 13px; font-weight: 700;
  letter-spacing: 0.5px;
}
.hero h1 { font-size: 44px; font-weight: 800; color: var(--text); margin-bottom: 18px; line-height: 1.3; }
.hero h1 span { background: var(--primary-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero p { font-size: 17px; color: var(--text-secondary); max-width: 620px; margin: 0 auto 36px; line-height: 1.8; }

.hero-search {
  max-width: 600px; margin: 0 auto; display: flex; gap: 6px;
  background: #fff; border-radius: var(--radius-xl); padding: 5px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.08);
}
.hero-search input {
  flex: 1; border: none; outline: none; padding: 14px 24px;
  font-size: 16px; border-radius: var(--radius-xl); color: var(--text);
}
.hero-search input::placeholder { color: var(--text-muted); font-size: 15px; }
.hero-search button {
  background: var(--primary-gradient); color: #fff; border: none;
  padding: 14px 36px; border-radius: var(--radius-xl);
  font-size: 16px; font-weight: 700; transition: transform .2s, box-shadow .2s;
  white-space: nowrap;
}
.hero-search button:hover { transform: scale(1.02); box-shadow: 0 4px 20px rgba(245,158,11,0.4); }

/* ===== Import methods bar ===== */
.import-methods {
  display: flex; justify-content: center; gap: 32px; margin-top: 28px;
}
.import-method {
  display: flex; align-items: center; gap: 8px;
  font-size: 14px; color: var(--text-secondary); font-weight: 500;
  padding: 8px 18px; background: rgba(255,255,255,0.7);
  border-radius: var(--radius-full);
  border: 1px solid rgba(245,158,11,0.15);
  transition: transform .2s, box-shadow .2s;
}
.import-method:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(245,158,11,0.12);
  border-color: rgba(245,158,11,0.3);
}
.import-icon { font-size: 18px; }

.hero-stats {
  display: flex; justify-content: center; gap: 40px; margin-top: 36px;
}
.hero-stat { text-align: center; color: var(--text-secondary); font-size: 14px; }
.hero-stat strong { display: block; font-size: 28px; font-weight: 800; color: var(--text); margin-bottom: 2px; }

/* ===== Core Features ===== */
.core-features {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px;
  max-width: 1280px; margin: -40px auto 50px; padding: 0 24px; position: relative; z-index: 2;
}
.core-feature {
  background: #fff; border-radius: var(--radius); padding: 28px 22px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.06); transition: transform .25s, box-shadow .25s;
  position: relative; overflow: hidden;
}
.core-feature:hover { transform: translateY(-6px); box-shadow: 0 12px 40px rgba(0,0,0,0.1); }
.core-feature-icon { font-size: 32px; margin-bottom: 12px; }
.core-feature h3 { font-size: 17px; font-weight: 700; margin-bottom: 8px; color: var(--text); }
.core-feature p { font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 14px; }

/* Card-specific accent bars */
.core-feature::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; border-radius: var(--radius) var(--radius) 0 0; }
.card-structure::before { background: linear-gradient(90deg, #3B82F6, #60A5FA); }
.card-review::before { background: linear-gradient(90deg, #EF4444, #F87171); }
.card-commute::before { background: linear-gradient(90deg, #10B981, #34D399); }
.card-advice::before { background: linear-gradient(90deg, #8B5CF6, #A78BFA); }

.core-feature-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.core-feature-tags span {
  font-size: 11px; padding: 3px 10px; background: #EFF6FF;
  color: #1D4ED8; border-radius: var(--radius-full); font-weight: 500;
}
.core-feature-risk { display: flex; gap: 8px; }
.risk-pill { padding: 4px 14px; border-radius: var(--radius-full); font-size: 12px; font-weight: 600; }
.risk-pill.low { background: #D1FAE5; color: #065F46; }
.risk-pill.mid { background: #FEF3C7; color: #92400E; }
.risk-pill.high { background: #FEE2E2; color: #991B1B; }
.core-feature-env { display: flex; flex-direction: column; gap: 4px; font-size: 12px; color: var(--text-secondary); }
.core-feature-advice-info {
  font-size: 12px; color: #6D28D9; padding: 6px 12px;
  background: #F5F3FF; border-radius: var(--radius-sm); text-align: center; font-weight: 600;
}

/* ===== District Overview ===== */
.district-overview-section { max-width: 1280px; margin: 0 auto 50px; padding: 0 24px; }
.section-heading {
  font-size: 20px; font-weight: 700; margin-bottom: 16px;
  padding-left: 14px; border-left: 4px solid var(--primary);
  color: var(--text);
}

/* ===== Subway (通勤辅助) ===== */
.subway-section {
  max-width: 1280px; margin: 0 auto 50px; padding: 0 24px;
}
.subway-section .section-header { padding: 4px 0 12px; }
.subway-section .section-header h3 { font-size: 18px; font-weight: 700; color: var(--text); margin-bottom: 4px; }
.subway-section .section-header p { font-size: 13px; color: var(--text-secondary); }
.subway-line-pills { padding: 0 0 16px; display: flex; gap: 8px; flex-wrap: wrap; }
.subway-pill {
  padding: 7px 18px; border: 1.5px solid var(--border-strong); border-radius: var(--radius-full);
  background: #fff; font-size: 13px; font-weight: 500; color: var(--text-secondary);
  cursor: pointer; transition: all .2s;
}
.subway-pill:hover { border-color: var(--primary); color: var(--primary); }
.subway-empty {
  padding: 80px 20px; text-align: center; color: var(--text-secondary); font-size: 15px;
  background: #FAFAFA; border-radius: var(--radius);
}

@media (max-width: 768px) {
  .hero { padding: 48px 20px 60px; }
  .hero h1 { font-size: 30px; }
  .hero p { font-size: 15px; }
  .hero-stats { gap: 20px; }
  .hero-stat strong { font-size: 22px; }
  .hero-search { flex-direction: column; border-radius: var(--radius); padding: 10px; }
  .hero-search input { border-radius: var(--radius-sm); border: 1.5px solid var(--border-strong); }
  .hero-search button { border-radius: var(--radius-sm); width: 100%; }
  .import-methods { gap: 12px; }
  .core-features { grid-template-columns: 1fr; padding: 0 20px; }
  .district-overview-section { padding: 0 20px; }
  .subway-section { padding: 0 20px; }
}
</style>
