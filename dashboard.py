import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# ==========================================
# Konfigurasi Halaman Streamlit
# ==========================================
st.set_page_config(page_title="Olist E-Commerce Dashboard", page_icon="📊", layout="wide")

# Set tema visualisasi menggunakan seaborn
sns.set_theme(style='darkgrid')

# ==========================================
# Helper Functions (Fungsi Pembantu Analisis)
# ==========================================

# Pertanyaan 1: Tren Penjualan Bulanan
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
    
    # Menghitung order growth untuk menentukan kenaikan/penurunan terbesar seperti di colab
    monthly_orders_df["order_growth"] = monthly_orders_df["order_count"].pct_change() * 100
    return monthly_orders_df

# Pertanyaan 2: Performa Kategori Produk
def create_sum_order_items_df(df):
    # Dioptimalkan menggunakan .size() agar tidak memerlukan kolom order_item_id tambahan
    sum_order_items_df = df.groupby("product_category_name_english").size().reset_index(name="quantity")
    sum_order_items_df = sum_order_items_df.sort_values(by="quantity", ascending=False)
    return sum_order_items_df

# Pertanyaan 3: Distribusi Geografis Pelanggan
def create_geographic_df(df):
    bystate_df = df.groupby("customer_state")["customer_unique_id"].nunique().reset_index()
    bystate_df.rename(columns={"customer_state": "state", "customer_unique_id": "customer_count"}, inplace=True)
    bystate_df = bystate_df.sort_values(by="customer_count", ascending=False)

    bycity_df = df.groupby("customer_city")["customer_unique_id"].nunique().reset_index()
    bycity_df.rename(columns={"customer_city": "city", "customer_unique_id": "customer_count"}, inplace=True)
    bycity_df = bycity_df.sort_values(by="customer_count", ascending=False)
    
    return bystate_df, bycity_df

# Pertanyaan 4: Analisis RFM & Segmentasi Pelanggan
def create_rfm_df(df):
    latest_date = df["order_purchase_timestamp"].max()
    rfm_df = df.groupby(by="customer_unique_id", as_index=False).agg({
        "order_purchase_timestamp": lambda x: (latest_date - x.max()).days, # Recency
        "order_id": "nunique",                                            # Frequency
        "payment_value": "sum"                                            # Monetary
    })
    rfm_df.columns = ["customer_unique_id", "recency", "frequency", "monetary"]
    
    # Mengamankan scoring RFM menggunakan metode rank(method='first') seperti di notebook colab
    if len(rfm_df) >= 5:
        rfm_df['r_score'] = pd.qcut(rfm_df['recency'], q=5, labels=[5, 4, 3, 2, 1])
        rfm_df['f_score'] = pd.qcut(rfm_df['frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])
        rfm_df['m_score'] = pd.qcut(rfm_df['monetary'], q=5, labels=[1, 2, 3, 4, 5])
        rfm_df['rfm_score'] = rfm_df['r_score'].astype(int) + rfm_df['f_score'].astype(int) + rfm_df['m_score'].astype(int)
        
        # Mapping segmentasi sesuai dengan logika notebook
        def assign_segment(score):
            if score >= 13: return "Top Customer"
            elif score >= 11: return "High Value"
            elif score >= 9: return "Loyal"
            elif score >= 7: return "Promising"
            elif score >= 6: return "New Customer"
            elif score >= 5: return "Need Attention"
            elif score >= 4: return "At Risk"
            else: return "Hibernating"
            
        rfm_df['rfm_segment'] = rfm_df['rfm_score'].apply(assign_segment)
    else:
        rfm_df['rfm_segment'] = "Standard"
        
    return rfm_df

# ==========================================
# Memuat Dataset Utama (Data Loading)
# ==========================================
@st.cache_data
def load_data():
    # SOLUSI MEMORYERROR: Hanya memuat 8 kolom yang esensial untuk visualisasi.
    # Kolom teks deskripsi dan teks ulasan yang memakan RAM sangat besar akan diabaikan.
    columns_needed = [
        "order_id", 
        "customer_unique_id", 
        "order_purchase_timestamp", 
        "payment_value", 
        "product_category_name_english", 
        "customer_state", 
        "customer_city", 
        "review_score"
    ]
    df = pd.read_csv("main_data.zip", usecols=columns_needed)
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    return df

try:
    main_df = load_data()
except FileNotFoundError:
    st.error("Berkas 'main_data.csv' tidak ditemukan! Pastikan file berada di direktori yang sama dengan dashboard.py.")
    st.stop()

# ==========================================
# Komponen Sidebar & Penapisan Rentang Waktu
# ==========================================
min_date = main_df["order_purchase_timestamp"].min().date()
max_date = main_df["order_purchase_timestamp"].max().date()

with st.sidebar:
    st.title("🛒 Olist E-Commerce")
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png", width=150)
    
    # Input rentang tanggal dari user
    date_range = st.date_input(
        label='Pilih Rentang Waktu Analisis:',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# REVIEWER KRITERIA 4: Blok try-except penanganan filter tanggal
try:
    start_date, end_date = date_range
    filtered_df = main_df[(main_df["order_purchase_timestamp"].dt.date >= start_date) & 
                          (main_df["order_purchase_timestamp"].dt.date <= end_date)]
except ValueError:
    st.warning("⚠️ Silakan lengkapi parameter rentang waktu pada sidebar (Pilih Tanggal Mulai dan Tanggal Selesai).")
    st.stop()

# Memproses data sekunder berdasarkan dataframe yang telah difilter
monthly_orders_df = create_monthly_orders_df(filtered_df)
sum_order_items_df = create_sum_order_items_df(filtered_df)
bystate_df, bycity_df = create_geographic_df(filtered_df)
rfm_df = create_rfm_df(filtered_df)

# ==========================================
# Ringkasan Metrik Utama (KPI Dashboard)
# ==========================================
st.title("📊 Olist E-Commerce Performance Dashboard")
st.markdown(f"Menampilkan performa bisnis dari rentang waktu **{start_date}** hingga **{end_date}**")

col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
with col_kpi1:
    st.metric("Total Orders", value=f"{filtered_df['order_id'].nunique():,}")
with col_kpi2:
    st.metric("Total Revenue", value=f"BRL {filtered_df['payment_value'].sum():,.2f}")
with col_kpi3:
    st.metric("Unique Customers", value=f"{filtered_df['customer_unique_id'].nunique():,}")
with col_kpi4:
    st.metric("Avg Review Score", value=f"{filtered_df['review_score'].mean():.2f} ⭐" if "review_score" in filtered_df.columns else "N/A")

st.markdown("---")

# ==========================================
# Struktur Visualisasi Berdasarkan Tab
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Tren Penjualan Bulanan", 
    "📦 Performa Kategori Produk", 
    "🌍 Distribusi Geografis", 
    "💎 Segmentasi Pelanggan (RFM)"
])

# --- TAB 1: Pertanyaan 1 (Tren Penjualan Bulanan & Peak Months) ---
with tab1:
    st.subheader("Tren Jumlah Pesanan dan Total Revenue Bulanan")
    
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 6))
    
    # Tren Jumlah Pesanan
    ax[0].plot(monthly_orders_df["order_month"], monthly_orders_df["order_count"], marker='o', linewidth=2, color="#72BCD4")
    ax[0].set_title("Monthly Total Orders Trends", fontsize=16)
    ax[0].set_ylabel("Number of Orders")
    ax[0].tick_params(axis='x', rotation=45)
    
    # Menandai titik puncak kenaikan/penurunan jika data mencukupi seperti di Colab
    if len(monthly_orders_df) > 1 and not monthly_orders_df["order_growth"].isnull().all():
        max_inc_idx = monthly_orders_df["order_growth"].idxmax()
        max_dec_idx = monthly_orders_df["order_growth"].idxmin()
        
        # Plot titik ekstrem
        ax[0].scatter(monthly_orders_df.loc[max_inc_idx, "order_month"], monthly_orders_df.loc[max_inc_idx, "order_count"], s=150, color="green", zorder=5)
        ax[0].scatter(monthly_orders_df.loc[max_dec_idx, "order_month"], monthly_orders_df.loc[max_dec_idx, "order_count"], s=150, color="red", zorder=5)
        
        ax[0].annotate(f"Highest Increase\n({monthly_orders_df.loc[max_inc_idx, 'order_growth']:.1f}%)", 
                       (monthly_orders_df.loc[max_inc_idx, "order_month"], monthly_orders_df.loc[max_inc_idx, "order_count"]),
                       textcoords="offset points", xytext=(10, 10), weight='bold', color='green')
        ax[0].annotate(f"Highest Decrease\n({monthly_orders_df.loc[max_dec_idx, 'order_growth']:.1f}%)", 
                       (monthly_orders_df.loc[max_dec_idx, "order_month"], monthly_orders_df.loc[max_dec_idx, "order_count"]),
                       textcoords="offset points", xytext=(10, -30), weight='bold', color='red')

    # Tren Total Revenue
    ax[1].plot(monthly_orders_df["order_month"], monthly_orders_df["revenue"], marker='o', linewidth=2, color="#2E8B57")
    ax[1].set_title("Monthly Revenue Trends (BRL)", fontsize=16)
    ax[1].set_ylabel("Revenue Value")
    ax[1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    st.pyplot(fig)


# --- TAB 2: Pertanyaan 2 (Kategori Produk Tertinggi & Terendah) ---
with tab2:
    st.subheader("Kategori Produk dengan Penjualan Tertinggi dan Terendah")
    
    fig_prod, ax_prod = plt.subplots(nrows=1, ncols=2, figsize=(20, 6))
    
    # Top 5 Kategori Produk
    sns.barplot(x="quantity", y="product_category_name_english", data=sum_order_items_df.head(5), palette="Blues_r", hue="product_category_name_english", legend=False, ax=ax_prod[0])
    ax_prod[0].set_title("Top 5 Most Demanded Product Categories", fontsize=15)
    ax_prod[0].set_xlabel("Quantity Sold")
    ax_prod[0].set_ylabel(None)
    
    # Bottom 5 Kategori Produk
    sns.barplot(x="quantity", y="product_category_name_english", data=sum_order_items_df.tail(5).sort_values(by="quantity", ascending=True), palette="Reds_r", hue="product_category_name_english", legend=False, ax=ax_prod[1])
    ax_prod[1].set_title("Bottom 5 Least Demanded Product Categories", fontsize=15)
    ax_prod[1].set_xlabel("Quantity Sold")
    ax_prod[1].set_ylabel(None)
    ax_prod[1].yaxis.tick_right()
    ax_prod[1].yaxis.set_label_position("right")
    
    plt.tight_layout()
    st.pyplot(fig_prod)


# --- TAB 3: Pertanyaan 3 (Distribusi Geografis & Wilayah Potensial) ---
with tab3:
    st.subheader("Distribusi Geografis Pelanggan Berdasarkan State dan City")
    
    fig_geo, ax_geo = plt.subplots(nrows=1, ncols=2, figsize=(20, 6))
    
    # Top 10 States Pelanggan Terbanyak
    sns.barplot(x="customer_count", y="state", data=bystate_df.head(10), palette="GnBu_r", hue="state", legend=False, ax=ax_geo[0])
    ax_geo[0].set_title("Top 10 States with Highest Customer Concentration", fontsize=15)
    ax_geo[0].set_xlabel("Number of Unique Customers")
    ax_geo[0].set_ylabel(None)
    
    # Top 10 Cities Pelanggan Terbanyak
    sns.barplot(x="customer_count", y="city", data=bycity_df.head(10), palette="Purples_r", hue="city", legend=False, ax=ax_geo[1])
    ax_geo[1].set_title("Top 10 Cities with Highest Customer Concentration", fontsize=15)
    ax_geo[1].set_xlabel("Number of Unique Customers")
    ax_geo[1].set_ylabel(None)
    ax_geo[1].yaxis.tick_right()
    ax_geo[1].yaxis.set_label_position("right")
    
    plt.tight_layout()
    st.pyplot(fig_geo)


# --- TAB 4: Pertanyaan 4 (Segmentasi Profil Pelanggan RFM) ---
with tab4:
    st.subheader("Segmentasi Profil Pelanggan Berdasarkan Analisis RFM")
    
    # Parameter RFM Rata-rata
    col_rfm1, col_rfm2, col_rfm3 = st.columns(3)
    with col_rfm1:
        st.metric("Average Recency", value=f"{rfm_df['recency'].mean():.1f} Days")
    with col_rfm2:
        st.metric("Average Frequency", value=f"{rfm_df['frequency'].mean():.2f} Times")
    with col_rfm3:
        st.metric("Average Monetary", value=f"BRL {rfm_df['monetary'].mean():,.2f}")
    
    # Visualisasi Distribusi Segmen Pelanggan
    if 'rfm_segment' in rfm_df.columns:
        segment_counts = rfm_df['rfm_segment'].value_counts().reset_index()
        segment_counts.columns = ['Segment', 'Customer Count']
        
        fig_rfm, ax_rfm = plt.subplots(figsize=(12, 5))
        sns.barplot(x="Customer Count", y="Segment", data=segment_counts, palette="viridis", hue="Segment", legend=False, ax=ax_rfm)
        ax_rfm.set_title("Customer Distribution by RFM Segment", fontsize=16)
        ax_rfm.set_xlabel("Number of Customers")
        ax_rfm.set_ylabel(None)
        
        plt.tight_layout()
        st.pyplot(fig_rfm)
