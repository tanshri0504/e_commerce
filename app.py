import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

# ─────────────────────────────
# PAGE CONFIG
# ─────────────────────────────
st.set_page_config(page_title="Smart E-Commerce Dashboard", layout="wide")

# ─────────────────────────────
# UI DESIGN
# ─────────────────────────────
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg,#eef2ff,#f8fafc);
}
.hero {
    background: linear-gradient(135deg,#0f172a,#1e3a8a,#2563eb);
    padding:30px;
    border-radius:15px;
    color:white;
}
.card {
    background:white;
    padding:15px;
    border-radius:12px;
    box-shadow:0 4px 20px rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────
# HERO SECTION
# ─────────────────────────────
st.markdown("""
<div class="hero">
<h1>🛒 Smart E-Commerce Dashboard</h1>
<p>Sales Analytics • Customer Insights • Interactive Maps</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────
# FILE UPLOAD
# ─────────────────────────────
file = st.sidebar.file_uploader("📂 Upload CSV File", type=["csv"])

if file:
    df = pd.read_csv(file)

    # ─────────────────────────────
    # DATA CLEANING
    # ─────────────────────────────
    df.dropna(inplace=True)
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

    # ─────────────────────────────
    # FILTERS
    # ─────────────────────────────
    st.sidebar.header("🔍 Filters")

    country = st.sidebar.multiselect(
        "Select Country",
        df['Country'].unique(),
        default=df['Country'].unique()
    )

    df = df[df['Country'].isin(country)]

    # ─────────────────────────────
    # KPI SECTION
    # ─────────────────────────────
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Total Sales", f"₹{df['TotalPrice'].sum():,.0f}")
    col2.metric("🧾 Orders", df['InvoiceNo'].nunique())
    col3.metric("👥 Customers", df['CustomerID'].nunique())
    col4.metric("📦 Avg Order", f"₹{df.groupby('InvoiceNo')['TotalPrice'].sum().mean():.0f}")

    st.markdown("---")

    # ─────────────────────────────
    # TABS
    # ─────────────────────────────
    tab1, tab2 = st.tabs(["📊 Graphs", "🌍 Maps"])

    # =============================
    # 📊 GRAPH SECTION
    # =============================
    with tab1:

        st.subheader("🌞 Sales Hierarchy (Sunburst)")
        fig1 = px.sunburst(df, path=['Country', 'Description'], values='TotalPrice')
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("🌳 Treemap")
        fig2 = px.treemap(df, path=['Country', 'Description'], values='TotalPrice')
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("📈 Sales Trend")
        trend = df.groupby(df['InvoiceDate'].dt.date)['TotalPrice'].sum().reset_index()
        fig3 = px.area(trend, x='InvoiceDate', y='TotalPrice')
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("📦 Spending Distribution")
        fig4 = px.box(df, x='Country', y='TotalPrice')
        st.plotly_chart(fig4, use_container_width=True)

    # =============================
    # 🌍 MAP SECTION
    # =============================
    with tab2:

        st.subheader("🌍 Global Sales Map")

        country_sales = df.groupby('Country')['TotalPrice'].sum().reset_index()

        fig5 = px.scatter_geo(
            country_sales,
            locations="Country",
            locationmode='country names',
            size="TotalPrice",
            color="TotalPrice",
            projection="natural earth"
        )

        st.plotly_chart(fig5, use_container_width=True)

        # 3D MAP
        st.subheader("🌆 3D Sales Map")

        coords = {
            "India": [20.5937, 78.9629],
            "USA": [37.0902, -95.7129],
            "UK": [55.3781, -3.4360],
            "Germany": [51.1657, 10.4515]
        }

        country_sales['lat'] = country_sales['Country'].apply(lambda x: coords.get(x, [0,0])[0])
        country_sales['lon'] = country_sales['Country'].apply(lambda x: coords.get(x, [0,0])[1])

        layer = pdk.Layer(
            "ColumnLayer",
            data=country_sales,
            get_position='[lon, lat]',
            get_elevation='TotalPrice',
            elevation_scale=50,
            radius=300000,
        )

        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=20, longitude=0, zoom=1, pitch=50),
            layers=[layer]
        ))

else:
    st.warning("📂 Please upload a CSV file to start")
