"""
rental-shield Streamlit 前端界面
应届生租房防坑决策引擎 · 广州站

运行方式：streamlit run app.py
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from db import get_houses_by_filter, get_house_by_id, get_house_reviews, get_landlord_by_phone
from utils import simulate_sunlight_hours, simulate_noise_level, risk_label
from agents import ReviewMinerAgent, LandlordRiskAgent, FinalAdvisorAgent
import config

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="应届生租房防坑决策引擎 · 广州站",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 自定义 CSS 样式（卡片圆角阴影、风险标签颜色等）
# ============================================================
st.markdown("""
<style>
    /* 房源卡片样式 */
    .house-card {
        background: white;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        cursor: pointer;
        transition: all 0.2s ease;
        border: 1px solid #eee;
    }
    .house-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        transform: translateY(-2px);
        border-color: #4A90D9;
    }
    .house-title {
        font-size: 17px;
        font-weight: bold;
        color: #1a1a1a;
        margin-bottom: 6px;
    }
    .house-price {
        font-size: 22px;
        font-weight: bold;
        color: #e74c3c;
    }
    .house-price-unit {
        font-size: 13px;
        color: #999;
        font-weight: normal;
    }
    .house-meta {
        font-size: 13px;
        color: #666;
    }
    .risk-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 10px;
        font-size: 12px;
        font-weight: bold;
    }
    /* 详情页样式 */
    .detail-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 24px;
        border-radius: 14px;
        margin-bottom: 20px;
    }
    .detail-header h2 {
        color: white !important;
        margin: 0;
    }
    .metric-box {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        border: 1px solid #e9ecef;
    }
    .advice-card {
        padding: 20px 24px;
        border-radius: 14px;
        margin: 16px 0;
    }
    .advice-recommend {
        background: #d4edda;
        border: 2px solid #28a745;
    }
    .advice-consider {
        background: #fff3cd;
        border: 2px solid #ffc107;
    }
    .advice-not {
        background: #f8d7da;
        border: 2px solid #dc3545;
    }
    .tag-positive {
        background: #d4edda;
        color: #155724;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 12px;
        margin: 2px;
        display: inline-block;
    }
    .tag-negative {
        background: #f8d7da;
        color: #721c24;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 12px;
        margin: 2px;
        display: inline-block;
    }
    .section-title {
        font-size: 18px;
        font-weight: bold;
        margin: 20px 0 10px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #4A90D9;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 初始化 Session State（页面状态管理）
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "list"         # 当前页面：list（列表） 或 detail（详情）
if "selected_house_id" not in st.session_state:
    st.session_state.selected_house_id = None  # 当前选中的房源ID
if "search_triggered" not in st.session_state:
    st.session_state.search_triggered = False  # 是否已触发搜索


def go_to_detail(house_id):
    """跳转到房源详情页"""
    st.session_state.selected_house_id = house_id
    st.session_state.page = "detail"


def go_to_list():
    """返回列表页"""
    st.session_state.page = "list"
    st.session_state.selected_house_id = None


# ============================================================
# 初始化 AI Agent（延迟加载）
# ============================================================
@st.cache_resource
def get_agents():
    """缓存 AI Agent 实例，避免重复初始化"""
    return {
        "miner": ReviewMinerAgent(),
        "landlord_checker": LandlordRiskAgent(),
        "advisor": FinalAdvisorAgent(),
    }


# ============================================================
# 辅助：获取等级图标
# ============================================================
def light_icon(level):
    """日照等级 → 图标映射"""
    return {"优": "☀️☀️☀️", "良": "☀️☀️", "中": "☀️", "差": "🌥️"}.get(level, "☀️")


def noise_icon(level):
    """噪声等级 → 图标映射"""
    return {"优": "🔇", "良": "🔈", "中": "🔉", "差": "🔊"}.get(level, "🔇")


# ============================================================
# 侧边栏：搜索筛选区
# ============================================================
def render_sidebar():
    """渲染侧边栏搜索筛选区域"""
    with st.sidebar:
        st.title("🔍 搜索筛选")

        # 区域多选
        districts = st.multiselect(
            "区域",
            options=["天河", "海珠", "番禺", "越秀", "荔湾", "白云"],
            default=[],
            placeholder="不限区域",
        )

        # 户型单选
        layout = st.selectbox(
            "户型",
            options=["不限", "一室", "两室", "三室及以上"],
            index=0,
        )
        if layout == "不限":
            layout = None

        # 月租范围滑块
        price_range = st.slider(
            "月租范围（元）",
            min_value=0,
            max_value=8000,
            value=(0, 8000),
            step=100,
            format="¥%d",
        )

        # 排序方式
        sort_by = st.radio(
            "排序方式",
            options=["综合推荐", "价格从低到高", "价格从高到低", "光照最优", "隔音最优"],
            index=0,
        )

        st.divider()

        # 搜索按钮
        if st.button("🔎 搜索房源", type="primary", use_container_width=True):
            st.session_state.search_triggered = True

        return districts, layout, price_range, sort_by


# ============================================================
# 页面一：房源列表页
# ============================================================
def render_list_page(districts, layout, price_range, sort_by):
    """渲染房源搜索结果列表"""
    st.title("🏠 应届生租房防坑决策引擎 · 广州站")
    st.caption("综合评估光照、隔音、价格、房东风险，帮你做出明智的租房决策")

    # 如果没有触发搜索，显示欢迎页
    if not st.session_state.search_triggered:
        st.info("👈 请在左侧设置筛选条件后点击「搜索房源」开始查找")
        st.markdown("""
        ### 功能说明
        - **物理模拟**：基于朝向、楼层、窗型自动计算日均采光时长；基于建筑类型、临街距离等预测噪声等级
        - **AI 评论挖掘**：DeepSeek AI 自动分析租客评论，提取隔音、采光、房东、水电、交通、安全六维度关键词
        - **房东风险评估**：通过历史投诉和评论分析，自动判定房东风险等级
        - **综合决策建议**：汇总所有维度信息，给出「推荐/可考虑/不推荐」的最终建议
        """)
        return

    # --- 执行数据库查询 ---
    houses = get_houses_by_filter(
        districts=districts if districts else None,
        layout=layout,
        min_price=price_range[0],
        max_price=price_range[1],
    )

    # --- 对每条房源计算物理模拟结果，用于排序 ---
    house_scores = []
    for h in houses:
        light = simulate_sunlight_hours(h.orientation, h.floor, h.total_floors, h.window_type)
        noise = simulate_noise_level(h.building_type, h.building_year, h.floor, h.total_floors,
                                     h.distance_to_street, h.has_business_below)
        house_scores.append({
            "house": h,
            "light": light,
            "noise": noise,
        })

    # --- 排序 ---
    if sort_by == "价格从低到高":
        house_scores.sort(key=lambda x: x["house"].price)
    elif sort_by == "价格从高到低":
        house_scores.sort(key=lambda x: x["house"].price, reverse=True)
    elif sort_by == "光照最优":
        house_scores.sort(key=lambda x: x["light"]["hours"], reverse=True)
    elif sort_by == "隔音最优":
        house_scores.sort(key=lambda x: x["noise"]["db"])
    # 综合推荐：默认按 ID 排序

    # --- 显示结果数量 ---
    st.subheader(f"找到 {len(houses)} 套房源")

    if len(houses) == 0:
        st.warning("未找到符合条件的房源，请调整筛选条件后重试。")
        return

    # --- 渲染房源卡片列表 ---
    for item in house_scores:
        h = item["house"]
        light = item["light"]
        noise = item["noise"]

        # 计算综合风险评分（用于初始显示）
        risk_score = 100
        if light["level"] == "差":
            risk_score -= 25
        elif light["level"] == "中":
            risk_score -= 10
        if noise["level"] == "差":
            risk_score -= 25
        elif noise["level"] == "中":
            risk_score -= 10

        # 市场价比较
        market = config.MARKET_RENT.get(h.district, {}).get(h.layout, h.price)
        deviation = (h.price - market) / market if market > 0 else 0
        if deviation > 0.2:
            risk_score -= 15

        risk_label_text = risk_label(risk_score)

        # 使用 columns 布局卡片
        cols = st.columns([4, 1.5, 2, 1.8])
        with cols[0]:
            st.markdown(f"**{h.title}**")
            st.caption(f"📍 {h.district} · {h.community}")
        with cols[1]:
            st.markdown(f"<span class='house-price'>¥{h.price}</span><span class='house-price-unit'>/月</span>", unsafe_allow_html=True)
            st.caption(f"{h.layout} · {h.area}㎡")
        with cols[2]:
            st.markdown(f"<span title='日照等级'>{light_icon(light['level'])} {light['level']} 采光 · {light['hours']}h</span>", unsafe_allow_html=True)
            st.markdown(f"<span title='隔音等级'>{noise_icon(noise['level'])} {noise['level']} 隔音 · {noise['db']}dB</span>", unsafe_allow_html=True)
        with cols[3]:
            st.markdown(risk_label_text)
            if st.button("📋 查看详情", key=f"detail_{h.id}", use_container_width=True):
                go_to_detail(h.id)
                st.rerun()

        st.divider()


# ============================================================
# 页面二：房源详情页
# ============================================================
def render_detail_page():
    """渲染房源详情页面，包含所有分析维度"""
    house_id = st.session_state.selected_house_id
    if not house_id:
        go_to_list()
        st.rerun()
        return

    # 获取房源数据
    house = get_house_by_id(house_id)
    if not house:
        st.error("房源不存在")
        go_to_list()
        st.rerun()
        return

    # 计算物理模拟
    light = simulate_sunlight_hours(house.orientation, house.floor, house.total_floors, house.window_type, house.district)
    noise = simulate_noise_level(house.building_type, house.building_year, house.floor, house.total_floors,
                                 house.distance_to_street, house.has_business_below, house.district)

    # 返回按钮
    if st.button("← 返回列表", type="secondary"):
        go_to_list()
        st.rerun()

    # ====================================
    # 1. 房源头部信息
    # ====================================
    st.markdown(f"""
    <div class="detail-header">
        <h2>🏠 {house.title}</h2>
        <p style="margin:8px 0 0 0;opacity:0.9;">
            📍 {house.district}区 · {house.community} · {house.layout} · {house.area}㎡
        </p>
        <p style="font-size:28px;font-weight:bold;margin:12px 0 0 0;">
            ¥{house.price}<span style="font-size:16px;font-weight:normal;">/月</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ====================================
    # 2. 房源基本信息表格
    # ====================================
    st.markdown('<p class="section-title">📋 基本信息</p>', unsafe_allow_html=True)
    info_data = {
        "区域": house.district,
        "小区": house.community,
        "户型": house.layout,
        "面积": f"{house.area}㎡",
        "月租": f"¥{house.price}",
        "楼层": f"{house.floor}/{house.total_floors}层",
        "朝向": house.orientation,
        "窗户类型": house.window_type,
        "建筑类型": house.building_type,
        "建筑年代": house.building_year,
        "距主街": f"{house.distance_to_street}米",
        "底商": "有" if house.has_business_below else "无",
        "来源链接": house.source_url,
    }
    cols = st.columns(4)
    keys = list(info_data.keys())
    for i, key in enumerate(keys):
        with cols[i % 4]:
            st.metric(label=key, value=info_data[key])

    # ====================================
    # 3. 物理环境指标卡片
    # ====================================
    st.markdown('<p class="section-title">🌤️ 物理环境模拟</p>', unsafe_allow_html=True)
    env_col1, env_col2 = st.columns(2)

    # --- 3a. 光照分析 ---
    with env_col1:
        st.markdown(f"""
        <div class="metric-box">
            <h3>{light_icon(light['level'])} 采光评级：{light['level']}</h3>
            <p style="font-size:36px;font-weight:bold;color:#f39c12;margin:8px 0;">
                {light['hours']}<span style="font-size:18px;">小时/天</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("📐 采光计算详情", expanded=True):
            orientation_weight = config.ORIENTATION_WEIGHTS.get(house.orientation, 0.6)
            ratio = house.floor / max(house.total_floors, 1)
            if ratio <= 1/3:
                floor_desc = "低层（受周边遮挡）"
                floor_coef = 0.7
            elif ratio <= 2/3:
                floor_desc = "中层（部分遮挡）"
                floor_coef = 0.9
            else:
                floor_desc = "高层（视野开阔）"
                floor_coef = 1.1
            window_coef = config.WINDOW_COEFFICIENTS.get(house.window_type, 1.0)

            st.markdown(f"""
            **计算公式**：{config.BASE_SUNLIGHT_HOURS}h × {orientation_weight}（{house.orientation}向） × {floor_coef}（{floor_desc}） × {window_coef}（{house.window_type}） = **{light['hours']}h**

            - 广州年均基准日照：{config.BASE_SUNLIGHT_HOURS} 小时/天
            - 朝向贡献：{house.orientation}向，权重 {orientation_weight}
            - 楼层贡献：第 {house.floor}/{house.total_floors} 层，系数 {floor_coef}（{floor_desc}）
            - 窗户贡献：{house.window_type}，系数 {window_coef}
            """)

    # --- 3b. 噪声分析 ---
    with env_col2:
        st.markdown(f"""
        <div class="metric-box">
            <h3>{noise_icon(noise['level'])} 隔音评级：{noise['level']}</h3>
            <p style="font-size:36px;font-weight:bold;color:{'#27ae60' if noise['db'] < 50 else '#e67e22'};margin:8px 0;">
                {noise['db']}<span style="font-size:18px;">dB</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("🔊 噪声计算详情", expanded=True):
            base_noise = config.BUILDING_NOISE.get(house.building_type, 40)
            if house.building_year < 2000:
                year_desc = "2000年前建筑 → +8dB"
                year_corr = 8
            elif house.building_year <= 2010:
                year_desc = "2000-2010年建筑 → +4dB"
                year_corr = 4
            else:
                year_desc = "2010年后建筑 → +0dB"
                year_corr = 0

            if house.distance_to_street < 50:
                street_desc = f"临街 < 50m → +20dB"
                street_corr = 20
            elif house.distance_to_street <= 200:
                street_desc = f"临街 50-200m → +10dB"
                street_corr = 10
            else:
                street_desc = f"远离主街 > 200m → +0dB"
                street_corr = 0

            biz_corr = 15 if house.has_business_below else 0
            biz_desc = f"有底商 → +15dB" if house.has_business_below else "无底商 → +0dB"
            floor_att = (house.total_floors - house.floor) * 0.5

            st.markdown(f"""
            **计算公式**：{base_noise}dB + {year_corr}dB + {street_corr}dB + {biz_corr}dB - {floor_att:.1f}dB = **{noise['db']}dB**

            - 建筑基础：{house.building_type} → {base_noise}dB
            - 建筑年代：{year_desc}
            - 临街距离：{street_desc}
            - 底商影响：{biz_desc}
            - 楼层衰减：{(house.total_floors - house.floor)}层 × 0.5dB = -{floor_att:.1f}dB
            """)

    # ====================================
    # 4. 评论挖掘结果
    # ====================================
    st.markdown('<p class="section-title">💬 AI 评论挖掘</p>', unsafe_allow_html=True)

    # 获取评论原始数据
    reviews = get_house_reviews(house_id)

    with st.spinner("🤖 AI 正在分析评论内容..."):
        agents = get_agents()
        review_analysis = agents["miner"].mine(house_id)

    # --- 展示六维度关键词 ---
    dimension_labels = {
        "sound": "🔇 隔音",
        "lighting": "☀️ 采光",
        "landlord": "👤 房东",
        "utility": "⚡ 水电",
        "transport": "🚇 交通",
        "safety": "🛡️ 安全",
    }
    dim_cols = st.columns(3)
    for i, (key, label) in enumerate(dimension_labels.items()):
        with dim_cols[i % 3]:
            st.markdown(f"**{label}**")
            data = review_analysis.get(key, {"positive": [], "negative": []})
            # 正面关键词（绿色标签）
            pos_tags = " ".join([f'<span class="tag-positive">+ {k}</span>' for k in data.get("positive", [])])
            neg_tags = " ".join([f'<span class="tag-negative">- {k}</span>' for k in data.get("negative", [])])
            st.markdown(pos_tags if pos_tags else "*暂无正面评价*", unsafe_allow_html=True)
            st.markdown(neg_tags if neg_tags else "*暂无负面评价*", unsafe_allow_html=True)

    # --- 评论原文滚动展示 ---
    with st.expander(f"📝 查看全部 {len(reviews)} 条评论原文", expanded=False):
        if reviews:
            for rev in reviews:
                rating_stars = "⭐" * rev.rating
                st.markdown(f"""
                <div style="background:#f8f9fa;padding:10px 14px;border-radius:8px;margin:6px 0;">
                    <strong>[{rev.platform}]</strong> {rating_stars} · {rev.created_at.strftime('%Y-%m-%d') if rev.created_at else ''}
                    <p style="margin:6px 0 0 0;">{rev.content}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("暂无评论数据")

    # ====================================
    # 5. 房东风险画像
    # ====================================
    st.markdown('<p class="section-title">👤 房东风险画像</p>', unsafe_allow_html=True)

    landlord = get_landlord_by_phone(house.landlord_phone_hash)

    with st.spinner("🔍 AI 正在评估房东风险..."):
        landlord_risk = agents["landlord_checker"].assess(house.landlord_phone_hash)

    if landlord:
        risk_col1, risk_col2, risk_col3 = st.columns(3)
        with risk_col1:
            st.metric("房东类型", landlord.type)
        with risk_col2:
            st.metric("历史投诉", f"{landlord.complaint_count} 次")
        with risk_col3:
            risk_lvl = landlord_risk.get("risk_level", "未知")
            risk_color = {"高": "🔴", "中": "🟡", "低": "🟢"}.get(risk_lvl, "⚪")
            st.metric("风险等级", f"{risk_color} {risk_lvl}")

        # 风险标签
        if landlord.risk_tags:
            tags = landlord.risk_tags.split(",")
            st.markdown("**风险标签**：" + " ".join([f'<span class="tag-negative">{t.strip()}</span>' for t in tags]), unsafe_allow_html=True)

        # 详细风险点
        risk_items = landlord_risk.get("risk_items", [])
        if risk_items:
            st.markdown("**详细风险点**：")
            for item in risk_items:
                if isinstance(item, dict):
                    st.warning(f"**{item.get('type', '风险')}**：{item.get('description', '')}")
                else:
                    st.warning(str(item))

        # 综合描述
        st.info(f"**综合评估**：{landlord_risk.get('summary', '暂无评估')}")
    else:
        st.info("暂无该房东信息")

    # ====================================
    # 6. 价格分析
    # ====================================
    market_price = config.MARKET_RENT.get(house.district, {}).get(house.layout, house.price)
    if market_price > 0:
        deviation = (house.price - market_price) / market_price
        is_reasonable = abs(deviation) <= 0.2
    else:
        deviation = 0
        is_reasonable = True
    price_analysis = {
        "market_price": market_price,
        "deviation": deviation,
        "is_reasonable": is_reasonable,
    }

    # ====================================
    # 7. 最终综合建议
    # ====================================
    st.markdown('<p class="section-title">🎯 最终决策建议</p>', unsafe_allow_html=True)

    with st.spinner("🤖 AI 正在综合分析并生成建议..."):
        advice = agents["advisor"].advise(light, noise, price_analysis, review_analysis, landlord_risk)

    decision = advice.get("decision", "可考虑")
    risk_level = advice.get("risk_level", "黄")
    summary = advice.get("summary", "")
    highlights = advice.get("highlights", [])
    warnings = advice.get("warnings", [])

    # 根据决策选择样式
    if decision == "推荐":
        card_class = "advice-recommend"
        emoji = "✅"
    elif decision == "不推荐":
        card_class = "advice-not"
        emoji = "❌"
    else:
        card_class = "advice-consider"
        emoji = "⚠️"

    st.markdown(f"""
    <div class="advice-card {card_class}">
        <h2>{emoji} 决策：{decision}</h2>
        <p style="font-size:16px;margin:12px 0;">{summary}</p>
    </div>
    """, unsafe_allow_html=True)

    # 优点和缺点
    h_col, w_col = st.columns(2)
    with h_col:
        st.markdown("#### ✅ 优点")
        if highlights:
            for hh in highlights:
                st.markdown(f"- {hh}")
        else:
            st.caption("暂无")

    with w_col:
        st.markdown("#### ⚠️ 注意事项")
        if warnings:
            for ww in warnings:
                st.markdown(f"- {ww}")
        else:
            st.caption("暂无明显缺点")


# ============================================================
# 主入口
# ============================================================
def main():
    """主函数：根据 session state 决定渲染哪个页面"""
    districts, layout, price_range, sort_by = render_sidebar()

    if st.session_state.page == "detail":
        render_detail_page()
    else:
        render_list_page(districts, layout, price_range, sort_by)


if __name__ == "__main__":
    main()
