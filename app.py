import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# =====================================================
# 1. CẤU HÌNH TRANG
# =====================================================
st.set_page_config(
    page_title="Hệ thống Insight Persona & Basket Analytics 2.0",
    page_icon="🏆",
    layout="wide"
)

st.markdown("""
<style>
.main { background-color: #f9fbff; }
.stMetric {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    border: 1px solid #e1e8f0;
}
.stTabs [data-baseweb="tab-list"] { gap: 30px; }
.stTabs [data-baseweb="tab"] {
    height: 60px;
    font-weight: bold;
    font-size: 16px;
}
.highlight-card {
    padding: 1.5rem;
    border-radius: 10px;
    border-left: 5px solid #007bff;
    background-color: #ffffff;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# 2. LOAD DỮ LIỆU
# =====================================================
@st.cache_data
def load_all_data():
    base_path = "/hdd3/namdh/datamining/shop_cluster_"

    df_cust = pd.read_csv(
        f"{base_path}/data/processed/customer_clusters_from_rules.csv"
    )

    df_rule_feat = pd.read_csv(
        f"{base_path}/data/processed/customer_rule_features.csv"
    )

    rules_path = f"{base_path}/data/processed/rules_with_basket_groups.csv"
    if os.path.exists(rules_path):
        df_rules = pd.read_csv(rules_path)
        has_bg = True
    else:
        df_rules = pd.read_csv(
            f"{base_path}/data/processed/rules_apriori_filtered.csv"
        )
        has_bg = False

    return df_cust, df_rules, df_rule_feat, has_bg


df, rules, rule_feat, has_bg = load_all_data()

# =====================================================
# 3. PERSONA CONFIG
# =====================================================
persona_config = {
    0: {
        "vn": "Khách Phổ thông / Nguy cơ rời bỏ",
        "icon": "📉",
        "color": "#636EFA",
        "insight": (
            "Nhóm khách hàng chiếm số lượng lớn nhưng tần suất mua thấp và "
            "đã lâu không quay lại. Giá trị dài hạn còn hạn chế."
        ),
        "strategy": (
            "Triển khai chiến dịch re-activation: voucher quay lại, freeship, "
            "bundle giá rẻ dựa trên các luật mua kèm phổ biến."
        )
    },
    1: {
        "vn": "Khách Quen Giá Trị Cao",
        "icon": "⭐",
        "color": "#00CC96",
        "insight": (
            "Nhóm khách hàng có hành vi mua lặp lại rõ ràng, thường xuyên kích hoạt "
            "các luật mua kèm có lift cao."
        ),
        "strategy": (
            "Áp dụng cross-sell và upsell cá nhân hóa dựa trên top rule-features. "
            "Triển khai chương trình loyalty/VIP."
        )
    },
    2: {
        "vn": "Siêu VIP / Nhiễu dữ liệu",
        "icon": "🏆",
        "color": "#EF553B",
        "insight": (
            "Cụm chỉ gồm một thực thể có giá trị RFM cực lớn, "
            "được xác định là artifact do CustomerID bị thiếu."
        ),
        "strategy": (
            "Loại khỏi phân tích marketing. Giữ lại để minh họa "
            "tầm quan trọng của xử lý dữ liệu."
        )
    }
}

# =====================================================
# 4. SIDEBAR
# =====================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3126/3126647.png", width=80)
    st.title("Elite CRM Analytics")

    algo_choice = st.radio("Chọn mô hình:", ["K-Means", "Agglomerative"])
    target_col = "cluster" if algo_choice == "K-Means" else "cluster_agg"

    st.divider()

    cluster_id = st.selectbox(
        "Chọn cụm:",
        sorted(df[target_col].unique()),
        format_func=lambda x: f"Cụm {x}: {persona_config.get(x, {}).get('vn')}"
    )

c_data = df[df[target_col] == cluster_id]
p_data = persona_config.get(cluster_id)

# =====================================================
# 5. HEADER
# =====================================================
st.title(f"{p_data['icon']} Persona: {p_data['vn']}")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Số KH", f"{len(c_data):,}")
m2.metric("Monetary TB", f"£{c_data['Monetary'].mean():,.0f}")
m3.metric("Frequency TB", f"{c_data['Frequency'].mean():.1f}")
m4.metric("Recency TB", f"{c_data['Recency'].mean():.1f} ngày")

st.divider()

# =====================================================
# 6. TABS
# =====================================================
tab_persona, tab_basket, tab_benchmark = st.tabs([
    "👤 PROFILING & RULE INSIGHT",
    "📦 HỆ SINH THÁI GIỎ HÀNG",
    "🔬 BENCHMARK"
])

# -----------------------------------------------------
# TAB 1: PROFILING + TOP RULE-FEATURES
# -----------------------------------------------------
with tab_persona:
    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.scatter(
            df,
            x="Component 1",
            y="Component 2",
            color=target_col,
            color_discrete_map={0: "#636EFA", 1: "#00CC96", 2: "#EF553B"},
            template="plotly_white",
            height=500
        )
        fig.add_trace(go.Scatter(
            x=c_data["Component 1"],
            y=c_data["Component 2"],
            mode="markers",
            marker=dict(size=10, color="yellow", line=dict(width=1, color="black")),
            name="Cụm đang chọn"
        ))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🧠 Insight")
        st.info(p_data["insight"])
        st.success(f"**Chiến lược:** {p_data['strategy']}")

    st.markdown("### 🔗 Top Rule-features kích hoạt nhiều nhất trong cụm")

    rf_cluster = rule_feat[
        rule_feat["CustomerID"].isin(c_data["CustomerID"])
    ]

    rule_cols = [c for c in rf_cluster.columns if c != "CustomerID"]

    top_rules = (
        rf_cluster[rule_cols]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
        .rename(columns={"index": "Rule_Feature", 0: "Activation_Rate"})
    )

    st.dataframe(
        top_rules.style.format({"Activation_Rate": "{:.3f}"}),
        use_container_width=True
    )

# -----------------------------------------------------
# TAB 2: BASKET
# -----------------------------------------------------
with tab_basket:
    st.subheader("🧺 Basket Rules theo nhóm sản phẩm")
    if has_bg:
        bg_id = st.selectbox(
            "Chọn Basket Group",
            sorted(rules["basket_group"].unique())
        )

        bg_rules = rules[rules["basket_group"] == bg_id] \
            .sort_values("lift", ascending=False)

        st.dataframe(
            bg_rules[
                ["antecedents_str", "consequents_str", "support", "confidence", "lift"]
            ].head(10),
            use_container_width=True
        )
    else:
        st.warning("Chưa có rules_with_basket_groups.csv")

# -----------------------------------------------------
# TAB 3: BENCHMARK
# -----------------------------------------------------
with tab_benchmark:
    st.subheader("🔬 Đánh giá mô hình")

    metric_df = pd.DataFrame({
        "Metric": ["Silhouette ↑", "Davies-Bouldin ↓"],
        "K-Means": ["0.873", "0.287"],
        "Agglomerative": ["0.871", "0.316"]
    })

    st.table(metric_df)

    st.success(
        "K-Means được chọn do silhouette cao hơn và cụm dễ diễn giải "
        "phục vụ hành động marketing."
    )

# =====================================================
# 7. EXPORT
# =====================================================
with st.expander("📥 Xuất danh sách khách hàng trong cụm"):
    st.dataframe(
        c_data[
            ["CustomerID", "Recency", "Frequency", "Monetary"]
        ].sort_values("Monetary", ascending=False),
        use_container_width=True
    )
