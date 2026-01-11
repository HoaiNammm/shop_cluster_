import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Customer Persona Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- 1. HÀM LOAD DỮ LIỆU ---
@st.cache_data
def load_data():
    # Kiểm tra file tồn tại trước khi load
    cluster_path = "data/processed/customer_clusters_from_rules.csv"
    rules_path = "data/processed/rules_apriori_filtered.csv"
    
    if not os.path.exists(cluster_path):
        st.error(f"Không tìm thấy file: {cluster_path}. Hãy chạy Notebook để lưu file trước!")
        return None, None
        
    df = pd.read_csv(cluster_path)
    rules = pd.read_csv(rules_path) if os.path.exists(rules_path) else pd.DataFrame()
    return df, rules

df, rules = load_data()

# Dừng app nếu không có dữ liệu
if df is None:
    st.stop()

# --- 2. ĐỊNH NGHĨA PERSONA ---
# (Phù hợp với kết quả Biến thể 2 của bạn)
persona_info = {
    0: {
        "name": "Standard/At-Risk Customers (Phổ thông/Rủi ro)",
        "emoji": "🏠",
        "color": "#636EFA",
        "desc": "Nhóm khách hàng có chi tiêu thấp hoặc đã lâu chưa quay lại mua sắm.",
        "action": "Gửi mã giảm giá 'Nhớ bạn' (Retention) hoặc gợi ý các sản phẩm giá rẻ để kích cầu."
    },
    1: {
        "name": "High-Value Regulars (Khách quen giá trị cao)",
        "emoji": "🌟",
        "color": "#00CC96",
        "desc": "Khách hàng mua sắm ổn định, giá trị đơn hàng cao hơn mức trung bình.",
        "action": "Tặng điểm thưởng X2 cho các đơn hàng tiếp theo, đề xuất combo (Bundle) sản phẩm."
    },
    2: {
        "name": "Super VIP Champions (Cá voi ưu tú)",
        "emoji": "💎",
        "color": "#EF553B",
        "desc": "Nhóm khách hàng cực kỳ quan trọng, chi tiêu khổng lồ và tần suất mua sắm hàng ngày.",
        "action": "Chăm sóc đặc quyền 1-1, tặng quà tri ân riêng biệt và mời tham gia sự kiện VIP."
    }
}

# --- SIDEBAR ---
st.sidebar.header("⚙️ Cấu hình Dashboard")
cluster_id = st.sidebar.selectbox(
    "Chọn Nhóm Persona:", 
    options=sorted(df['cluster'].unique()),
    format_func=lambda x: f"Cụm {x}: {persona_info[x]['name']}" if x in persona_info else f"Cụm {x}"
)

# Lấy dữ liệu của cụm đang chọn
c_data = df[df['cluster'] == cluster_id]
current_persona = persona_info.get(cluster_id, persona_info[0])

# --- GIAO DIỆN CHÍNH ---
st.title(f"{current_persona['emoji']} Phân tích Persona: {current_persona['name']}")
st.markdown(f"**Mô tả chân dung:** {current_persona['desc']}")

# Hiển thị các Metric chính
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    st.metric("Tổng số khách", f"{len(c_data):,}")
with m_col2:
    st.metric("Recency TB", f"{c_data['Recency'].mean():.1f} ngày", delta_color="inverse")
with m_col3:
    st.metric("Frequency TB", f"{c_data['Frequency'].mean():.1f} lần")
with m_col4:
    st.metric("Monetary TB", f"£{c_data['Monetary'].mean():,.0f}")

st.divider()

# --- CÁC TAB CHỨC NĂNG ---
tab1, tab2, tab3 = st.tabs(["📊 Trực quan hóa & Phân tách", "💡 Chiến lược Marketing", "📋 Danh sách khách hàng"])

with tab1:
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("Vị trí khách hàng trên bản đồ hành vi (PCA)")
        # Kiểm tra xem có cột Component không
        if 'Component 1' in df.columns and 'Component 2' in df.columns:
            fig_pca = px.scatter(
                df, x='Component 1', y='Component 2', 
                color='cluster',
                color_continuous_scale=px.colors.qualitative.Plotly,
                hover_data=['CustomerID', 'Monetary'],
                title="Phân bố các cụm dựa trên Rules + RFM"
            )
            # Highlight cụm đang chọn bằng cách làm mờ các cụm khác (tùy chọn)
            st.plotly_chart(fig_pca, use_container_width=True)
        else:
            st.warning("Thiếu cột 'Component 1/2'. Hãy chạy lại Notebook và lưu đầy đủ cột.")

    with col_right:
        st.subheader("So sánh với Trung bình")
        avg_all = df[['Recency', 'Frequency', 'Monetary']].mean()
        avg_cluster = c_data[['Recency', 'Frequency', 'Monetary']].mean()
        
        comp_df = pd.DataFrame({
            "Chỉ số": ["Recency", "Frequency", "Monetary"],
            "Toàn sàn": avg_all.values,
            "Cụm này": avg_cluster.values
        }).melt(id_vars="Chỉ số")
        
        fig_comp = px.bar(comp_df, x="Chỉ số", y="value", color="variable", barmode="group",
                          labels={"value": "Giá trị", "variable": "Nhóm"})
        st.plotly_chart(fig_comp, use_container_width=True)

with tab2:
    st.subheader("🎯 Hành động đề xuất")
    st.success(f"**Chiến lược:** {current_persona['action']}")
    
    st.subheader("📦 Gợi ý Bundles (Dựa trên Association Rules)")
    if not rules.empty:
        st.write("Dưới đây là các luật kết hợp mạnh nhất có thể áp dụng cho nhóm này:")
        st.dataframe(rules.head(10), use_container_width=True)
    else:
        st.info("Chưa có dữ liệu luật kết hợp.")

with tab3:
    st.subheader("🔍 Danh sách khách hàng chi tiết")
    st.write(f"Hiển thị danh sách khách hàng thuộc cụm {cluster_id}")
    st.dataframe(c_df_view := c_data[['CustomerID', 'Recency', 'Frequency', 'Monetary']].sort_values('Monetary', ascending=False), 
                 use_container_width=True)
    
    # Cho phép download kết quả cụm
    csv = c_df_view.to_csv(index=False).encode('utf-8')
    st.download_button("Tải danh sách (.csv)", data=csv, file_name=f"cluster_{cluster_id}_customers.csv", mime='text/csv')

st.sidebar.markdown("---")
st.sidebar.info("Dashboard được xây dựng để hỗ trợ ra quyết định dựa trên dữ liệu Phân cụm và Luật kết hợp.")