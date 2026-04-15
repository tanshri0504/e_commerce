import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Smart E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide"
)

# ─────────────────────────────────────────────
# CUSTOM UI (LIKE YOUR MEDIFIND)
# ─────────────────────────────────────────────
st.markdown("""
<style>
body { background:#f4f7ff; }
.big-card {
    background:white;
    padding:20px;
    border-radius:15px;
    box-shadow:0 4px 20px rgba(0,0,0,0.08);
}
.metric-card {
    background:linear-gradient(135deg,#1e3a8a,#2563eb);
    color:white;
    padding:20px;
    border-radius:15px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TITLE
# ─────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#0f172a,#1e3a8a);
padding:30px;border-radius:15px;color:white">
<h1>🛒 Smart E-Commerce Analytics</h1>
<p>Sales • Customers • Recommendations • AI Insights</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FILE UPLOAD
# ─────────────────────────────────────────────
st.sidebar.header("📂 Upload Dataset")
file = st.sidebar.file_uploader("Upload CSV (Kaggle dataset)", type=["csv"])

if file:
    df = pd.read_csv(file)
else:
    st.warning("Upload dataset to continue")
    st.stop()

# ─────────────────────────────────────────────
# BASIC CLEANING
# ─────────────────────────────────────────────
df.dropna(inplace=True)

# Ensure required columns
required = ['CustomerID','InvoiceNo','Quantity','UnitPrice','Country']
if not all(col in df.columns for col in required):
    st.error("Dataset must contain: CustomerID, InvoiceNo, Quantity, UnitPrice, Country")
    st.stop()

df['TotalPrice'] = df['Quantity'] * df['UnitPrice']

# ─────────────────────────────────────────────
# KPI SECTION
# ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Total Sales", f"₹{df['TotalPrice'].sum():,.0f}")
col2.metric("🧾 Orders", df['InvoiceNo'].nunique())
col3.metric("👥 Customers", df['CustomerID'].nunique())
col4.metric("📦 Avg Order Value", f"₹{df.groupby('InvoiceNo')['TotalPrice'].sum().mean():.0f}")

st.markdown("---")

# ─────────────────────────────────────────────
# SALES ANALYSIS
# ─────────────────────────────────────────────
st.subheader("📊 Sales Analysis")

country_sales = df.groupby('Country')['TotalPrice'].sum().reset_index()

fig = px.bar(country_sales, x='Country', y='TotalPrice',
             color='TotalPrice', title="Sales by Country")
st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# TOP PRODUCTS
# ─────────────────────────────────────────────
st.subheader("🔥 Top Selling Products")

top_products = df.groupby('Description')['Quantity'].sum().nlargest(10).reset_index()

fig2 = px.bar(top_products, x='Quantity', y='Description',
              orientation='h', title="Top Products")
st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────────────────────────
# CUSTOMER SEGMENTATION (ML)
# ─────────────────────────────────────────────
st.subheader("🤖 Customer Segmentation (AI)")

customer = df.groupby('CustomerID').agg({
    'TotalPrice':'sum',
    'InvoiceNo':'count'
}).rename(columns={'InvoiceNo':'Frequency'})

scaler = StandardScaler()
scaled = scaler.fit_transform(customer)

kmeans = KMeans(n_clusters=3, random_state=42)
customer['Cluster'] = kmeans.fit_predict(scaled)

fig3 = px.scatter(customer, x='TotalPrice', y='Frequency',
                  color='Cluster', title="Customer Segments")
st.plotly_chart(fig3, use_container_width=True)

# ─────────────────────────────────────────────
# RECOMMENDATION SYSTEM
# ─────────────────────────────────────────────
st.subheader("🛍️ Product Recommendation")

product = st.selectbox("Select Product", df['Description'].unique())

product_df = df[df['Description'] == product]

customers = product_df['CustomerID'].unique()

recommended = df[df['CustomerID'].isin(customers)]
recommended = recommended[recommended['Description'] != product]

top_recommend = recommended['Description'].value_counts().head(5)

st.write("### Recommended Products:")
for item in top_recommend.index:
    st.success(item)

# ─────────────────────────────────────────────
# HEATMAP
# ─────────────────────────────────────────────
st.subheader("🔥 Correlation Heatmap")

corr = df[['Quantity','UnitPrice','TotalPrice']].corr()

fig4 = px.imshow(corr, text_auto=True, title="Correlation Matrix")
st.plotly_chart(fig4, use_container_width=True)

# ─────────────────────────────────────────────
# DOWNLOAD
# ─────────────────────────────────────────────
csv = df.to_csv(index=False)

st.download_button("📥 Download Processed Data", csv, "processed_data.csv")
