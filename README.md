# 安租 · 应届生租房防坑决策引擎 · 广州站

基于 AI 评论挖掘 + 物理环境模拟的智能租房口碑分析平台，聚合网络评价，帮助应届生避开黑中介和问题房源。

> 参照 [rightHouse](https://github.com/liguobao/HouseSearch) 和 唯心所寓(Wellcee) 的设计理念，专注「信息采集 + 口碑分析」而非简单房源列表。

## 核心能力

| 模块 | 说明 |
|------|------|
| **AI 评论挖掘** | DeepSeek AI 分析租客评论，提取隔音/采光/房东/水电/交通/安全 6 维度关键词 |
| **房东风险评估** | 基于历史投诉数据自动判定房东风险等级（押金不退、随意涨租、二房东转租等 5 类） |
| **环境物理模拟** | 朝向×楼层×窗型计算采光时长；建筑类型×年代×临街距离预测噪声分贝 |
| **价格合理性** | 对比同区域同户型市场均价，±20% 合理区间判定，历史价格走势展示 |
| **地铁线路筛选** | 广州 9 条地铁线全站点坐标，选线即可查看沿线房源 |
| **通勤计算** | 高德公共交通 API，计算房源到公司的公交/地铁通勤时间 |
| **综合决策** | 多维度加权评分，输出「推荐/可考虑/不推荐」+ 优点 + 风险提示 |

## 技术架构

```
┌──────────────────────────────────────────────────────────┐
│                    Vue 3 SPA 前端                         │
│  Pinia Store · Vue Router · Leaflet 地图 · Axios         │
│  HomeView / SearchView / DetailView / FavoritesView      │
├──────────────────────────────────────────────────────────┤
│                    FastAPI 后端                           │
│  /houses /analysis /agents /districts /commute /subway   │
│  /favorites /images                                      │
├──────────────────────────────────────────────────────────┤
│                    业务服务层                             │
│  日照模拟 · 噪声模拟 · AI Agent(3个) · 地理编码           │
│  通勤计算 · 地铁服务 · 收藏服务 · 区域统计                 │
├──────────────────────────────────────────────────────────┤
│                    数据持久层                             │
│  SQLAlchemy ORM · SQLite                                 │
│  houses / reviews / landlords / price_history / images   │
│  districts / favorites / workspace_configs               │
├──────────────────────────────────────────────────────────┤
│                    外部服务                               │
│  DeepSeek API ↔ 高德地图 API (地理编码+公交通勤)          │
└──────────────────────────────────────────────────────────┘
```

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/2362461686/rental-shield.git
cd rental-shield
```

### 2. 安装后端依赖

```bash
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

### 3. 安装前端依赖

```bash
cd frontend
npm install
cd ..
```

### 4. 初始化数据

```bash
python seed_data.py
```

### 5. 配置 API Key（可选）

```bash
# DeepSeek AI（不配置则使用规则引擎降级）
export DEEPSEEK_API_KEY="your-key"

# 高德地图（地理编码 + 通勤计算，不配置则使用直线距离估算）
export AMAP_API_KEY="your-key"
```

### 6. 启动

```bash
# 终端 1 — 后端
uvicorn backend.main:app --reload --port 8000

# 终端 2 — 前端
cd frontend && npm run dev
```

浏览器访问 **http://localhost:5173**

> 也支持 Streamlit 旧版：`streamlit run app.py` → http://localhost:8501

## 项目结构

```
rental-shield/
├── app.py                          # Streamlit 旧版前端（保留）
├── config.py / db.py               # 根级配置 & 数据库模型
├── utils.py / agents.py            # 物理模拟 & AI Agent
├── seed_data.py                    # 种子数据：50套广州房源
├── fetch_images.py                 # 链家/贝壳房源图片抓取
├── requirements.txt
├── rental.db                       # SQLite 数据库
│
├── backend/                        # FastAPI 后端
│   ├── main.py                     # 应用入口
│   ├── config.py                   # 后端配置
│   ├── agents.py / utils.py        # Agent & 工具
│   ├── deps.py                     # 依赖注入
│   ├── db/
│   │   ├── database.py             # 引擎 + 会话 + 迁移
│   │   ├── models.py               # ORM 模型(8 张表)
│   │   ├── queries.py              # 查询函数
│   │   └── migrations.py           # SQLite ALTER TABLE 迁移
│   ├── models/
│   │   └── house.py                # Pydantic schemas
│   ├── routers/
│   │   ├── houses.py               # 房源 CRUD + 关键词搜索
│   │   ├── analysis.py             # 物理模拟端点
│   │   ├── agent_routes.py         # AI Agent 端点
│   │   ├── districts.py            # 区域统计 + 地理编码
│   │   ├── commute.py              # 通勤计算 + 工作地配置
│   │   ├── subway.py               # 地铁站点/线路查询
│   │   ├── favorites.py            # 收藏 toggle/check/list
│   │   └── images.py               # 图片服务
│   └── services/
│       ├── house_service.py        # 房源业务逻辑
│       ├── district_service.py     # 区域统计
│       ├── commute_service.py      # 通勤计算
│       ├── subway_service.py       # 广州 9 线地铁数据
│       ├── geocode_service.py      # 高德地理编码
│       └── favorite_service.py     # 收藏业务
│
├── frontend/                       # Vue 3 SPA 前端
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.js                 # Vue 入口
│       ├── App.vue                 # 根组件
│       ├── router/index.js         # 路由：首页/搜索/详情/收藏
│       ├── api/client.js           # Axios 客户端
│       ├── assets/styles/main.css  # 全局样式：暖橙色INS风主题
│       ├── stores/
│       │   ├── house.js            # 搜索状态 + 通勤缓存
│       │   ├── detail.js           # 详情两阶段加载
│       │   └── favorites.js        # 收藏状态
│       ├── views/
│       │   ├── HomeView.vue        # 首页：核心能力卡片 + 地铁
│       │   ├── SearchView.vue      # 搜索：列表/地图双视图
│       │   ├── DetailView.vue      # 详情：AI分析 + 位置地图
│       │   └── FavoritesView.vue   # 收藏列表
│       └── components/
│           ├── map/
│           │   └── HouseMap.vue    # Leaflet 地图(3种模式)
│           ├── search/
│           │   ├── SearchPanel.vue # 筛选面板(区域/户型/价格/地铁)
│           │   ├── WorkspaceModal.vue  # 通勤设置弹窗
│           │   └── DistrictOverview.vue
│           ├── house/
│           │   └── HouseCard.vue   # 房源卡片(风险标签+指示灯)
│           └── layout/
│               └── AppHeader.vue
│
└── images/                         # 房源图片(50个子目录)
```

## 数据库表

| 表名 | 用途 |
|------|------|
| `houses` | 房源主表（含经纬度、通勤分） |
| `reviews` | 租客评论 |
| `price_history` | 历史价格 |
| `landlords` | 房东信息 |
| `listing_images` | 房源图片 |
| `districts` | 区域中心坐标 |
| `favorites` | 用户收藏 |
| `workspace_configs` | 通勤工作地配置 |

## 设计语言

- **主色调**：暖橙色 `#F59E0B`，INS 风低饱和度暖灰背景 `#F5F0EB`
- **卡片系统**：大软阴影 (`0 6px 30px rgba(0,0,0,0.06)`) + `14px` 圆角
- **指标体系**：绿/黄/橙/红 四色编码（采光、隔音、风险、价格）
- **技术栈**：`Vue 3` `FastAPI` `SQLAlchemy` `SQLite` `DeepSeek API` `高德地图 API` `Leaflet`
