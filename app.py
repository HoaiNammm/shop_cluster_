import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Hệ thống Insight Persona & Basket Analytics 2.0",
    page_icon="🏆",
    layout="wide"
)

# Custom CSS để giao diện chuyên nghiệp hơn
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
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. HÀM LOAD DỮ LIỆU ---
@st.cache_data
def load_all_data():
    df_cust = pd.read_csv("/hdd3/namdh/datamining/shop_cluster_/data/processed/customer_clusters_from_rules.csv")
    if os.path.exists("/hdd3/namdh/datamining/shop_cluster_/data/processed/rules_with_basket_groups.csv"):
        df_rules = pd.read_csv("/hdd3/namdh/datamining/shop_cluster_/data/processed/rules_with_basket_groups.csv")
        has_bg = True
    else:
        df_rules = pd.read_csv("rules_apriori_filtered.csv")
        has_bg = False
    return df_cust, df_rules, has_bg

df, rules, has_bg = load_all_data()

# --- 2. LOGIC PERSONA & INSIGHT CHI TIẾT ---
persona_config = {
    0: {
        "vn": "Khách Phổ thông / Rủi ro", 
        "icon": "📉", "color": "#636EFA", 
        "insight": "Chi phí để có được (CAC) nhóm này rất lớn nhưng giá trị thu hồi lại thấp. Tỷ lệ rời bỏ (Churn) đang ở mức báo động.",
        "strategy": "Sử dụng Automation Marketing. Tặng mã Voucher giảm giá sâu hoặc Freeship cho đơn hàng tiếp theo để \"đánh thức\" họ quay lại, mục tiêu là đưa Recency về mức dưới 30 ngày."
    },
    1: {
        "vn": "Khách Quen Giá Trị Cao", 
        "icon": "⭐", "color": "#00CC96", 
        "insight": "Đây là nhóm có lòng trung thành cao nhưng đang bị \"nguội lạnh\". Họ cần một lý do để quay lại thường xuyên hơn.",
        "strategy": "Tận dụng kết quả từ Basket Clustering để cá nhân hóa gợi ý. Nếu họ đã mua món A, hãy gửi thông báo về món B thuộc cùng nhóm ngành hàng ngay tại thời điểm ngày thứ 30 (trước khi họ chạm ngưỡng 61 ngày)."
    },
    2: {
        "vn": "Siêu VIP / Đối tác chiến lược", 
        "icon": "🏆", "color": "#EF553B", 
        "insight": "Sự ổn định của toàn bộ doanh nghiệp phụ thuộc vào sự hài lòng của nhóm này. Một biến động nhỏ trong hành vi của \"Whale\" sẽ gây sụt giảm doanh thu nghiêm trọng hơn hàng ngàn khách hàng nhỏ lẻ cộng lại.",
        "strategy": "Áp dụng cơ chế Key Account Management (KAM). Cần sự can thiệp trực tiếp từ cấp quản lý để duy trì mối quan hệ 1-1, ưu tiên tồn kho và cung cấp các giải pháp logistics riêng biệt thay vì các chương trình khuyến mãi đại trà."
    }
}

# --- 3. SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3126/3126647.png", width=80)
    st.title("Elite CRM Analytics")
    
    st.header("🔬 So sánh Mô hình")
    algo_choice = st.radio("Chọn Mô hình:", ["K-Means", "Agglomerative"])
    target_col = 'cluster' if algo_choice == "K-Means" else 'cluster_agg'
    
    st.divider()
    
    st.header("👤 Phân khúc Khách hàng")
    cluster_id = st.selectbox("Chọn Persona:", options=sorted(df[target_col].unique()),
                              format_func=lambda x: f"Cụm {x}: {persona_config.get(x, {}).get('vn', 'N/A')}")
    
c_data = df[df[target_col] == cluster_id]
p_data = persona_config.get(cluster_id, persona_config[0])

# --- 4. GIAO DIỆN CHÍNH ---
st.title(f"{p_data['icon']} Persona: {p_data['vn']} ({algo_choice})")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Số lượng Khách", f"{len(c_data):,}")
m2.metric("Doanh thu TB", f"£{c_data['Monetary'].mean():,.0f}")
m3.metric("Tần suất TB", f"{c_data['Frequency'].mean():.1f} lần")
m4.metric("Recency TB", f"{c_data['Recency'].mean():.1f} ngày")

st.divider()

# --- 5. CÁC TABS PHÂN TÍCH ---
tab_persona, tab_basket, tab_benchmark = st.tabs([
    "👤 PHÂN TÍCH PERSONA", 
    "📦 HỆ SINH THÁI GIỎ HÀNG", 
    "🔬 BENCHMARK CHIẾN LƯỢC"
])

# --- TAB 1: PHÂN TÍCH PERSONA ---
with tab_persona:
    st.subheader("🎯 Đặc điểm Hành vi & Định hướng Chăm sóc")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_pca = px.scatter(df, x='Component 1', y='Component 2', color=target_col,
                             color_discrete_map={0: "#636EFA", 1: "#00CC96", 2: "#EF553B"},
                             title="Bản đồ Phân cụm (PCA Space)", template="plotly_white", height=500)
        fig_pca.add_trace(go.Scatter(x=c_data['Component 1'], y=c_data['Component 2'], 
                                     mode='markers', marker=dict(color='yellow', size=10, line=dict(width=1, color='Black')),
                                     name="Vị trí cụm hiện tại"))
        st.plotly_chart(fig_pca, use_container_width=True)
    
    with col2:
        st.markdown(f"#### 🧬 Insight cho Cụm {cluster_id}")
        st.info(p_data['insight'])
        st.success(f"**Chiến lược:**\n{p_data['strategy']}")
        
        st.markdown("---")
        # Radar Chart
        categories = ['Recency', 'Frequency', 'Monetary']
        all_max = df[categories].max()
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=(df[categories].mean()/all_max), theta=categories, fill='toself', name='TB Chung'))
        fig_radar.add_trace(go.Scatterpolar(r=(c_data[categories].mean()/all_max), theta=categories, fill='toself', name='Persona này', line_color=p_data['color']))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=True, height=350)
        st.plotly_chart(fig_radar, use_container_width=True)

# --- TAB 2: GIỎ HÀNG ---
with tab_basket:
    st.subheader("🧺 Phân tích sâu 5 Nhóm Hệ sinh thái Sản phẩm")
    if has_bg:
        bg_id = st.selectbox("Chọn Nhóm Giỏ hàng để phân tích sâu:", options=sorted(rules['basket_group'].unique()), 
                             format_func=lambda x: f"Nhóm {x}")
        
        curr_rules = rules[rules['basket_group'] == bg_id].sort_values('lift', ascending=False)
        
        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.write(f"**Top Quy luật trong Nhóm {bg_id}:**")
            st.dataframe(curr_rules[['antecedents_str', 'consequents_str', 'lift', 'confidence']].head(10), use_container_width=True)
        
        with c2:
            st.markdown("### 🔍 Phân tích Chiến thuật")
            if bg_id in [0, 1]:
                st.success("**NHÓM THẢO MỘC (HERB GARDEN)**")
                st.write("- **Sản phẩm chính:** Rosemary, Thyme, Parsley, Basil, Chives.")
                st.write("- **Insight:** Lift cực cao (~74). Khách hàng mua theo bộ sưu tập (Set).")
                st.write("- **Hành động:** Bán Combo bộ 6 nhãn hoặc quà tặng kèm khi mua hạt giống thảo mộc.")
            elif bg_id == 2:
                st.warning("**NHÓM DECOR SCANDINAVIAN**")
                st.write("- **Sản phẩm chính:** Wooden Heart, Star, Tree Christmas.")
                st.write("- **Insight:** Mua theo Concept thẩm mỹ đồng bộ. Lift đạt ~35.")
                st.write("- **Hành động:** Trưng bày theo chủ đề 'Giáng sinh gỗ' trên Website.")
            elif bg_id == 3:
                st.info("**NHÓM PHỤ KIỆN & HÀNG GỬI (ONLINE ACCS)**")
                st.write("- **Sản phẩm chính:** Shoulder Bags (Suki, Skull), Jam Making Set, Postage.")
                st.write("- **Insight:** Nhóm khách hàng sở thích cá nhân, thường mua Online.")
                st.write("- **Hành động:** Gợi ý túi xách đi kèm khi khách mua các bộ dụng cụ thủ công.")
            elif bg_id == 4:
                st.error("**NHÓM LƯU TRỮ & LOGISTICS**")
                st.write("- **Sản phẩm chính:** Jumbo Bags, Storage Bags, Dotcom Postage.")
                st.write("- **Insight:** Khách mua sắm số lượng lớn, cần túi chứa và dịch vụ vận chuyển.")
                st.write("- **Hành động:** Miễn phí túi Jumbo cho đơn hàng trên £100.")
    else:
        st.warning("Vui lòng chạy lại Notebook để tạo file rules_with_basket_groups.csv")

# --- TAB 3: BENCHMARK ---
with tab_benchmark:
    st.subheader("🔬 Đánh giá Đối chứng & Hiệu quả (Mục 2.3)")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### 1. So sánh Thuật toán (Quantitative)")
        metric_df = pd.DataFrame({
            "Metric": ["Silhouette (Cao là tốt)", "DB Index (Thấp là tốt)", "Mức độ phân tách"],
            "K-Means": ["0.873 (Win)", "0.287 (Win)", "Rất rõ ràng"],
            "Agglomerative": ["0.870", "0.316", "Dễ bị nhiễu"]
        })
        st.table(metric_df)
        
    with col_b:
        st.markdown("#### 2. So sánh Góc nhìn (Qualitative)")
        view_df = pd.DataFrame({
            "Tiêu chí": ["Góc nhìn Khách hàng", "Góc nhìn Giỏ hàng"],
            "Trọng tâm": ["Con người (Who)", "Sản phẩm (What)"],
            "Mục tiêu": ["Retention (Giữ chân)", "Cross-sell (Bán thêm)"],
            "Giá trị": ["Quyết định ai là VIP", "Quyết định Combo nào tốt"]
        })
        st.table(view_df)

    st.success("**KẾT LUẬN:** Góc nhìn Khách hàng giúp quản trị CRM (Who), còn góc nhìn Giỏ hàng giúp tối ưu hóa Sales (What). Kết hợp cả hai là chìa khóa cho chiến lược Marketing 10 điểm.")

# --- 6. XUẤT DỮ LIỆU ---
with st.expander("📥 Xuất danh sách Khách hàng mục tiêu"):
    st.dataframe(c_data[['CustomerID', 'Recency', 'Frequency', 'Monetary']].sort_values('Monetary', ascending=False))