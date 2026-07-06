# 安租 · AI 租房风险评估平台 · 广州站

基于 **物理模拟 + AI 评论挖掘 + 多平台实时爬虫** 的智能租房决策引擎。输入小区名或房源链接，AI 自动分析日照、噪音、房东风险、价格合理性，输出量化评估报告。

> 参照 [HouseSearch](https://github.com/liguobao/HouseSearch) 的爬虫 + 地图驱动架构，专注「数据采集 + 分析决策」而非简单房源列表。

## 核心差异化（DeepSeek 客户端做不到的）

| 能力 | 说明 |
|------|------|
| **物理环境模拟** | 朝向×楼层×窗型 → 日照时长；建筑类型×临街距离 → 噪音分贝（定量计算，非 AI 猜测） |
| **房东跨房源透视** | 一个房东所有房源的风险聚合，投诉模式可视化 |
| **社区数据聚合** | 67 社区均价统计、区域对比，价格历史走势图 |
| **多平台实时爬虫** | 豆瓣租房小组定时抓取，后台每 30 分钟自动更新 |
| **交互式地图筛选** | Leaflet 地图 + 列表双视图，地铁线/通勤/价格多维度筛选 |
| **AI 对话助手** | 右下角 DeepSeek 浮窗，随时咨询租房问题 |

## 全家桶功能

| 模块 | 说明 |
|------|------|
| AI 评论挖掘 | DeepSeek 六维分析（噪音/采光/房东/押金/通勤/安全），每条风险附原始评论证据 |
| 环境物理模拟 | 日照时长 + 噪音分贝 + 价格合理性 三项量化评估 |
| 房东风险评估 | 押金不退、随意涨租、二房东转租等 5 类风险，跨房源投诉聚合 |
| 通勤计算 | 高德公共交通 API，9 条广州地铁线数据，实时通勤时间 |
| 搜索筛选 | 区域、户型、价格、地铁线、关键词多维筛选 + 分页 |
| 评估向导 | 粘贴链接自动抓取 → 手动补充 → AI 分析 → 生成报告 |
| 收藏系统 | 收藏/取消 + 列表查看 |
| 搜索建议 | Levenshtein 模糊匹配，输入"骏景"自动推荐"骏景花园" |

## 技术架构

```
┌───────────────────────────────────────────────────────┐
│                  Vue 3 SPA 前端                        │
│  Pinia · Vue Router · Leaflet · Axios · SVG 图表       │
│  HomeView / SearchView / DetailView / AssessView      │
│  FavoritesView · AI 助手浮窗 · 错误边界 · 移动端适配     │
├───────────────────────────────────────────────────────┤
│                  FastAPI 后端                          │
│  /houses /analysis /agents /assessments /commute      │
│  /subway /favorites /districts /crawler /chat         │
├───────────────────────────────────────────────────────┤
│                  爬虫引擎 (crawlers/)                   │
│  DoubanCrawler · BeikeCrawler · LianjiaCrawler       │
│  CrawlerManager · 后台调度器 (30min/次)                │
├───────────────────────────────────────────────────────┤
│                  业务服务层                             │
│  日照模拟 · 噪声模拟 · AI Agent(3个) · 地理编码         │
│  通勤计算 · 地铁服务 · 评论分析 · 社区统计              │
├───────────────────────────────────────────────────────┤
│                  数据持久层                             │
│  SQLAlchemy ORM · SQLite                              │
│  houses / reviews / landlords / price_history         │
│  districts / favorites / workspace_configs             │
├───────────────────────────────────────────────────────┤
│                  外部服务                               │
│  DeepSeek API · 高德地图 API · 豆瓣公开数据             │
└───────────────────────────────────────────────────────┘
```

## 快速开始

### 1. 克隆 & 安装

```bash
git clone https://github.com/2362461686/rental-shield.git
cd rental-shield

# 后端
pip install -r backend/requirements.txt
pip install curl_cffi

# 前端
cd frontend && npm install && cd ..
```

### 2. 初始化数据

```bash
python seed_data.py   # 生成 500 套广州真实小区房源数据
```

### 3. 配置 API Key

```bash
# DeepSeek AI（不配置则使用规则引擎降级，AI 助手无法使用）
export DEEPSEEK_API_KEY="sk-xxx"

# 高德地图（不配置则使用直线距离估算）
export AMAP_API_KEY="xxx"
```

### 4. 启动

```bash
# 终端 1 — 后端（服务前端静态文件 + API）
uvicorn backend.main:app --port 8000

# 终端 2 — 前端热重载开发（可选）
cd frontend && npm run dev
```

浏览器访问 **http://localhost:8000**（生产）或 **http://localhost:5173**（开发）

## 爬虫

后台爬虫每分钟自动从豆瓣租房小组抓取房源，数据实时入库。

```bash
# 手动触发
curl -X POST http://localhost:8000/api/v1/crawler/run/douban?pages=3

# 查看状态
curl http://localhost:8000/api/v1/crawler/status

# 列出所有爬虫源
curl http://localhost:8000/api/v1/crawler/sources
```

## 项目结构

```
rental-shield/
├── config.py / db.py               # 全局配置 & DB 工具
├── utils.py / agents.py            # 物理模拟 & AI Agent
├── seed_data.py                    # 种子数据（500 套房源）
├── rental.db                       # SQLite 数据库
│
├── backend/
│   ├── main.py                     # FastAPI 入口 + 后台爬虫启动
│   ├── config.py                   # 后端配置
│   ├── db/
│   │   ├── database.py / models.py / queries.py / migrations.py
│   ├── models/                     # Pydantic schemas
│   ├── routers/
│   │   ├── houses.py               # 房源 + 社区统计 + 搜索建议
│   │   ├── analysis.py             # 物理模拟
│   │   ├── agent_routes.py         # AI Agent
│   │   ├── assessments.py          # 评估向导
│   │   ├── districts.py            # 区域统计
│   │   ├── commute.py              # 通勤计算
│   │   ├── subway.py               # 地铁数据
│   │   ├── favorites.py            # 收藏
│   │   ├── crawler.py              # 爬虫管理
│   │   └── chat.py                 # AI 对话助手
│   ├── services/                   # 业务逻辑
│   └── crawlers/
│       ├── base.py                 # 爬虫基类（频率控制/重试）
│       ├── douban.py               # 豆瓣租房小组
│       ├── beike.py                # 贝壳找房
│       ├── lianjia.py              # 链家
│       ├── manager.py              # 调度器（去重/落地）
│       └── scheduler.py            # 后台定时任务
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.js / App.vue       # 入口 + 根组件
│       ├── router/index.js         # 5 条路由
│       ├── api/client.js           # Axios 客户端
│       ├── assets/styles/main.css  # Design System
│       ├── stores/                 # Pinia: house, detail, favorites
│       ├── views/
│       │   ├── HomeView.vue        # 首页（热门社区 + 三步向导）
│       │   ├── SearchView.vue      # 搜索（列表/地图双视图 + 分页）
│       │   ├── DetailView.vue      # 详情（价格走势 + 通勤 + AI 分析）
│       │   ├── AssessView.vue      # 评估向导
│       │   └── FavoritesView.vue   # 收藏
│       └── components/
│           ├── map/                # Leaflet 地图
│           ├── search/             # 筛选面板 + 区域对比
│           ├── house/              # 房源卡片 + 图片画廊 + 历史走势图
│           ├── analysis/           # 日照/噪音/评论/房东卡片
│           ├── layout/             # 头部 + 底部
│           └── ui/                 # AI 助手 + 回到顶部 + 错误边界 + 空状态
│
└── images/                         # 房源图片
```

## 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| `DEEPSEEK_API_KEY` | 否 | DeepSeek API Key（不配置则 AI 降级为规则引擎） |
| `AMAP_API_KEY` | 否 | 高德地图 API Key（不配置则用直线距离估算通勤） |

## License

MIT
