<template>
  <div class="home-root">
    <!-- Hero -->
    <section class="hm-hero">
      <div class="hm-badge">AI 风险评估工具 · 帮你避开问题房源</div>
      <h1>租房前，先让 <span>AI 帮你探探路</span></h1>
      <p>
        输入看中的房源链接或小区名，AI 自动抓取房屋信息<br/>
        综合分析六类风险，生成真实可参考的评估报告
      </p>
      <div class="hm-search">
        <input v-model="q" placeholder="粘贴 58 / 贝壳房源链接，或输入小区名…" @keydown.enter="go" />
        <button @click="go">开始评估</button>
      </div>
      <div class="hm-stats">
        <div class="hm-stat"><em>50+</em> 房源</div>
        <div class="hm-dot">·</div>
        <div class="hm-stat"><em>145+</em> 条评论</div>
        <div class="hm-dot">·</div>
        <div class="hm-stat"><em>6</em> 个维度分析</div>
        <div class="hm-dot">·</div>
        <div class="hm-stat"><em>AI</em> 驱动</div>
      </div>
    </section>

    <!-- Feature Cards -->
    <section class="hm-features">
      <div class="hm-feat" v-for="f in features" :key="f.title">
        <span class="hm-feat-icon">{{ f.icon }}</span>
        <h4>{{ f.title }}</h4>
        <p>{{ f.desc }}</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const q = ref('')
function go() {
  router.push('/assess/new')
}

const features = [
  { icon: '🔗', title: '链接解析', desc: '粘贴 58 / 贝壳房源链接，自动抓取户型、价格、楼层等关键信息' },
  { icon: '🔍', title: '六维分析', desc: '噪音、采光、房东、押金、通勤、安全 —— 全方位风险扫描' },
  { icon: '🤖', title: 'AI 评估', desc: 'DeepSeek 大模型分析真实评论，识别隐藏风险，不靠关键词猜' },
  { icon: '📋', title: '证据报告', desc: '每条风险都附原始评论证据，不瞎编，让结论有据可查' },
]
</script>

<style scoped>
.home-root { margin: -24px -20px; }

/* ── Hero ── */
.hm-hero {
  background: linear-gradient(160deg, #FEF9E7 0%, #FFF7ED 35%, #FFFBF5 65%, #fff 100%);
  padding: 72px 24px 88px; text-align: center; position: relative; overflow: hidden;
}
.hm-hero::before {
  content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
  background: radial-gradient(circle at 30% 40%, rgba(251,191,36,0.08) 0%, transparent 50%),
              radial-gradient(circle at 70% 60%, rgba(245,158,11,0.05) 0%, transparent 50%);
}
.hm-hero > * { position: relative; z-index: 1; }
.hm-badge {
  display: inline-block; padding: 5px 18px; margin-bottom: 20px;
  background: rgba(245,158,11,0.12); color: #B45309;
  border-radius: 100px; font-size: 13px; font-weight: 700; letter-spacing: 0.3px;
}
.hm-hero h1 { font-size: 40px; font-weight: 800; color: #1F2937; margin-bottom: 16px; line-height: 1.35; }
.hm-hero h1 span { background: linear-gradient(135deg, #F59E0B, #EA580C); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hm-hero p { font-size: 17px; color: #9CA3AF; max-width: 520px; margin: 0 auto 36px; line-height: 1.8; }

.hm-search {
  max-width: 600px; margin: 0 auto; display: flex; gap: 6px;
  background: #fff; border-radius: 16px; padding: 6px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.06);
}
.hm-search input {
  flex: 1; border: none; outline: none; padding: 15px 22px;
  font-size: 16px; border-radius: 12px; color: #1F2937;
}
.hm-search input::placeholder { color: #D1D5DB; font-size: 15px; }
.hm-search button {
  background: linear-gradient(135deg, #F59E0B, #EA580C); color: #fff; border: none;
  padding: 15px 32px; border-radius: 12px; font-size: 16px; font-weight: 700;
  white-space: nowrap; transition: transform .15s, box-shadow .2s;
}
.hm-search button:hover { transform: scale(1.02); box-shadow: 0 4px 20px rgba(245,158,11,0.35); }

.hm-stats {
  display: flex; justify-content: center; align-items: center; gap: 12px; margin-top: 32px;
  color: #9CA3AF; font-size: 14px;
}
.hm-stat em { font-style: normal; font-weight: 700; color: #6B7280; }
.hm-dot { font-size: 10px; }

/* ── Features ── */
.hm-features {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;
  max-width: 1080px; margin: -44px auto 60px; padding: 0 24px; position: relative; z-index: 2;
}
.hm-feat {
  background: #fff; border-radius: 16px; padding: 28px 22px; text-align: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.04);
  transition: transform .25s, box-shadow .25s;
}
.hm-feat:hover { transform: translateY(-4px); box-shadow: 0 8px 30px rgba(0,0,0,0.08); }
.hm-feat-icon { font-size: 32px; display: block; margin-bottom: 10px; }
.hm-feat h4 { font-size: 16px; font-weight: 700; margin-bottom: 6px; color: #1F2937; }
.hm-feat p { font-size: 13px; color: #9CA3AF; line-height: 1.6; }

@media (max-width: 768px) {
  .hm-hero { padding: 48px 20px 64px; }
  .hm-hero h1 { font-size: 28px; }
  .hm-hero p { font-size: 15px; }
  .hm-search { flex-direction: column; padding: 10px; }
  .hm-search input { padding: 14px 18px; border: 1.5px solid #E5E7EB; border-radius: 10px; }
  .hm-search button { width: 100%; padding: 14px; border-radius: 10px; }
  .hm-stats { flex-wrap: wrap; gap: 8px 4px; }
  .hm-dot { display: none; }
  .hm-features { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 480px) {
  .hm-features { grid-template-columns: 1fr; }
}
</style>
