# 🏠 Rental-Shield 应届生租房防坑决策引擎 · 广州站

基于物理模拟算法与 DeepSeek AI 的智能租房决策辅助工具，帮助应届生全面评估房源，避免踩坑。

## 核心功能

- **物理环境模拟**：基于朝向、楼层、窗型计算日均采光时长；基于建筑类型、年代、临街距离预测噪声等级
- **AI 评论挖掘**：DeepSeek AI 自动分析租客评论，提取隔音、采光、房东、水电、交通、安全六维度正负面关键词
- **房东风险评估**：通过历史投诉和评论分析，自动判定房东风险等级（押金不退、随意涨租、二房东转租等）
- **综合决策建议**：汇总所有维度信息，给出「推荐/可考虑/不推荐」的最终建议

## 技术架构

```
┌─────────────────────────────────────────────────┐
│                   Streamlit 前端                  │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ 搜索筛选 │  │ 房源卡片 │  │   详情分析页   │  │
│  └──────────┘  └──────────┘  └───────────────┘  │
├─────────────────────────────────────────────────┤
│                   业务逻辑层                      │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ utils.py │  │agents.py │  │    config.py   │  │
│  │ 物理模拟 │  │ AI Agent │  │    全局配置    │  │
│  └──────────┘  └──────────┘  └───────────────┘  │
├─────────────────────────────────────────────────┤
│                   数据持久层                      │
│  ┌──────────┐  ┌──────────────────────────────┐  │
│  │  db.py   │  │       SQLite (rental.db)      │  │
│  │ SQLAlch  │  │  houses/reviews/landlords... │  │
│  └──────────┘  └──────────────────────────────┘  │
├─────────────────────────────────────────────────┤
│                   外部服务                        │
│  ┌─────────────────────────────────────────────┐ │
│  │        DeepSeek API (OpenAI 兼容模式)       │ │
│  │  ReviewMiner / LandlordRisk / FinalAdvisor  │ │
│  └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/2362461686/rental-shield.git
cd rental-shield
```

### 2. 创建虚拟环境并安装依赖

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 配置 DeepSeek API Key

```bash
# Linux / macOS
export DEEPSEEK_API_KEY="your-deepseek-api-key"

# Windows PowerShell
$env:DEEPSEEK_API_KEY="your-deepseek-api-key"

# Windows CMD
set DEEPSEEK_API_KEY=your-deepseek-api-key
```

> 如果不配置 API Key，项目仍可正常运行（使用规则引擎降级方案），但 AI 评论分析和房东风险评估功能将被禁用。

### 4. 初始化数据库并导入种子数据

```bash
python seed_data.py
```

### 5. 启动应用

```bash
streamlit run app.py
```

浏览器将自动打开 `http://localhost:8501`。

## 项目结构

```
rental-shield/
├── app.py              # Streamlit 前端主界面
├── config.py           # 全局配置（API、市场租金、物理参数）
├── db.py               # 数据库模型定义（SQLAlchemy + SQLite）
├── utils.py            # 物理模拟算法（日照计算、噪声计算、风险标签）
├── agents.py           # AI Agent（评论挖掘、房东风险、最终决策）
├── seed_data.py        # 种子数据生成（50套广州房源 + 评论 + 房东）
├── requirements.txt    # Python 依赖
├── README.md           # 项目说明
└── .gitignore          # Git 忽略规则
```

## 技术栈

`Python` `Streamlit` `SQLAlchemy` `SQLite` `DeepSeek API` `OpenAI SDK`

## 截图

> 运行 `streamlit run app.py` 后，你将看到：
> - 左侧边栏：区域、户型、租金范围等筛选条件
> - 主区域：房源卡片列表，包含光照/隔音评级和风险标签
> - 详情页：物理环境模拟、AI 评论挖掘、房东风险画像、综合决策建议
