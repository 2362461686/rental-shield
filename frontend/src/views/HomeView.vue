<template>
  <div class="home-view">
    <!-- Hero: 定位声明 + 搜索 -->
    <section class="hero">
      <div class="hero-badge">AI驱动 · 应届生专属</div>
      <h1>租房<span>不踩坑</span>，用数据说话</h1>
      <p>聚合全网租客真实评价，AI 挖掘房东套路、评估居住环境、对比市场行情，帮你做出理性决策</p>
      <form class="hero-search" @submit.prevent="handleSearch">
        <input v-model="searchQuery" type="text" placeholder="输入小区名，如：骏景花园" />
        <button type="submit">搜口碑</button>
      </form>
      <div class="hero-stats">
        <div class="hero-stat"><strong>50+</strong> 房源</div>
        <div class="hero-stat"><strong>6</strong> 个区域</div>
        <div class="hero-stat"><strong>145+</strong> 条评论</div>
        <div class="hero-stat"><strong>AI</strong> 分析</div>
      </div>
    </section>

    <!-- 核心能力 (4 cards) -->
    <section class="core-features">
      <div class="core-feature card-review">
        <div class="core-feature-icon">&#x1F4DD;</div>
        <h3>评论挖掘</h3>
        <p>AI 自动提取隔音、采光、房东态度等 6 个维度的关键词，告别"靠感觉"</p>
        <div class="core-feature-tags">
          <span class="tag-pos">隔音好</span>
          <span class="tag-neg">押金纠纷</span>
          <span class="tag-pos">近地铁</span>
        </div>
      </div>
      <div class="core-feature card-risk">
        <div class="core-feature-icon">&#x26A0;&#xFE0F;</div>
        <h3>房东画像</h3>
        <p>识别高风险房东：押金不退、随意涨租、二房东转租、维修推诿、态度恶劣</p>
        <div class="core-feature-risk">
          <span class="risk-pill low">低风险</span>
          <span class="risk-pill mid">中风险</span>
          <span class="risk-pill high">高风险</span>
        </div>
      </div>
      <div class="core-feature card-env">
        <div class="core-feature-icon">&#x1F3E2;</div>
        <h3>环境模拟</h3>
        <p>日照时长 + 噪声分贝的物理量化，朝向、楼层、窗户、临街距离综合计算</p>
        <div class="core-feature-env">
          <span>&#x2600;&#xFE0F; 日照 优/良/中/差</span>
          <span>&#x1F50A; 隔音 优/良/中/差</span>
        </div>
      </div>
      <div class="core-feature card-price">
        <div class="core-feature-icon">&#x1F4B0;</div>
        <h3>价格分析</h3>
        <p>对比同区域同户型市场均价，判断是否被"杀猪"，历史价格走势一目了然</p>
        <div class="core-feature-price-info">
          市场参考 ±20% 合理区间
        </div>
      </div>
    </section>

    <!-- 区域概览 -->
    <section class="district-overview-section">
      <DistrictOverview />
    </section>

    <!-- 地铁线路 -->
    <section class="subway-section">
      <div class="section-header">
        <h3>广州地铁线路</h3>
        <p>选择线路筛选沿线房源</p>
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
      <div v-else class="subway-empty">点击上方线路查看地铁详情</div>
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
  padding: 64px 24px 100px; text-align: center; position: relative; overflow: hidden;
}
.hero::before {
  content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
  background: radial-gradient(circle at 30% 40%, rgba(251,191,36,0.12) 0%, transparent 50%),
              radial-gradient(circle at 70% 60%, rgba(245,158,11,0.08) 0%, transparent 50%);
}
.hero>* { position: relative; z-index: 1; }

.hero-badge {
  display: inline-block; padding: 6px 18px; margin-bottom: 20px;
  background: rgba(245,158,11,0.1); color: var(--primary-dark);
  border-radius: var(--radius-full); font-size: 13px; font-weight: 600;
}
.hero h1 { font-size: 44px; font-weight: 800; color: var(--text); margin-bottom: 18px; line-height: 1.3; }
.hero h1 span { background: var(--primary-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero p { font-size: 17px; color: var(--text-secondary); max-width: 580px; margin: 0 auto 36px; line-height: 1.7; }

.hero-search {
  max-width: 580px; margin: 0 auto; display: flex; gap: 6px;
  background: #fff; border-radius: var(--radius-xl); padding: 5px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.08);
}
.hero-search input {
  flex: 1; border: none; outline: none; padding: 14px 24px;
  font-size: 16px; border-radius: var(--radius-xl); color: var(--text);
}
.hero-search input::placeholder { color: var(--text-muted); }
.hero-search button {
  background: var(--primary-gradient); color: #fff; border: none;
  padding: 14px 36px; border-radius: var(--radius-xl);
  font-size: 16px; font-weight: 700; transition: transform .2s, box-shadow .2s;
}
.hero-search button:hover { transform: scale(1.02); box-shadow: 0 4px 20px rgba(245,158,11,0.4); }

.hero-stats {
  display: flex; justify-content: center; gap: 40px; margin-top: 40px;
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
.card-review::before { background: linear-gradient(90deg, #10B981, #34D399); }
.card-risk::before { background: linear-gradient(90deg, #EF4444, #F87171); }
.card-env::before { background: linear-gradient(90deg, #3B82F6, #60A5FA); }
.card-price::before { background: linear-gradient(90deg, #F59E0B, #FBBF24); }

.core-feature-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.core-feature-risk { display: flex; gap: 8px; }
.risk-pill { padding: 4px 14px; border-radius: var(--radius-full); font-size: 12px; font-weight: 600; }
.risk-pill.low { background: #D1FAE5; color: #065F46; }
.risk-pill.mid { background: #FEF3C7; color: #92400E; }
.risk-pill.high { background: #FEE2E2; color: #991B1B; }
.core-feature-env { display: flex; flex-direction: column; gap: 4px; font-size: 12px; color: var(--text-secondary); }
.core-feature-price-info { font-size: 12px; color: var(--primary); padding: 6px 12px; background: #FEF3C7; border-radius: var(--radius-sm); text-align: center; font-weight: 600; }

/* ===== District Overview ===== */
.district-overview-section { max-width: 1280px; margin: 0 auto 50px; padding: 0 24px; }

/* ===== Subway ===== */
.subway-section {
  max-width: 1280px; margin: 0 auto 50px; padding: 0 24px;
  background: #fff; border-radius: var(--radius); box-shadow: 0 4px 24px rgba(0,0,0,0.06);
}
.section-header { padding: 24px 28px 12px; }
.section-header h3 { font-size: 18px; font-weight: 700; color: var(--text); margin-bottom: 4px; }
.section-header p { font-size: 13px; color: var(--text-secondary); }
.subway-line-pills { padding: 0 28px 16px; display: flex; gap: 8px; flex-wrap: wrap; }
.subway-pill {
  padding: 7px 18px; border: 1.5px solid var(--border-strong); border-radius: var(--radius-full);
  background: #fff; font-size: 13px; font-weight: 500; color: var(--text-secondary);
  cursor: pointer; transition: all .2s;
}
.subway-pill:hover { border-color: var(--primary); color: var(--primary); }
.subway-empty {
  padding: 80px 20px; text-align: center; color: var(--text-secondary); font-size: 15px;
  background: #FAFAFA; border-radius: 0 0 var(--radius) var(--radius);
}

@media (max-width: 768px) {
  .hero { padding: 48px 20px 80px; }
  .hero h1 { font-size: 30px; }
  .hero p { font-size: 15px; }
  .hero-stats { gap: 20px; }
  .hero-stat strong { font-size: 22px; }
  .hero-search { flex-direction: column; border-radius: var(--radius); padding: 10px; }
  .hero-search input { border-radius: var(--radius-sm); border: 1.5px solid var(--border-strong); }
  .hero-search button { border-radius: var(--radius-sm); width: 100%; }
  .core-features { grid-template-columns: 1fr; padding: 0 20px; }
  .district-overview-section { padding: 0 20px; }
  .subway-section { padding: 0; border-radius: var(--radius); }
}
</style>
