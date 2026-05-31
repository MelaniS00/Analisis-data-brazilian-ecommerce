import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# ==============================
# Konfigurasi Halaman
# ==============================
st.set_page_config(page_title="Olist E-Commerce Dashboard", page_icon="🛒", layout="wide")

# Set style seaborn
sns.set_theme(style='darkgrid')

# ==============================
# Helper Functions
# ==============================
def create_monthly_orders_df(df):
    monthly_orders_df = df.resample(rule='M', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    monthly_orders_df.index = monthly_orders_df.index.strftime('%Y-%m')
    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={
        "order_purchase_timestamp": "order_month",
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    return monthly_orders_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english")["order_item_id"].count().reset_index()
    sum_order_items_df.rename(columns={"order_item_id": "quantity"}, inplace=True)
    sum_order_items_df = sum_order_items_df.sort_values(by="quantity", ascending=False)
    return sum_order_items_df

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_unique_id.nunique().reset_index()
    bystate_df.rename(columns={"customer_unique_id": "customer_count"}, inplace=True)
    return bystate_df.sort_values(by="customer_count", ascending=False)

def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").customer_unique_id.nunique().reset_index()
    bycity_df.rename(columns={"customer_unique_id": "customer_count"}, inplace=True)
    return bycity_df.sort_values(by="customer_count", ascending=False)

def create_rfm_df(df):
    current_date = df['order_purchase_timestamp'].max()
    rfm_df = df.groupby('customer_unique_id', as_index=False).agg({
        'order_purchase_timestamp': lambda x: (current_date - x.max()).days,
        'order_id': 'nunique',
        'payment_value': 'sum'
    })
    rfm_df.columns = ['customer_unique_id', 'recency', 'frequency', 'monetary']
    return rfm_df

# ==============================
# Load Data
# ==============================
@st.cache_data
def load_data():
    all_df = pd.read_csv("main_data.zip")
    datetime_cols = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"]
    for col in datetime_cols:
        all_df[col] = pd.to_datetime(all_df[col])
    return all_df

all_df = load_data()

# ==============================
# Sidebar untuk Filter Data
# ==============================
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    st.header("Filter Data")
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Terapkan filter pada dataset
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                 (all_df["order_purchase_timestamp"] <= str(end_date))]

# Eksekusi helper functions
monthly_orders_df = create_monthly_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
bystate_df = create_bystate_df(main_df)
bycity_df = create_bycity_df(main_df)
rfm_df = create_rfm_df(main_df)

# ==============================
# Main Dashboard
# ==============================
st.title("🛒 Olist E-Commerce Dashboard")
st.markdown("Dashboard interaktif untuk menganalisis performa penjualan, demografi, dan metrik RFM.")

# --- Bagian 1: Sales & Revenue ---
st.header("1. Sales & Revenue Performance")
col1, col2 = st.columns(2)

with col1:
    total_orders = monthly_orders_df.order_count.sum()
    st.metric("Total Orders", value=total_orders)
with col2:
    total_revenue = monthly_orders_df.revenue.sum()
    st.metric("Total Revenue", value=f"BRL {total_revenue:,.2f}")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 6))

ax[0].plot(monthly_orders_df["order_month"], monthly_orders_df["order_count"], marker='o', linewidth=2, color="#72BCD4")
ax[0].set_title("Total Orders per Month", fontsize=16)
ax[0].tick_params(axis='x', rotation=45)
ax[0].set_ylabel("Number of Orders")

ax[1].plot(monthly_orders_df["order_month"], monthly_orders_df["revenue"], marker='o', linewidth=2, color="#2E8B57")
ax[1].set_title("Total Revenue per Month (BRL)", fontsize=16)
ax[1].tick_params(axis='x', rotation=45)
ax[1].set_ylabel("Revenue")

st.pyplot(fig)
st.markdown("**Insight:** Terdapat tren kenaikan transaksi yang cukup konsisten dari awal tahun 2017 dan puncaknya terjadi pada bulan November 2017 (kemungkinan efek Black Friday). Tren penjualan (jumlah order) berbanding lurus dengan tren revenue.")
st.markdown("---")

# --- Bagian 2: Best & Worst Products ---
st.header("2. Best & Worst Performing Products")
col1, col2 = st.columns(2)

with col1:
    fig_best, ax_best = plt.subplots(figsize=(10, 6))
    sns.barplot(x="quantity", y="product_category_name_english", data=sum_order_items_df.head(5), palette="Blues_r", hue="product_category_name_english", legend=False, ax=ax_best)
    ax_best.set_title("Top 5 Best Performing Products", fontsize=15)
    ax_best.set_xlabel("Quantity Sold")
    ax_best.set_ylabel(None)
    st.pyplot(fig_best)

with col2:
    fig_worst, ax_worst = plt.subplots(figsize=(10, 6))
    sns.barplot(x="quantity", y="product_category_name_english", data=sum_order_items_df.sort_values(by="quantity", ascending=True).head(5), palette="Reds_r", hue="product_category_name_english", legend=False, ax=ax_worst)
    ax_worst.set_title("Top 5 Worst Performing Products", fontsize=15)
    ax_worst.set_xlabel("Quantity Sold")
    ax_worst.set_ylabel(None)
    ax_worst.invert_xaxis()
    ax_worst.yaxis.set_label_position("right")
    ax_worst.yaxis.tick_right()
    st.pyplot(fig_worst)

st.markdown("**Insight:** Kategori produk yang paling laku didominasi oleh perabotan rumah tangga (bed bath table, furniture decor) dan kesehatan/kecantikan (health beauty). Sebaliknya, barang spesifik seperti asuransi (security and services) dan pakaian anak (fashion children clothes) memiliki angka penjualan terendah di platform.")
st.markdown("---")

# --- Bagian 3: Customer Demographics ---
st.header("3. Customer Demographics")
col1, col2 = st.columns(2)

with col1:
    fig_state, ax_state = plt.subplots(figsize=(10, 6))
    sns.barplot(x="customer_count", y="customer_state", data=bystate_df.head(10), palette="viridis", hue="customer_state", legend=False, ax=ax_state)
    ax_state.set_title("Top 10 States by Customer Count", fontsize=15)
    ax_state.set_xlabel("Number of Customers")
    ax_state.set_ylabel(None)
    st.pyplot(fig_state)

with col2:
    fig_city, ax_city = plt.subplots(figsize=(10, 6))
    sns.barplot(x="customer_count", y="customer_city", data=bycity_df.head(10), palette="magma", hue="customer_city", legend=False, ax=ax_city)
    ax_city.set_title("Top 10 Cities by Customer Count", fontsize=15)
    ax_city.set_xlabel("Number of Customers")
    ax_city.set_ylabel(None)
    st.pyplot(fig_city)

st.markdown("**Insight:** Pelanggan E-Commerce Olist sangat terkonsentrasi di wilayah tenggara Brazil. Negara bagian SP (São Paulo), RJ (Rio de Janeiro), dan MG (Minas Gerais) adalah penyumbang pelanggan terbesar. Hal ini sejalan dengan visualisasi kota, di mana São Paulo menduduki peringkat pertama dengan selisih jumlah pelanggan yang sangat jauh dibandingkan kota lainnya.")
st.markdown("---")

# --- Bagian 4: RFM Analysis ---
st.header("4. RFM Analysis (Recency, Frequency, Monetary)")
st.markdown("Identifikasi segmen pelanggan terbaik (*Champions*) untuk menentukan target promosi.")

col1, col2, col3 = st.columns(3)

with col1:
    fig_r, ax_r = plt.subplots(figsize=(8, 6))
    sns.barplot(y="recency", x="customer_unique_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette="Greens_r", hue="customer_unique_id", legend=False, ax=ax_r)
    ax_r.set_title("By Recency (days)", fontsize=14)
    ax_r.tick_params(axis='x', rotation=45, labelsize=8)
    ax_r.set_ylabel(None)
    ax_r.set_xlabel(None)
    # Menjaga ruang visual jika nilai recency 0
    ax_r.set_ylim(bottom=0, top=rfm_df['recency'].max() * 0.05)
    st.pyplot(fig_r)

with col2:
    fig_f, ax_f = plt.subplots(figsize=(8, 6))
    sns.barplot(y="frequency", x="customer_unique_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette="Blues_r", hue="customer_unique_id", legend=False, ax=ax_f)
    ax_f.set_title("By Frequency (times)", fontsize=14)
    ax_f.tick_params(axis='x', rotation=45, labelsize=8)
    ax_f.set_ylabel(None)
    ax_f.set_xlabel(None)
    st.pyplot(fig_f)

with col3:
    fig_m, ax_m = plt.subplots(figsize=(8, 6))
    sns.barplot(y="monetary", x="customer_unique_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette="Oranges_r", hue="customer_unique_id", legend=False, ax=ax_m)
    ax_m.set_title("By Monetary (BRL)", fontsize=14)
    ax_m.tick_params(axis='x', rotation=45, labelsize=8)
    ax_m.set_ylabel(None)
    ax_m.set_xlabel(None)
    st.pyplot(fig_m)

st.markdown("""
**Insight:**
- **Recency:** Terdapat beberapa pelanggan yang baru saja bertransaksi di rentang waktu 0-2 hari sebelum data terakhir direkam. Mereka adalah segmen pelanggan aktif (recent).
- **Frequency:** Mayoritas transaksi di E-Commerce Olist didominasi oleh pembeli sekali waktu (one-time buyer). Namun, terdapat beberapa pelanggan sangat loyal yang melakukan pembelian hingga lebih dari 15 kali (seperti pelanggan dengan ID berawalan 8d50f...).
- **Monetary:** Pelanggan yang menghasilkan revenue paling besar (mencapai lebih dari 100.000 BRL) ternyata bukanlah pelanggan yang paling sering berbelanja. Hal ini mengindikasikan adanya transaksi B2B (pembelian borongan bernilai tinggi) atau pembelian barang mewah (high-ticket items) yang dilakukan hanya dalam 1-2 kali transaksi.
""")

# Footer
st.caption("Copyright © Melani Siyamafiroh 2026")
