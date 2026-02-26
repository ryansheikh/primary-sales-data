import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Pharma Executive Dashboard", layout="wide")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_pharma_sales.csv",
                     parse_dates=["Billing_Date","Mfg_Date","Expiry_Date","SO_Creation_Date"])

    today = pd.Timestamp.now().normalize()
    df["Days_to_Expiry"] = (df["Expiry_Date"] - today).dt.days

    return df

df = load_data()

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("Filters")

selected_product = st.sidebar.multiselect(
    "Select Product",
    df["Material_Name"].dropna().unique()
)

selected_year = st.sidebar.multiselect(
    "Select Year",
    df["Billing_Date"].dt.year.unique()
)

if selected_product:
    df = df[df["Material_Name"].isin(selected_product)]

if selected_year:
    df = df[df["Billing_Date"].dt.year.isin(selected_year)]

# =========================
# TITLE
# =========================
st.title("💊 Pharma Sales Executive Dashboard")

# =========================
# KPI SECTION
# =========================
col1, col2, col3, col4, col5 = st.columns(5)

total_revenue = df["Revenue"].sum()
total_qty = df["Billing_Qty"].sum()
avg_lead = df["Lead_Time"].mean()
expiry_90 = df[df["Days_to_Expiry"] < 90].shape[0]
unique_customers = df["Sold_to"].nunique()

col1.metric("Total Revenue", f"{total_revenue:,.0f}")
col2.metric("Total Quantity Sold", f"{total_qty:,.0f}")
col3.metric("Avg Lead Time (Days)", f"{avg_lead:.1f}")
col4.metric("Expiring < 90 Days", expiry_90)
col5.metric("Active Customers", unique_customers)

st.markdown("---")

# =========================
# 1️⃣ Revenue Trend
# =========================
st.subheader("📈 Monthly Revenue Trend")

monthly = df.groupby(df["Billing_Date"].dt.to_period("M"))["Revenue"].sum().reset_index()
monthly["Billing_Date"] = monthly["Billing_Date"].astype(str)

fig1 = px.line(monthly, x="Billing_Date", y="Revenue", markers=True)
st.plotly_chart(fig1, use_container_width=True)

# =========================
# 2️⃣ Top Products
# =========================
st.subheader("🏆 Top 10 Products by Revenue")

top_products = df.groupby("Material_Name")["Revenue"].sum().sort_values(ascending=False).head(10)
fig2 = px.bar(top_products, orientation="h")
st.plotly_chart(fig2, use_container_width=True)

# =========================
# 3️⃣ Revenue by Distributor
# =========================
st.subheader("🚚 Revenue by Distribution Partner")

dist = df.groupby("SDP_Name")["Revenue"].sum().sort_values(ascending=False).head(10)
fig3 = px.bar(dist, orientation="h")
st.plotly_chart(fig3, use_container_width=True)

# =========================
# 4️⃣ Customer Concentration
# =========================
st.subheader("👥 Top Customers by Revenue")

top_customers = df.groupby("Sold_to")["Revenue"].sum().sort_values(ascending=False).head(10)
fig4 = px.bar(top_customers, orientation="h")
st.plotly_chart(fig4, use_container_width=True)

# =========================
# 5️⃣ Expiry Risk Analysis
# =========================
st.subheader("⚠️ Expiry Risk Analysis")

expiry_df = df[df["Days_to_Expiry"] >= 0]

fig5 = px.histogram(expiry_df, x="Days_to_Expiry", nbins=50)
st.plotly_chart(fig5, use_container_width=True)

st.write("Products expiring within 90 days:")
st.dataframe(df[df["Days_to_Expiry"] < 90][[
    "Material_Name","Batch","Expiry_Date","Days_to_Expiry"
]].sort_values("Days_to_Expiry"))

# =========================
# 6️⃣ Lead Time Distribution
# =========================
st.subheader("⏳ Order Fulfillment Lead Time")

fig6 = px.histogram(df, x="Lead_Time", nbins=40)
st.plotly_chart(fig6, use_container_width=True)

# =========================
# 7️⃣ Product Age When Sold
# =========================
st.subheader("📦 Product Freshness (Age When Sold)")

df["Product_Age_When_Sold"] = (df["Billing_Date"] - df["Mfg_Date"]).dt.days
fig7 = px.box(df, y="Product_Age_When_Sold")
st.plotly_chart(fig7, use_container_width=True)

# =========================
# 8️⃣ Revenue Contribution %
# =========================
st.subheader("📊 Revenue Contribution by Product")

product_rev = df.groupby("Material_Name")["Revenue"].sum().reset_index()
product_rev = product_rev.sort_values("Revenue", ascending=False)
product_rev["Revenue %"] = product_rev["Revenue"] / product_rev["Revenue"].sum() * 100

fig8 = px.pie(product_rev.head(10), names="Material_Name", values="Revenue")
st.plotly_chart(fig8, use_container_width=True)
