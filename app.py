import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_pharma_sales.csv", parse_dates=[
        "Billing_Date", "Mfg_Date", "Expiry_Date", "SO_Creation_Date"
    ])
    return df

df = load_data()

st.title("💊 Pharma Sales Analytics Dashboard")

# Sidebar filters
st.sidebar.header("Filters")

material = st.sidebar.multiselect(
    "Select Product",
    df["Material_Name"].unique()
)

if material:
    df = df[df["Material_Name"].isin(material)]

# KPI Section
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Revenue", f"{df['Revenue'].sum():,.0f}")
col2.metric("Total Quantity", f"{df['Billing_Qty'].sum():,.0f}")
col3.metric("Avg Lead Time", f"{df['Lead_Time'].mean():.1f} days")
col4.metric("Expiring < 90 Days", f"{(df['Days_to_Expiry'] < 90).sum()}")

# Revenue Trend
st.subheader("📈 Monthly Revenue Trend")

monthly = df.groupby(df["Billing_Date"].dt.to_period("M"))["Revenue"].sum().reset_index()
monthly["Billing_Date"] = monthly["Billing_Date"].astype(str)

fig = px.line(monthly, x="Billing_Date", y="Revenue", markers=True)
st.plotly_chart(fig, use_container_width=True)

# Top Products
st.subheader("🏆 Top 10 Products by Revenue")

top_products = df.groupby("Material_Name")["Revenue"].sum().sort_values(ascending=False).head(10)
fig2 = px.bar(top_products, orientation="h")
st.plotly_chart(fig2, use_container_width=True)

# Top Customers
st.subheader("👥 Top Customers")

top_customers = df.groupby("Sold_to")["Revenue"].sum().sort_values(ascending=False).head(10)
fig3 = px.bar(top_customers, orientation="h")
st.plotly_chart(fig3, use_container_width=True)

# Expiry Risk
st.subheader("⚠️ Expiry Risk Analysis")

expiry = df[df["Days_to_Expiry"] < 90]
st.write(f"Products expiring in next 90 days: {len(expiry)}")

st.dataframe(expiry[[
    "Material_Name", "Batch", "Expiry_Date", "Days_to_Expiry"
]].head(20))