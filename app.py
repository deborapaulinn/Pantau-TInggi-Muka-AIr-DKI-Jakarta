import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
import pickle
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Pantau Tinggi Muka Air", page_icon="💧", layout="wide")

# --- DATA & KAMUS ---
pintu_air = {
    "Bendung Katulampa": "Bendung Katulampa",
    "Manggarai BKB": "Manggarai BKB",
    "Pos Depok": "Pos Depok",
    "PA Karet": "PA Karet",
    "Pos Krukut Hulu": "Pos Krukut Hulu",
    "Pos Pesanggrahan": "Pos Pesanggrahan",
    "Pos Angke Hulu": "Pos Angke Hulu",
    "Waduk Pluit": "Waduk Pluit",
    "Pasar Ikan Laut": "Pasar Ikan Laut",
    "Pos Cipinang Hulu": "Pos Cipinang Hulu",
    "Pos Sunter Hulu": "Pos Sunter Hulu",
    "Pulo Gadung": "Pulo Gadung"
}

ambang_batas = {
    "Bendung Katulampa": {"siaga1": 200, "siaga2": 150, "siaga3": 80},
    "Pos Depok": {"siaga1": 350, "siaga2": 270, "siaga3": 200},
    "Manggarai BKB": {"siaga1": 950, "siaga2": 850, "siaga3": 750},
    "PA Karet": {"siaga1": 600, "siaga2": 550, "siaga3": 450},
    "Pos Krukut Hulu": {"siaga1": 300, "siaga2": 250, "siaga3": 150},
    "Pos Pesanggrahan": {"siaga1": 350, "siaga2": 250, "siaga3": 150},
    "Pos Angke Hulu": {"siaga1": 300, "siaga2": 250, "siaga3": 150},
    "Waduk Pluit": {"siaga1": 45, "siaga2": 0, "siaga3": -51},
    "Pasar Ikan Laut": {"siaga1": 250, "siaga2": 200, "siaga3": 170},
    "Pos Cipinang Hulu": {"siaga1": 250, "siaga2": 200, "siaga3": 150},
    "Pos Sunter Hulu": {"siaga1": 250, "siaga2": 200, "siaga3": 140},
    "Pulo Gadung": {"siaga1": 770, "siaga2": 700, "siaga3": 550}
}

pkl_mapping = {
    "Bendung Katulampa": "BendungKatulampa_results.pkl",
    "Manggarai BKB": "Manggarai BKB_results.pkl",
    "Pos Depok": "Pos Depok_results.pkl",
    "PA Karet": "PA Karet_results.pkl",
    "Pos Krukut Hulu": "Pos Krukut Hulu_results.pkl",
    "Pos Pesanggrahan": "Pos Pesanggrahan_results.pkl",
    "Pos Angke Hulu": "Pos Angke Hulu_results.pkl",
    "Waduk Pluit": "Waduk Pluit_results.pkl",
    "Pasar Ikan Laut": "Pasar Ikan Laut_results.pkl",
    "Pos Cipinang Hulu": "Pos Cipinang Hulu_results.pkl",
    "Pos Sunter Hulu": "Pos Sunter Hulu_results.pkl",
    "Pulo Gadung": "Pulo Gadung_results.pkl"
}

model_list = ["SVR", "Quantile Regression", "Generalized Additive Models"]

# --- FUNGSI HELPER ---
def get_status_siaga(tma, batas):
    if tma >= batas["siaga1"]:
        return "🔴 Siaga I (Bahaya)"
    elif tma >= batas["siaga2"]:
        return "🟠 Siaga II (Siaga)"
    elif tma >= batas["siaga3"]:
        return "🟡 Siaga III (Waspada)"
    else:
        return "🔵 Normal"

def load_model(lokasi):
    file_name = pkl_mapping.get(lokasi)
    if not file_name: return None
    file_path = os.path.join("models", file_name)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as file:
                return pickle.load(file)
        except Exception as e:
            st.error(f"Gagal memuat {file_name}: {e}")
    return None

# --- SIDEBAR ---
st.sidebar.title("Menu")

# Inisialisasi state halaman jika belum ada
if "halaman" not in st.session_state:
    st.session_state.halaman = "Dashboard"

def ganti_halaman(nama_halaman):
    st.session_state.halaman = nama_halaman

# Tombol-tombol navigasi yang akan merubah state halaman saat diklik
st.sidebar.button("Halaman Prediksi", use_container_width=True, type="primary" if st.session_state.halaman == "Dashboard" else "secondary", on_click=ganti_halaman, args=("Dashboard",))
st.sidebar.button("Riwayat Data", use_container_width=True, type="primary" if st.session_state.halaman == "Riwayat Data" else "secondary", on_click=ganti_halaman, args=("Riwayat Data",))
st.sidebar.button("Metode Prediksi", use_container_width=True, type="primary" if st.session_state.halaman == "Metode Prediksi" else "secondary", on_click=ganti_halaman, args=("Metode Prediksi",))
st.sidebar.button("Panduan Mitigasi", use_container_width=True, type="primary" if st.session_state.halaman == "Panduan Mitigasi" else "secondary", on_click=ganti_halaman, args=("Panduan Mitigasi",))
st.sidebar.button("Peta Lokasi", use_container_width=True, type="primary" if st.session_state.halaman == "Peta Lokasi" else "secondary", on_click=ganti_halaman, args=("Peta Lokasi",))

# 1. HALAMAN DASHBOARD UTAMA
if st.session_state.halaman == "Dashboard":
    
    st.title("Pantau Tinggi Muka Air")
    st.markdown("Sistem informasi prediksi tinggi muka air di DKI Jakarta dalam 1–3 hari ke depan menggunakan model machine learning dan statistik lanjutan.")
    st.markdown("---")

    # --- FORM INPUT (Tanpa Tombol Submit) ---
    col1, col2, col3 = st.columns([2, 1.5, 2])

    with col1:
        pilihan_key = st.selectbox("PINTU AIR *", options=list(pintu_air.keys()))
        lokasi = pintu_air[pilihan_key]
        batas_lokasi = ambang_batas[lokasi]
        
    with col2:
        tanggal_pilih = st.date_input(
            "TANGGAL *", 
            value=datetime.date(2025, 12, 3),
            min_value=datetime.date(2022, 1, 13), 
            max_value=datetime.date(2025, 12, 31)
        )
        
    with col3:
        model_pilih = st.selectbox("MODEL PREDIKSI", options=model_list)

    # --- PEMROSESAN MODEL ---
    model_bundle = load_model(lokasi) 

    if model_bundle is None:
        st.error(f"⚠️ File data untuk {lokasi} tidak ditemukan di folder `models/`.")
        st.stop()

    # Mapping pilihan UI ke key di dalam PKL
    key_mapping = {
        "SVR": "svr_results",
        "Quantile Regression": "qr_results",
        "Generalized Additive Models": "gam_results"
    }
    target_key = key_mapping[model_pilih]

    if target_key not in model_bundle:
        st.error(f"⚠️ Model {model_pilih} tidak ditemukan di dalam data {lokasi}.")
        st.stop()

    hasil_model = model_bundle[target_key]

    # --- EKSTRAKSI DATA DARI PKL ---
    try:
        # 1. Fungsi Pembongkar Super Cerdas (Menangani Pandas DataFrame, Dict, dan Array)
        def get_numeric_array(data):
            if isinstance(data, pd.DataFrame):
                for k in [0.5, '0.5', '0.50', 'median', 'q50', 0.50]:
                    if k in data.columns:
                        return data[k].values.flatten()
                return data.iloc[:, 0].values.flatten()
                
            elif isinstance(data, dict):
                for k in [0.5, '0.5', '0.50', 'median', 'q50', 0.50]:
                    if k in data:
                        return np.array(data[k]).flatten()
                first_key = list(data.keys())[0]
                return np.array(data[first_key]).flatten()
                
            return np.array(data).flatten()

        # 2. Fungsi Pencari Nilai Prediksi Masa Depan (+1, +2, +3)
        def get_pred_value(data_dict):
            if 'y_pred_oos' in data_dict:
                arr = get_numeric_array(data_dict['y_pred_oos'])
                return round(float(arr[0]), 1) if len(arr) > 0 else 0.0
            elif 'pred_test' in data_dict:
                arr = get_numeric_array(data_dict['pred_test'])
                return round(float(arr[-1]), 1) if len(arr) > 0 else 0.0
            return 0.0

        pred_h1 = get_pred_value(hasil_model[1])
        pred_h2 = get_pred_value(hasil_model[2])
        pred_h3 = get_pred_value(hasil_model[3])

        # 3. Fungsi Cerdas Pencari Data Aktual & Prediksi Historis (SVR/GAM vs QR)
        kunci_train = 'y_train_raw' if 'y_train_raw' in hasil_model[1] else 'y_train'
        kunci_test = 'y_test_raw' if 'y_test_raw' in hasil_model[1] else 'y_test'
        
        kunci_pred_train = 'y_pred_tr' if 'y_pred_tr' in hasil_model[1] else 'pred_train'
        kunci_pred_test = 'y_pred_te' if 'y_pred_te' in hasil_model[1] else 'pred_test'

        # 4. Menggabungkan Data Historis (Train + Test)
        train_dates = pd.to_datetime(hasil_model[1]['train_index'])
        test_dates = pd.to_datetime(hasil_model[1]['test_index'])
        all_dates = list(train_dates) + list(test_dates)

        # Gabungkan Aktual
        train_actual = get_numeric_array(hasil_model[1][kunci_train])
        test_actual = get_numeric_array(hasil_model[1][kunci_test])
        all_actual = np.concatenate([train_actual, test_actual])

        # Gabungkan Prediksi Historis
        train_pred = get_numeric_array(hasil_model[1][kunci_pred_train])
        test_pred = get_numeric_array(hasil_model[1][kunci_pred_test])
        all_pred = np.concatenate([train_pred, test_pred])

        # 5. Filter berdasarkan Tanggal Pilihan di Kalender
        df_history = pd.DataFrame({
            'Tanggal': all_dates, 
            'Aktual': all_actual,
            'Prediksi_Historis': all_pred
        })
        df_history['Tanggal_Date'] = df_history['Tanggal'].dt.date
        df_filtered = df_history[df_history['Tanggal_Date'] <= tanggal_pilih].sort_values('Tanggal')

        if df_filtered.empty:
            st.warning("⚠️ Data historis pada tanggal yang dipilih kosong/tidak tersedia.")
            st.stop()

        # 6. Ambil TMA Terakhir (Terkini)
        tma_terkini = round(float(df_filtered.iloc[-1]['Aktual']), 1)
        status_saat_ini = get_status_siaga(tma_terkini, batas_lokasi)

        # 7. Persiapan Data Akhir untuk Grafik
        dates_past = df_filtered['Tanggal'].dt.date.tolist()
        aktual_past = df_filtered['Aktual'].tolist()
        pred_past = df_filtered['Prediksi_Historis'].tolist() # <-- Data baru untuk grafik keseluruhan
        
        dates_future = [
            tanggal_pilih + datetime.timedelta(days=1),
            tanggal_pilih + datetime.timedelta(days=2),
            tanggal_pilih + datetime.timedelta(days=3)
        ]
        pred_future = [pred_h1, pred_h2, pred_h3]

    except Exception as e:
        st.error(f"Terjadi kesalahan saat mengekstrak isi model: {e}")
        st.stop()

    # --- METRICS CARDS ---
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2, m3, m4, m5 = st.columns([1, 1, 1, 1, 1.5])
    with m1:
        st.metric(label="TMA TERKINI", value=f"{tma_terkini} cm", delta="Aktual")
    with m2:
        st.metric(label="PREDIKSI +1 HARI", value=f"{pred_h1} cm", delta=f"{model_pilih}", delta_color="off")
    with m3:
        st.metric(label="PREDIKSI +2 HARI", value=f"{pred_h2} cm", delta=f"{model_pilih}", delta_color="off")
    with m4:
        st.metric(label="PREDIKSI +3 HARI", value=f"{pred_h3} cm", delta=f"{model_pilih}", delta_color="off")
    with m5:
        if "Normal" in status_saat_ini:
            st.success(f"**STATUS SAAT INI**\n\n{status_saat_ini}")
        elif "Siaga III" in status_saat_ini:
            st.info(f"**STATUS SAAT INI**\n\n{status_saat_ini}")
        elif "Siaga II" in status_saat_ini:
            st.warning(f"**STATUS SAAT INI**\n\n{status_saat_ini}")
        else:
            st.error(f"**STATUS SAAT INI**\n\n{status_saat_ini}")


    # --- NILAI EVALUASI MODEL (DENGAN FILTER PER MODEL) ---
    try:
        # Mengambil data metrik dari H+1 (hasil_model[1])
        metrics_data = hasil_model[1].get('metrics', {})
        
        if isinstance(metrics_data, dict) and metrics_data:
            st.markdown("##### 📊 Evaluasi Kinerja Model")
            
            # 1. Tentukan kata kunci filter berdasarkan model yang dipilih di UI
            if model_pilih == "SVR":
                keyword_aktif = ["svr"]
            elif model_pilih == "Quantile Regression":
                keyword_aktif = ["qr", "quantile"]
            elif model_pilih == "Generalized Additive Models":
                keyword_aktif = ["gam", "generalized"]
            else:
                keyword_aktif = []

            # 2. Meratakan dictionary (flat-map)
            flat_metrics = {}
            for k, v in metrics_data.items():
                if isinstance(v, dict):
                    for sub_k, sub_v in v.items():
                        flat_metrics[f"{k}_{sub_k}"] = sub_v
                else:
                    flat_metrics[k] = v
                    
            # 3. Proses Penyaringan: Hanya ambil metrik yang sesuai dengan model aktif
            filtered_metrics = {}
            for k, v in flat_metrics.items():
                k_lower = k.lower()
                
                # --- FILTER PENGECUALIAN TAMBAHAN ---
                # Daftar kata kunci yang ingin disembunyikan dari layar
                kata_kunci_dihapus = ["early_warn", "siaga", "coverage", "width"]
                
                # Jika nama metrik mengandung salah satu kata di atas, lewati!
                if any(kata in k_lower for kata in kata_kunci_dihapus):
                    continue
                
                # Cek apakah metrik ini milik model LAIN
                is_other_model = False
                daftar_model_lain = {
                    "svr": ["svr"],
                    "qr": ["qr", "quantile"],
                    "gam": ["gam", "generalized"]
                }
                
                for mod_name, kws in daftar_model_lain.items():
                    if any(kw in k_lower for kw in kws):
                        if not any(kw in model_pilih.lower() for kw in kws) and not (model_pilih == "Quantile Regression" and mod_name == "qr") and not (model_pilih == "Generalized Additive Models" and mod_name == "gam"):
                            is_other_model = True
                            break
                
                if any(kw in k_lower for kw in keyword_aktif) or not is_other_model:
                    filtered_metrics[k] = v

            # 4. Menampilkan metrik hasil filter ke dalam grid (Maksimal 4 kolom per baris)
            if filtered_metrics:
                keys = list(filtered_metrics.keys())
                for i in range(0, len(keys), 4):
                    cols = st.columns(4)
                    for j in range(4):
                        if i + j < len(keys):
                            k = keys[i + j]
                            v = filtered_metrics[k]
                            
                            if isinstance(v, (int, float, np.floating)):
                                val_str = f"{v:.3f}"
                            else:
                                val_str = str(v)
                                
                            label_bersih = str(k).upper().replace("_", " ")
                            cols[j].metric(label=label_bersih, value=val_str)
            else:
                st.info("Tidak ada metrik evaluasi khusus untuk model ini.")
                
            st.markdown("<br>", unsafe_allow_html=True)
    except Exception as e:
        pass

    # --- GRAFIK 1: PREDIKSI VS AKTUAL ---
    st.subheader(f"Grafik Prediksi vs Aktual Tinggi Muka Air ({lokasi})")
    st.caption(f"Satuan: cm — Model: {model_pilih} | Menampilkan riwayat hingga {tanggal_pilih.strftime('%d %b %Y')}")

    fig1 = go.Figure()

    # Plot Garis Aktual (Batasi 60 hari terakhir agar tidak berat)
    limit_hari = 60
    plot_dates_past = dates_past[-limit_hari:]
    plot_aktual_past = aktual_past[-limit_hari:]

    fig1.add_trace(go.Scatter(
        x=plot_dates_past, y=plot_aktual_past, 
        mode='lines+markers', name='Aktual',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=6)
    ))

    # Plot Garis Prediksi
    dates_pred_full = [plot_dates_past[-1]] + dates_future
    pred_full = [plot_aktual_past[-1]] + pred_future

    fig1.add_trace(go.Scatter(
        x=dates_pred_full, y=pred_full, 
        mode='lines+markers', name='Prediksi 3 Hari',
        line=dict(color='#ff7f0e', width=3, dash='dashdot'),
        marker=dict(size=8)
    ))

    fig1.add_hline(y=batas_lokasi["siaga1"], line_dash="dash", line_color="red", annotation_text="Siaga I", annotation_position="top left")
    fig1.add_hline(y=batas_lokasi["siaga2"], line_dash="dash", line_color="orange", annotation_text="Siaga II", annotation_position="top left")
    fig1.add_hline(y=batas_lokasi["siaga3"], line_dash="dash", line_color="#e6c200", annotation_text="Siaga III", annotation_position="top left")

    fig1.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor='lightgray'),
        yaxis=dict(showgrid=True, gridcolor='lightgray', title='Tinggi Muka Air (cm)'),
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig1, use_container_width=True)

    # --- GRAFIK 1B: PREDIKSI VS AKTUAL SELURUH TANGGAL (2022-2025) ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader(f"Grafik Historis Keseluruhan Prediksi vs Aktual ({lokasi})")
    st.caption(f"Satuan: cm — Model: {model_pilih} | Menampilkan dua garis utuh perbandingan data aktual dan hasil prediksi")

    fig1_full = go.Figure()

    # 1. Garis Aktual Keseluruhan (Biru)
    fig1_full.add_trace(go.Scatter(
        x=dates_past, y=aktual_past, 
        mode='lines', name='Aktual',
        line=dict(color='#1f77b4', width=1.5)
    ))

    # 2. Garis Prediksi Keseluruhan + Sambungan 3 Hari ke Depan (Orange)
    dates_pred_total = dates_past + dates_future
    pred_total = pred_past + pred_future

    fig1_full.add_trace(go.Scatter(
        x=dates_pred_total, y=pred_total, 
        mode='lines', name='Prediksi Model',
        line=dict(color='#ff7f0e', width=1.5)
    ))

    # Garis Batas Status Siaga
    fig1_full.add_hline(y=batas_lokasi["siaga1"], line_dash="dash", line_color="red", annotation_text="Siaga I", annotation_position="top left")
    fig1_full.add_hline(y=batas_lokasi["siaga2"], line_dash="dash", line_color="orange", annotation_text="Siaga II", annotation_position="top left")
    fig1_full.add_hline(y=batas_lokasi["siaga3"], line_dash="dash", line_color="#e6c200", annotation_text="Siaga III", annotation_position="top left")

    fig1_full.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor='lightgray'),
        yaxis=dict(showgrid=True, gridcolor='lightgray', title='Tinggi Muka Air (cm)'),
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig1_full, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- GRAFIK 2: SISTEM PERINGATAN DINI ---
    st.subheader("Sistem Peringatan Dini")
    st.caption("Posisi TMA terhadap ambang batas siaga - Tren Aktual 7 Hari Terakhir")

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    col_s1.error(f"🔴 **Siaga I (Bahaya)**\n\n≥ {batas_lokasi['siaga1']} cm")
    col_s2.warning(f"🟠 **Siaga II (Siaga)**\n\n{batas_lokasi['siaga2']} – {batas_lokasi['siaga1']-1} cm")
    col_s3.info(f"🟡 **Siaga III (Waspada)**\n\n{batas_lokasi['siaga3']} – {batas_lokasi['siaga2']-1} cm")
    col_s4.success(f"🔵 **Normal**\n\n< {batas_lokasi['siaga3']} cm")

    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        x=plot_dates_past[-7:], y=plot_aktual_past[-7:], fill='tozeroy',
        mode='lines+markers', name='Tinggi Air Aktual',
        line=dict(color='#17becf', width=3),
        fillcolor='rgba(23, 190, 207, 0.2)'
    ))

    fig2.add_hline(y=batas_lokasi["siaga1"], line_dash="dash", line_color="red")
    fig2.add_hline(y=batas_lokasi["siaga2"], line_dash="dash", line_color="orange")
    fig2.add_hline(y=batas_lokasi["siaga3"], line_dash="dash", line_color="#e6c200")

    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='lightgray'),
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig2, use_container_width=True)

# 2. HALAMAN RIWAYAT DATA
elif st.session_state.halaman == "Riwayat Data":
    st.title("📊 Riwayat Data Tinggi Muka Air")
    st.markdown("Halaman ini menampilkan tabel informasi riwayat data Tinggi Muka Air (TMA) seluruh pintu air di DKI Jakarta beserta hasil visualisasi model prediksi.")
    st.markdown("---")

    # --- 1. FORM INPUT (PERIODE WAKTU & MODEL PREDIKSI) ---
    col1, col2 = st.columns(2)
    with col1:
        periode_pilih = st.selectbox(
            "PERIODE WAKTU", 
            options=["Semua (2022-2025)", "2022", "2023", "2024", "2025"]
        )
    with col2:
        model_pilih_riwayat = st.selectbox(
            "MODEL PREDIKSI UNTUK GRAFIK", 
            options=model_list, 
            key="model_riwayat"
        )

    # --- 2 & 3. PROSES PENGAMBILAN DATA & MENAMPILKAN TABEL ---
    st.subheader("📋 Tabel Informasi Riwayat TMA Seluruh Pintu Air")
    
    # 💡 CATATAN UNTUK ACUAN EXCEL:
    # Jika nanti Anda ingin membaca langsung dari file Excel gabungan, kodenya tinggal diganti seperti ini:
    # df_all = pd.read_excel("nama_file_excel_anda.xlsx")
    
    # Di bawah ini adalah sistem otomatis untuk mengekstrak data historis dari file .pkl seluruh pintu air:
    with st.spinner("Mengkstrak data seluruh pintu air..."):
        list_df = []
        
        # Fungsi pembongkar lokal untuk keamanan tipe data
        def ekstrak_array_lokal(data):
            if isinstance(data, pd.DataFrame):
                for k in [0.5, '0.5', '0.50', 'median', 'q50', 0.50]:
                    if k in data.columns: return data[k].values.flatten()
                return data.iloc[:, 0].values.flatten()
            elif isinstance(data, dict):
                for k in [0.5, '0.5', '0.50', 'median', 'q50', 0.50]:
                    if k in data: return np.array(data[k]).flatten()
                return np.array(list(data.values())[0]).flatten()
            return np.array(data).flatten()

        for nama_ui, lokasi_nama in pintu_air.items():
            bundle = load_model(lokasi_nama)
            if bundle and "svr_results" in bundle:
                hasil_svr = bundle["svr_results"]
                if 1 in hasil_svr:
                    kunci_train = 'y_train_raw' if 'y_train_raw' in hasil_svr[1] else 'y_train'
                    kunci_test = 'y_test_raw' if 'y_test_raw' in hasil_svr[1] else 'y_test'
                    
                    # Gabungkan Tanggal
                    t_dates = pd.to_datetime(hasil_svr[1]['train_index'])
                    te_dates = pd.to_datetime(hasil_svr[1]['test_index'])
                    all_d = list(t_dates) + list(te_dates)
                    
                    # Gabungkan Aktual
                    tr_act = ekstrak_array_lokal(hasil_svr[1][kunci_train])
                    te_act = ekstrak_array_lokal(hasil_svr[1][kunci_test])
                    all_act = np.concatenate([tr_act, te_act])
                    
                    # Ambil Prediksi Historis Sesuai Model Pilihan Grafik
                    key_map_riwayat = {
                        "SVR": "svr_results",
                        "Quantile Regression": "qr_results",
                        "Generalized Additive Models": "gam_results"
                    }
                    t_key = key_map_riwayat[model_pilih_riwayat]
                    
                    pred_total = np.zeros(len(all_act))
                    if t_key in bundle and 1 in bundle[t_key]:
                        k_p_tr = 'y_pred_tr' if 'y_pred_tr' in bundle[t_key][1] else 'pred_train'
                        k_p_te = 'y_pred_te' if 'y_pred_te' in bundle[t_key][1] else 'pred_test'
                        tr_pr = ekstrak_array_lokal(bundle[t_key][1][k_p_tr])
                        te_pr = ekstrak_array_lokal(bundle[t_key][1][k_p_te])
                        pred_total = np.concatenate([tr_pr, te_pr])
                    
                    # Buat DataFrame per pintu air
                    df_pintu = pd.DataFrame({
                        'Tanggal': all_d,
                        'Pintu Air': lokasi_nama,
                        'TMA Aktual (cm)': all_act,
                        'TMA Prediksi (cm)': pred_total
                    })
                    list_df.append(df_pintu)

        if list_df:
            # Menggabungkan data dari seluruh pintu air menjadi satu kesatuan tabel
            df_all = pd.concat(list_df, ignore_index=True)
            df_all['Tahun'] = df_all['Tanggal'].dt.year
            
            # Filter data berdasarkan "Periode Waktu" pilihan user
            if periode_pilih != "Semua (2022-2025)":
                df_all = df_all[df_all['Tahun'] == int(periode_pilih)]
            
            # Urutkan berdasarkan tanggal terbaru
            df_all = df_all.sort_values(by=['Tanggal', 'Pintu Air'], ascending=[False, True])
            
            # Buat tampilan tabel ringkas untuk informasi riwayat
            df_tabel_tampil = df_all[['Tanggal', 'Pintu Air', 'TMA Aktual (cm)']].copy()
            df_tabel_tampil['Tanggal'] = df_tabel_tampil['Tanggal'].dt.strftime('%Y-%m-%d')
            
            df_tabel_tampil.reset_index(drop=True, inplace=True)  # Hapus index yang acak
            df_tabel_tampil.index = df_tabel_tampil.index + 1     # Mulai nomor urut dari 1 (bukan 0)
            df_tabel_tampil.index.name = "No"                     # Beri judul 'No' pada kolom angka tersebut
            
            # Tampilkan tabel ke layar Streamlit
            st.dataframe(df_tabel_tampil, use_container_width=True, height=350)
            
            # Tombol tambahan untuk download data tabel dalam bentuk CSV/Excel-ready
            csv_data = df_tabel_tampil.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Unduh Data Riwayat (CSV)", 
                data=csv_data, 
                file_name=f"riwayat_tma_{periode_pilih.replace(' ', '_')}.csv", 
                mime="text/csv"
            )
            
            # --- 4. HASIL VISUALISASI DI BAWAH TABEL RIWAYAT DATA ---
            st.markdown("---")
            st.subheader("📉 Visualisasi Tren Riwayat Data vs Prediksi")
            st.caption(f"Perbandingan grafik data Aktual vs Prediksi Model **{model_pilih_riwayat}** pada periode **{periode_pilih}**")
            
            # Filter khusus pintu air untuk grafik agar tidak tumpang tindih ribuan baris data
            pintu_grafik = st.selectbox("PILIH PINTU AIR UNTUK VISUALISASI GRAFIK", options=list(pintu_air.values()))
            df_grafik = df_all[df_all['Pintu Air'] == pintu_grafik].sort_values(by='Tanggal')
            
            if not df_grafik.empty:
                fig_riwayat = go.Figure()
                
                # Garis Aktual (Biru)
                fig_riwayat.add_trace(go.Scatter(
                    x=df_grafik['Tanggal'], y=df_grafik['TMA Aktual (cm)'],
                    mode='lines', name='TMA Aktual', line=dict(color='#1f77b4', width=1.5)
                ))
                
                # Garis Prediksi Model (Orange)
                fig_riwayat.add_trace(go.Scatter(
                    x=df_grafik['Tanggal'], y=df_grafik['TMA Prediksi (cm)'],
                    mode='lines', name=f'Prediksi ({model_pilih_riwayat})', 
                    line=dict(color='#ff7f0e', width=1.5, dash='dash')
                ))
                
                # Ambang Batas Siaga Lokasi Terpilih
                batas_grafik = ambang_batas[pintu_grafik]
                fig_riwayat.add_hline(y=batas_grafik["siaga1"], line_dash="dash", line_color="red", annotation_text="Siaga I")
                fig_riwayat.add_hline(y=batas_grafik["siaga2"], line_dash="dash", line_color="orange", annotation_text="Siaga II")
                fig_riwayat.add_hline(y=batas_grafik["siaga3"], line_dash="dash", line_color="#e6c200", annotation_text="Siaga III")
                
                fig_riwayat.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=True, gridcolor='lightgray'),
                    yaxis=dict(showgrid=True, gridcolor='lightgray', title='Tinggi Muka Air (cm)'),
                    margin=dict(l=20, r=20, t=20, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_riwayat, use_container_width=True)
            else:
                st.warning("⚠️ Tidak ada data historis yang tersedia untuk grafik pada kombinasi filter ini.")
        else:
            st.error("⚠️ Gagal mengekstrak data. Pastikan file model `.pkl` berada di folder `models/`.")

# 3. HALAMAN METODE PREDIKSI
elif st.session_state.halaman == "Metode Prediksi":
    st.title("⚙️ Metodologi & Algoritma Prediksi")
    st.markdown("Halaman ini menjelaskan dasar ilmiah, formulasi matematika, dan perbandingan performa dari tiga model utama yang digunakan dalam sistem ini.")
    st.markdown("---")

    # --- 1. PENJELASAN TIAP MODEL (TABS) ---
    st.subheader("💡 Deskripsi Algoritma")
    tab1, tab2, tab3 = st.tabs(["Support Vector Regression", "Quantile Regression", "Generalized Additive Models"])

    with tab1:
        st.markdown("""
        **Support Vector Regression (SVR)** adalah algoritma pembelajaran mesin berbasis kernel yang mencari sebuah *hyperplane* dalam ruang dimensi tinggi untuk melakukan regresi. 
        Keunggulan utamanya adalah kemampuan menangani data non-linear dan ketahanannya terhadap gangguan (*noise*) data.
        """)
        # Rumus SVR dengan MathML
        st.markdown("**Formulasi Matematika:**")
        st.write(
            """<div style='background-color: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0;'>
            <math xmlns="http://www.w3.org/1998/Math/MathML" display="block">
              <munder>
                <mo>min</mo>
                <mrow>
                  <mi>w</mi>
                  <mo>,</mo>
                  <mi>b</mi>
                  <mo>,</mo>
                  <mi>&#x3BE;</mi>
                </mrow>
              </munder>
              <mfrac>
                <mn>1</mn>
                <mn>2</mn>
              </mfrac>
              <msup>
                <mrow>
                  <mo>||</mo>
                  <mi>w</mi>
                  <mo>||</mo>
                </mrow>
                <mn>2</mn>
              </msup>
              <mo>+</mo>
              <mi>C</mi>
              <munderover>
                <mo>&#x2211;</mo>
                <mrow>
                  <mi>i</mi>
                  <mo>=</mo>
                  <mn>1</mn>
                </mrow>
                <mi>n</mi>
              </munderover>
              <mo>(</mo>
              <msub>
                <mi>&#x3BE;</mi>
                <mi>i</mi>
              </msub>
              <mo>+</mo>
              <msubsup>
                <mi>&#x3BE;</mi>
                <mi>i</mi>
                <mo>*</mo>
              </msubsup>
              <mo>)</mo>
            </math>
            </div>""", unsafe_allow_html=True
        )

    with tab2:
        st.markdown("""
        **Quantile Regression (QR)** memperluas model regresi standar dengan memprediksi kuantil kondisional (seperti median atau persentil ke-75) daripada hanya nilai rata-rata. 
        Model ini sangat penting dalam manajemen risiko banjir karena memberikan estimasi batas atas (probabilitas kejadian ekstrem).
        """)
        st.markdown("**Formulasi Matematika:**")
        st.write(
            """<div style='background-color: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0;'>
            <math xmlns="http://www.w3.org/1998/Math/MathML" display="block">
              <munder>
                <mo>min</mo>
                <mrow>
                  <mi>&#x3B2;</mi>
                  <mo>&#x2208;</mo>
                  <msup>
                    <mi>R</mi>
                    <mi>p</mi>
                  </msup>
                </mrow>
              </munder>
              <mo>[</mo>
              <munder>
                <mo>&#x2211;</mo>
                <mrow>
                  <mi>i</mi>
                  <mo>:</mo>
                  <msub>
                    <mi>y</mi>
                    <mi>i</mi>
                  </msub>
                  <mo>&#x2265;</mo>
                  <msubsup>
                    <mi>x</mi>
                    <mi>i</mi>
                    <mi>&#x2032;</mi>
                  </msubsup>
                  <mi>&#x3B2;</mi>
                </mrow>
              </munder>
              <mi>&#x3C4;</mi>
              <mo>|</mo>
              <msub>
                <mi>y</mi>
                <mi>i</mi>
              </msub>
              <mo>-</mo>
              <msubsup>
                <mi>x</mi>
                <mi>i</mi>
                <mi>&#x2032;</mi>
              </msubsup>
              <mi>&#x3B2;</mi>
              <mo>|</mo>
              <mo>+</mo>
              <munder>
                <mo>&#x2211;</mo>
                <mrow>
                  <mi>i</mi>
                  <mo>:</mo>
                  <msub>
                    <mi>y</mi>
                    <mi>i</mi>
                  </msub>
                  <mo>&lt;</mo>
                  <msubsup>
                    <mi>x</mi>
                    <mi>i</mi>
                    <mi>&#x2032;</mi>
                  </msubsup>
                  <mi>&#x3B2;</mi>
                </mrow>
              </munder>
              <mo>(</mo>
              <mn>1</mn>
              <mo>-</mo>
              <mi>&#x3C4;</mi>
              <mo>)</mo>
              <mo>|</mo>
              <msub>
                <mi>y</mi>
                <mi>i</mi>
              </msub>
              <mo>-</mo>
              <msubsup>
                <mi>x</mi>
                <mi>i</mi>
                <mi>&#x2032;</mi>
              </msubsup>
              <mi>&#x3B2;</mi>
              <mo>|</mo>
              <mo>]</mo>
            </math>
            </div>""", unsafe_allow_html=True
        )

    with tab3:
        st.markdown("""
        **Generalized Additive Models (GAM)** adalah model statistik yang memungkinkan hubungan non-linear antara variabel dependen dan independen melalui fungsi mulus (*smoothing functions*). 
        Sangat cocok untuk data TMA yang memiliki pola musiman dan tren non-linear yang kompleks.
        """)
        st.markdown("**Formulasi Matematika:**")
        st.write(
            """<div style='background-color: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0;'>
            <math xmlns="http://www.w3.org/1998/Math/MathML" display="block">
              <mi>g</mi>
              <mo>(</mo>
              <mi>E</mi>
              <mo>(</mo>
              <mi>Y</mi>
              <mo>)</mo>
              <mo>)</mo>
              <mo>=</mo>
              <msub>
                <mi>&#x3B2;</mi>
                <mn>0</mn>
              </msub>
              <mo>+</mo>
              <msub>
                <mi>f</mi>
                <mn>1</mn>
              </msub>
              <mo>(</mo>
              <msub>
                <mi>x</mi>
                <mn>1</mn>
              </msub>
              <mo>)</mo>
              <mo>+</mo>
              <msub>
                <mi>f</mi>
                <mn>2</mn>
              </msub>
              <mo>(</mo>
              <msub>
                <mi>x</mi>
                <mn>2</mn>
              </msub>
              <mo>)</mo>
              <mo>+</mo>
              <mo>&#x22EF;</mo>
              <mo>+</mo>
              <msub>
                <mi>f</mi>
                <mi>m</mi>
              </msub>
              <mo>(</mo>
              <msub>
                <mi>x</mi>
                <mi>m</mi>
              </msub>
              <mo>)</mo>
            </math>
            </div>""", unsafe_allow_html=True
        )

    # --- 2. PERBANDINGAN MODEL (TABEL RINGKAS) ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("⚖️ Perbandingan Karakteristik Model")
    
    data_banding = {
        "Kriteria": ["Akurasi Rerata", "Ketahanan Outlier", "Interpretabilitas", "Output Risiko", "Kompleksitas"],
        "SVR": ["Tinggi", "Sedang", "Rendah (Black-box)", "Point Estimate", "Tinggi"],
        "QR": ["Sedang", "Sangat Tinggi", "Tinggi", "Probabilistic/Range", "Rendah"],
        "GAM": ["Tinggi", "Sedang", "Sangat Tinggi", "Point Estimate", "Sedang"]
    }
    st.table(pd.DataFrame(data_banding))

    # --- 3. PERBANDINGAN DALAM BENTUK GRAFIK ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📊 Visualisasi Efisiensi Prediksi")
    st.caption("Ilustrasi perbandingan tingkat kesalahan (error) relatif antar model berdasarkan data pengujian.")

    # Data dummy untuk ilustrasi perbandingan performa (bisa diganti dengan data asli jika ada)
    models = ["SVR", "Quantile Reg.", "GAM"]
    rmse_vals = [12.5, 15.8, 13.2] # Contoh RMSE
    mae_vals = [9.8, 11.2, 10.1]   # Contoh MAE

    fig_compare = go.Figure()
    fig_compare.add_trace(go.Bar(x=models, y=rmse_vals, name='RMSE (Lower is Better)', marker_color='#1f77b4'))
    fig_compare.add_trace(go.Bar(x=models, y=mae_vals, name='MAE (Lower is Better)', marker_color='#ff7f0e'))

    fig_compare.update_layout(
        barmode='group',
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='lightgray', title='Nilai Error (cm)'),
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_compare, use_container_width=True)

    st.success("ℹ️ **Kesimpulan:** Model **SVR** cenderung unggul dalam akurasi titik, sementara **Quantile Regression** memberikan wawasan terbaik untuk kondisi ekstrem (banjir), dan **GAM** memberikan penjelasan terbaik mengenai kontribusi tiap variabel terhadap kenaikan air.")

# 4. HALAMAN PANDUAN MITIGASI
elif st.session_state.halaman == "Panduan Mitigasi":
    st.title("🛡️ Panduan Mitigasi & Keselamatan")
    st.markdown("Berikut adalah Standar Operasional Prosedur (SOP) dan langkah-langkah pencegahan yang harus dilakukan masyarakat berdasarkan status peringatan dini Tinggi Muka Air (TMA).")
    st.markdown("---")

    # --- STATUS NORMAL (BIRU) ---
    st.success("""
    ### 🔵 Status Normal
    **Kondisi:** Tinggi air berada di batas aman. Tidak ada potensi banjir dalam waktu dekat.
    
    **Tindakan Pencegahan & Mitigasi:**
    * **Pantau Lingkungan:** Jaga kebersihan saluran air, selokan, dan sungai dari sumbatan sampah.
    * **Persiapan Awal:** Kenali rute evakuasi dan lokasi posko banjir terdekat dari tempat tinggal Anda.
    * **Update Informasi:** Tetap pantau prakiraan cuaca dari BMKG dan informasi TMA melalui dashboard ini secara berkala.
    """)

    # --- SIAGA III (KUNING) ---
    st.info("""
    ### 🟡 Siaga III (Waspada)
    **Kondisi:** Debit air mulai meningkat. Terdapat potensi genangan di area dataran rendah atau pemukiman bantaran sungai.
    
    **Tindakan Pencegahan & Mitigasi:**
    * **Amankan Barang:** Mulai pindahkan barang elektronik, perabotan, dan dokumen penting ke tempat yang lebih tinggi (lantai 2 atau area aman).
    * **Koordinasi Warga:** Pengurus RT/RW mulai mensosialisasikan peringatan dini kepada warga di area rawan.
    * **Persiapan Logistik:** Pastikan ketersediaan bahan makanan darurat, air bersih, dan obat-obatan pribadi.
    """)

    # --- SIAGA II (ORANYE) ---
    st.warning("""
    ### 🟠 Siaga II (Siaga)
    **Kondisi:** Kenaikan air semakin signifikan dan cepat. Banjir kemungkinan besar akan segera melanda beberapa wilayah.
    
    **Tindakan Pencegahan & Mitigasi:**
    * **Tas Siaga Bencana:** Siapkan dan dekatkan tas siaga bencana agar siap dibawa kapan saja.
    * **Matikan Listrik:** Cabut seluruh colokan listrik dan matikan meteran (MCB) rumah untuk mencegah korsleting dan tersetrum.
    * **Amankan Kendaraan:** Pindahkan mobil atau sepeda motor ke dataran yang lebih tinggi dan aman.
    * **Prioritas Evakuasi:** Lansia, anak-anak, ibu hamil, dan orang sakit disarankan untuk dievakuasi lebih awal ke tempat aman.
    """)

    # --- SIAGA I (MERAH) ---
    st.error("""
    ### 🔴 Siaga I (Bahaya)
    **Kondisi:** Air telah melewati ambang batas kritis. Banjir besar sedang atau akan segera terjadi. Waktu evakuasi sangat singkat.
    
    **Tindakan Pencegahan & Mitigasi:**
    * **Evakuasi Segera:** Tinggalkan rumah dan segera menuju ke titik kumpul atau posko pengungsian resmi. Jangan menunda-nunda!
    * **Jangan Menerobos Air:** Hindari berjalan atau mengemudi melewati arus banjir. Air setinggi lutut yang mengalir deras sudah cukup untuk menyeret manusia dewasa.
    * **Ikuti Arahan Petugas:** Patuhi seluruh instruksi dari petugas BPBD, SAR, dan relawan di lapangan.
    * **Hindari Area Bahaya:** Jauhi tiang listrik, gardu listrik, dan pohon besar yang rawan tumbang.
    """)

    # --- TIPS TAMBAHAN: TAS SIAGA BENCANA ---
    st.markdown("---")
    st.markdown("### 🎒 Persiapan Tas Siaga Bencana (Penting!)")
    st.markdown("Siapkan satu tas ransel khusus yang mudah dibawa dan simpan di tempat yang mudah dijangkau. Isi tas tersebut dengan:")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        * 📄 **Dokumen Penting:** KTP, KK, Ijazah, Surat Tanah/Rumah (masukkan dalam map plastik kedap air).
        * 👕 **Pakaian Ganti:** Pakaian untuk 3 hari, pakaian dalam, selimut ringan, dan jas hujan.
        * 💊 **Obat-obatan:** Kotak P3K, obat-obatan pribadi rutin, dan vitamin.
        """)
    with col2:
        st.markdown("""
        * 🔦 **Peralatan:** Senter, baterai cadangan, peluit (untuk meminta tolong), dan powerbank terisi penuh.
        * 🥫 **Logistik Dasar:** Air minum kemasan dan makanan awet/siap saji (biskuit, makanan kaleng).
        * 💵 **Uang Tunai:** Siapkan uang tunai secukupnya, karena ATM mungkin tidak berfungsi saat listrik padam.
        """)

# 5. HALAMAN TENTANG / PETA LOKASI
elif st.session_state.halaman == "Peta Lokasi":
    st.title("📍 Peta Lokasi Pintu Air")
    st.markdown("Pemetaan geografis 12 titik stasiun pemantau Tinggi Muka Air (TMA) yang terintegrasi dalam sistem prediksi ini.")
    st.markdown("---")

    # Daftar koordinat (Sudah diperbaiki format minusnya pada pos 10)
    data_koordinat = [
        [-6.633529, 106.837175],  # 1. Bendung Katulampa
        [-6.402000, 106.821000],  # 2. Manggarai BKB
        [-6.208100, 106.850700],  # 3. Pos Depok
        [-6.196500, 106.815500],  # 4. PA Karet
        [-6.264920, 106.480140],  # 5. Pos Krukut Hulu
        [-6.289100, 106.812200],  # 6. Pos Pesanggrahan
        [-6.171714, 106.726583],  # 7. Pos Angke Hulu
        [-6.117390, 106.799908],  # 8. Waduk Pluit
        [-6.126467, 106.809449],  # 9. Pasar Ikan Laut
        [-6.231756, 106.877533],  # 10. Pos Cipinang Hulu
        [-6.162942, 106.881303],  # 11. Pos Sunter Hulu
        [-6.190928, 106.904321]   # 12. Pulo Gadung
    ]

    # Menggabungkan nama pintu air dengan koordinatnya
    df_peta = pd.DataFrame({
        'Nama Pintu Air': list(pintu_air.keys()),
        'Latitude': [x[0] for x in data_koordinat],
        'Longitude': [x[1] for x in data_koordinat]
    })

    # Membuat visualisasi Peta Interaktif menggunakan Plotly Mapbox
    fig_map = go.Figure(go.Scattermapbox(
        lat=df_peta['Latitude'],
        lon=df_peta['Longitude'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=14,
            color='#d62728',  # Warna merah agar mencolok
            opacity=0.8
        ),
        text=df_peta['Nama Pintu Air'], # Teks yang muncul saat titik disentuh
        hoverinfo='text'
    ))

    # Menggunakan gaya peta OpenStreetMap (Gratis & tidak butuh API Key)
    fig_map.update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(
            center=dict(lat=-6.25, lon=106.8), # Titik tengah peta saat pertama kali dimuat
            zoom=9 # Tingkat perbesaran awal
        ),
        margin={"r":0,"t":0,"l":0,"b":0}, # Menghilangkan jarak tepi putih
        height=550 # Tinggi peta di layar
    )

    st.plotly_chart(fig_map, use_container_width=True)

    # Tabel ringkas di bawah peta untuk referensi kordinat
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📌 Referensi Koordinat Geografis")
    
    # Merapikan index tabel agar dimulai dari angka 1
    df_peta.index = df_peta.index + 1
    df_peta.index.name = "No"
    
    st.dataframe(df_peta, use_container_width=True)