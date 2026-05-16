# 💧 SiagaAir — Prediksi Pintu Air Jakarta

Aplikasi Streamlit untuk visualisasi dan prediksi tinggi muka air di 12 pos pintu air Jakarta.

---

## 📁 Struktur Folder

```
project/
├── app.py                    ← Aplikasi utama Streamlit
├── requirements.txt          ← Dependensi Python
├── generate_dummy_pkl.py     ← Script pembuat data uji (opsional)
└── models/
    ├── BendungKatulampa_results.pkl
    ├── Manggarai BKB_results.pkl
    ├── PA Karet_results.pkl
    ├── Pasar Ikan Laut_results.pkl
    ├── Pos Angke Hulu_results.pkl
    ├── Pos Cipinang Hulu_results.pkl
    ├── Pos Depok_results.pkl
    ├── Pos Krukut Hulu_results.pkl
    ├── Pos Pesanggrahan_results.pkl
    ├── Pos Sunter Hulu_results.pkl
    ├── Pulo Gadung_results.pkl
    └── Waduk Pluit_results.pkl
```

---

## 🚀 Cara Menjalankan

### 1. Install dependensi
```bash
pip install -r requirements.txt
```

### 2. Siapkan file PKL
Pastikan folder `models/` berisi 12 file `.pkl`.  
Kalau belum punya file PKL asli, jalankan script dummy dulu:
```bash
python generate_dummy_pkl.py
```

### 3. Jalankan aplikasi
```bash
streamlit run app.py
```

---

## 📦 Format File PKL yang Didukung

Setiap file `.pkl` harus berisi **dictionary** dengan kunci nama model:

```python
{
    "SVR": {
        "dates":    <array tanggal>,
        "actual":   <array float — nilai aktual TMA>,
        "pred_h1":  <array float — prediksi H+1>,
        "pred_h2":  <array float — prediksi H+2>,
        "pred_h3":  <array float — prediksi H+3>,
    },
    "Quantile Regression": { ... },
    "Generalized Additive Models": { ... },
}
```

### Nama kunci alternatif yang juga dikenali:
| Data | Kunci yang diterima |
|------|---------------------|
| Tanggal | `dates`, `date`, `Date`, `index` |
| Aktual | `actual`, `y_actual`, `y_true`, `target`, `Actual` |
| Prediksi H+1 | `pred_h1`, `pred_1`, `h1`, `horizon_1`, `y_pred_1`, `forecast_1` |
| Prediksi H+2 | `pred_h2`, `pred_2`, `h2`, `horizon_2`, `y_pred_2`, `forecast_2` |
| Prediksi H+3 | `pred_h3`, `pred_3`, `h3`, `horizon_3`, `y_pred_3`, `forecast_3` |

---

## 🖥️ Fitur Aplikasi

| Fitur | Keterangan |
|-------|------------|
| Pemilihan Pos | 12 pos pintu air Jakarta |
| Pemilihan Model | SVR, Quantile Regression, GAM |
| Pemilihan Tanggal | Kalender interaktif (13 Jan 2022–2025) |
| Prediksi H+1,+2,+3 | Nilai prediksi + status siaga |
| Evaluasi | MAE, RMSE, MAPE, R² per horizon |
| Plot Keseluruhan | Prediksi vs aktual seluruh periode |
| Plot 3 Hari | Context 7 hari + prediksi ke depan |
| Grafik Siaga | Gauge + bar chart batas siaga |

---

## 🚨 Batas Siaga

| Pos | Siaga 3 | Siaga 2 | Siaga 1 |
|-----|---------|---------|---------|
| Bendung Katulampa | 80 cm | 150 cm | 200 cm |
| Pos Depok | 200 cm | 270 cm | 350 cm |
| Manggarai BKB | 750 cm | 850 cm | 950 cm |
| PA Karet | 450 cm | 550 cm | 600 cm |
| Pos Krukut Hulu | 150 cm | 250 cm | 300 cm |
| Pos Pesanggrahan | 150 cm | 250 cm | 350 cm |
| Pos Angke Hulu | 150 cm | 250 cm | 300 cm |
| Waduk Pluit | -51 cm | 0 cm | 45 cm |
| Pasar Ikan Laut | 170 cm | 200 cm | 250 cm |
| Pos Cipinang Hulu | 150 cm | 200 cm | 250 cm |
| Pos Sunter Hulu | 140 cm | 200 cm | 250 cm |
| Pulo Gadung | 550 cm | 700 cm | 770 cm |
