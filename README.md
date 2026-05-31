# 🛒 Olist E-Commerce Dashboard

Dashboard interaktif ini dibuat menggunakan **Streamlit** untuk menganalisis data publik E-Commerce Olist dari Brazil. Dashboard ini menyajikan wawasan mengenai performa penjualan bulanan, produk terlaris dan paling tidak laku, demografi pelanggan, serta segmentasi pelanggan menggunakan analisis RFM (Recency, Frequency, Monetary).

## 📌 Setup Environment
Untuk menjalankan proyek ini di mesin lokal, pastikan Anda telah menginstal Python. Sangat disarankan untuk menggunakan *virtual environment*.

### 1. Menggunakan Anaconda (Rekomendasi)
Buka terminal/command prompt dan jalankan perintah berikut:
```bash
conda create --name olist-env python=3.9
conda activate olist-env
pip install -r requirements.txt


### Setup Environment - Shell/Terminal
```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

### Run steamlit app
```
streamlit run dashboard.py
```
