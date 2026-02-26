import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Pharma Executive Dashboard", layout="wide")

# ---------------- LOAD DATA ----------------

@st.cache_data
def load_data():
df = pd.read_csv("cleaned_pharma_sales.csv")

```
date_cols = ["Billing_Date","Mfg_Date","Expiry_Date","SO_Creation_Date"]
for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors="coerce")

today = pd.Timestamp.now().normalize()
df["Days_to_Expiry"] = (df["Expiry_Date"] - today).dt.days

return df
```

df = load_data()

# ---------------- SIDEBAR ----------------

st.sidebar.title("Filters")

product = st.sidebar.multiselect(
"Product",
df["Material_Name"].dropna().unique()
)

year = st.sidebar.multiselect(
"Year",
df["Billing_Date"].dt.year.unique()
)

if product:
df = df[df["Material_Name"].isin(product)]

if year:
df = df[df["Billing_Date"].dt.year.isin(year)]

# ---------------- KPIs ----------------

st.title("💊 Pharma Executive Dashboard")

c1,c2,c3,c4,c5 = st.columns(5)

c1.metric("Revenue", f"{df['Revenue'].sum():,.0f}")
c2.metric("Units Sold", f"{df['Billing_Qty'].sum():,.0f}")
c3.metric("Customers", df["Sold_to"].nunique())
c4.metric("Avg Lead Time", f"{df['Lead_Time'].mean():.1f} days")
c5.metric("Expiry < 90 Days", df[df["Days_to_Expiry"]<90].shape[0])

st.markdown("---")

# ---------------- REVENUE TREND ----------------

st.subheader("Revenue Trend")

monthly = df.groupby(df["Billing_Date"].dt.to_period("M"))["Revenue"].sum().reset_index()
monthly["Billing_Date"] = monthly["Billing_Date"].astype(str)

fig1 = px.line(monthly, x="Billing_Date", y="Revenue", markers=True)
st.plotly_chart(fig1, use_container_width=True)

# ---------------- TOP PRODUCTS ----------------

col1, col2 = st.columns(2)

top_products = df.groupby("Material_Name")["Revenue"].sum().sort_values().tail(10)
col1.subheader("Top Products")
col1.plotly_chart(px.bar(top_products, orientation="h"), use_container_width=True)

top_customers = df.groupby("Sold_to")["Revenue"].sum().sort_values().tail(10)
col2.subheader("Top Customers")
col2.plotly_chart(px.bar(top_customers, orientation="h"), use_container_width=True)

# ---------------- EXPIRY ----------------

st.subheader("Expiry Risk")

fig2 = px.histogram(df[df["Days_to_Expiry"]>=0], x="Days_to_Expiry")
st.plotly_chart(fig2, use_container_width=True)

st.dataframe(
df[df["Days_to_Expiry"]<90][["Material_Name","Batch","Expiry_Date","Days_to_Expiry"]]
)
