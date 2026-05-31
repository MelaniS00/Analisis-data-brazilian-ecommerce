# 🛒 Olist E-Commerce Dashboard

Dashboard interaktif ini dibuat menggunakan **Streamlit** untuk menganalisis data publik **Olist E-Commerce** dari Brazil. Dashboard ini menyajikan berbagai wawasan mengenai performa bisnis, seperti:

- 📈 Tren penjualan bulanan
- 🏆 Produk terlaris dan paling tidak laku
- 👥 Demografi pelanggan
- 🎯 Segmentasi pelanggan menggunakan metode **RFM (Recency, Frequency, Monetary)**

---

## 📌 Setup Environment

Pastikan **Python** sudah terinstal pada perangkat Anda. Disarankan menggunakan **virtual environment** agar dependensi proyek terisolasi dengan baik.

## 🪄 Clone Repository

```
https://github.com/MelaniS00/Analisis-data-brazilian-ecommerce.git
cd proyek_analisis_data
```

### 1. Menggunakan Anaconda (Rekomendasi)
Buka terminal/command prompt dan jalankan perintah berikut:
```
conda create --name olist-env python=3.9
conda activate olist-env
pip install -r requirements.txt
```

### 2. Setup Environment - Shell/Terminal
```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

### 3. Run steamlit app
```
streamlit run dashboard.py
```
