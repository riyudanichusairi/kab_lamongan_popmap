import streamlit as st
import folium
from streamlit_folium import st_folium
import json
from folium.plugins import Search
import pandas as pd
import branca.colormap as cm

# ==========================================
# 1. KONFIGURASI HALAMAN UTAMA (WIDE MODE)
# ==========================================
st.set_page_config(layout="wide", page_title="Visualisasi Data Kependudukan", page_icon="🌐")

# Mengurangi padding bawaan Streamlit agar layout lebih padat dan clean
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    div[data-testid="stVerticalBlock"] > div:has(div.stDataFrame) { margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA MANAGEMENT (DIPROTEKSI DARI FILE RUSAK/KOSONG)
# ==========================================
try:
    with open("kab_lamongan_popmap.geojson", "r", encoding="utf-8") as f:
        geo_data = json.load(f)
except FileNotFoundError:
    st.error("❌ File 'kab_lamongan_popmap.geojson' tidak ditemukan di repositori GitHub Anda.")
    st.stop()
except json.JSONDecodeError:
    st.error("❌ File 'kab_lamongan_popmap.geojson' terdeteksi kosong atau rusak di GitHub. Harap unggah ulang file GeoJSON asli yang sehat ke repositori Anda.")
    st.stop()

records = []
for fitur in geo_data.get('features', []):
    props = fitur.get('properties', {})
    records.append({
        'Kecamatan': props.get('KEC', 'Tidak Diketahui'),
        'Desa': props.get('KEL_DES', 'Tidak Diketahui'),
        'Jumlah Penduduk': props.get('jumlah_penduduk', 0),
        'Laki-laki': props.get('laki_laki', 0),
        'Perempuan': props.get('perempuan', 0)
    })

# Pengecekan jika ekstraksi fitur GeoJSON kosong
if not records:
    st.warning("⚠️ Tidak ada data objek spasial (features) yang berhasil dibaca dari file GeoJSON.")
    df = pd.DataFrame(columns=['Kecamatan', 'Desa', 'Jumlah Penduduk', 'Laki-laki', 'Perempuan'])
else:
    df = pd.DataFrame(records)

# ==========================================
# 3. HEADER APLIKASI (PERBAIKAN FLEXBOX AGAR TIDAK TERPOTONG)
# ==========================================
st.markdown("""
    <div style="display: flex; align-items: center; gap: 20px; padding: 10px 0; margin-bottom: 10px;">
        <img src="https://wikimedia.org" width="65" style="object-fit: contain;">
        <div style="display: flex; flex-direction: column; justify-content: center;">
            <h2 style="margin: 0; padding: 0; line-height: 1.3; font-family: sans-serif; font-size: 28px; font-weight: bold; color: #1E1E1E;">
                VISUALISASI DATA KEPENDUDUKAN
            </h2>
            <p style="margin: 5px 0 0 0; padding: 0; line-height: 1; color: #666666; font-family: sans-serif; font-size: 14px; letter-spacing: 0.5px;">
                KABUPATEN LAMONGAN - DINAS KEPENDUDUKAN DAN PENCATATAN SIPIL
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 4. PEMBAGIAN KOLOM UTAMA (KIRI: FILTER, KANAN: PETA)
# ==========================================
col_kontrol, col_peta = st.columns()

# --- PANEL KONTROL SEBELAH KIRI ---
with col_kontrol:
    st.markdown("### 🔍 Cari Data Wilayah")
    
    daftar_kecamatan = sorted(df['Kecamatan'].unique()) if not df.empty else []
    
    kecamatan_terpilih = st.selectbox(
        "Kecamatan:",
        options=["-- Semua Kecamatan --"] + daftar_kecamatan,
        key="kecamatan_box"
    )

    if kecamatan_terpilih != "-- Semua Kecamatan --":
        df_kec = df[df['Kecamatan'] == kecamatan_terpilih]
        daftar_desa = sorted(df_kec['Desa'].unique())
    else:
        df_kec = df
        daftar_desa = sorted(df['Desa'].unique()) if not df.empty else []

    desa_terpilih = st.multiselect(
        "Kelurahan/Desa:",
        options=daftar_desa,
        placeholder="- Pilih Desa -",
        key="desa_box"
    )
    
    # Logika sinkronisasi data filter spasial & tabel
    if desa_terpilih:
        df_filter = df[df['Desa'].isin(desa_terpilih)]
        geo_data_filter = geo_data.copy()
        geo_data_filter['features'] = [
            f for f in geo_data.get('features', []) if f.get('properties', {}).get('KEL_DES') in desa_terpilih
        ]
        label_status = "Hasil Seleksi Desa"
    elif kecamatan_terpilih != "-- Semua Kecamatan --":
        df_filter = df_kec
        list_desa_kec = df_kec['Desa'].tolist()
        geo_data_filter = geo_data.copy()
        geo_data_filter['features'] = [
            f for f in geo_data.get('features', []) if f.get('properties', {}).get('KEL_DES') in list_desa_kec
        ]
        label_status = f"Kec. {kecamatan_terpilih}"
    else:
        df_filter = df
        geo_data_filter = geo_data
        label_status = "Total Lamongan"

    st.markdown("---")
    
    # Menu Struktur Layer (Daftar Peta)
    st.markdown("### 📂 Daftar Layer Peta")
    st.checkbox("🔘 Kepadatan Penduduk", value=True)
    st.checkbox("⚪ Fasilitas Pendidikan", value=False)
    st.checkbox("⚪ Fasilitas Kesehatan", value=False)
    
    st.markdown(" ")
    
    # Tombol Aksi data / Download CSV
    csv_data = df_filter.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Unduh Data (CSV)",
        data=csv_data,
        file_name=f"data_penduduk_{label_status.replace(' ', '_')}.csv",
        mime="text/csv",
        use_container_width=True
    )

# --- PANEL PETA SEBELAH KANAN ---
with col_peta:
    # Baris informasi singkat di atas peta
    st.info("ℹ️ Batas wilayah administrasi yang digunakan dalam peta ini bersifat indikatif.")
    
    # Setup Koordinat Awal Peta
    map_center = [-7.14, 112.33]
    map_zoom = 10
    
    m = folium.Map(location=map_center, zoom_start=map_zoom, tiles=None, control_scale=True)
    
    # Menggunakan basemap satelit Google Hybrid
    folium.TileLayer(
        tiles='https://google.com{x}&y={y}&z={z}',
        attr='Google Hybrid',
        name='Google Satelit (Hybrid)'
    ).add_to(m)

    # Skema Legenda Warna Kloroplet
    colormap_peta = cm.StepColormap(
        colors=['#ffffcc', '#7fcdbb', '#41b6c4', '#1d91c0', '#253494', '#081d58'],
        index=[0, 1000, 2000, 3000, 4500, 6000, 10000],
        vmin=0, vmax=10000,
        caption="Jumlah Penduduk per Desa (Jiwa)"
    )

    def ganti_warna(fitur):
        jumlah_pop = fitur.get('properties', {}).get('jumlah_penduduk', 0)
        return {
            'fillColor': colormap_peta(jumlah_pop), 
            'color': '#ff1a1a',  # Outline batas merah tegas sesuai referensi gambar
            'weight': 1.2,           
            'fillOpacity': 0.45       
        }

    # Render layer spasial kloroplet
    if geo_data_filter.get('features'):
        choro_layer = folium.GeoJson(
            geo_data_filter,
            name="Kloroplet Penduduk",
            style_function=ganti_warna,
            control=True,
            highlight_function=lambda x: {'weight': 2.5, 'color': '#ffff00', 'fillOpacity': 0.6}
        ).add_to(m)

        # Otomatis melakukan fit zoom ke batas wilayah terfilter
        if kecamatan_terpilih != "-- Semua Kecamatan --" or desa_terpilih:
            bounds = choro_layer.get_bounds()
            m.fit_bounds(bounds) 

        # Fitur pencarian teks langsung di dalam peta
        peta_search = Search(
            layer=choro_layer, geom_type="Polygon", placeholder="Cari desa...",
            collapsed=True, position="topright", search_label="KEL_DES", search_zoom=14
        ).add_to(m)

        # Fitur Popup Demografi Interaktif saat poligon diklik
        folium.features.GeoJsonPopup(
            fields=["KEC", "KEL_DES", "jumlah_penduduk", "laki_laki", "perempuan"],
            aliases=["Kecamatan:", "Desa/Kelurahan:", "Jumlah Penduduk:", "Laki-laki:", "Perempuan:"],
            labels=True
        ).add_to(choro_layer)

        # Tooltip layang saat kursor menyentuh poligon
        folium.features.GeoJsonTooltip(fields=["KEL_DES"], aliases=["Desa: "], labels=False, sticky=True).add_to(choro_layer)

    # Memasukkan legenda warna ke peta
    colormap_peta.add_to(m)

    # Render visualisasi peta objek ke sisi kanan halaman utama
    st_folium(m, width='100%', height=550, returned_objects=[])

# ==========================================
# 5. RINGKASAN METRIK & TABEL DATA (DI BAGIAN BAWAH)
# ==========================================
st.markdown("---")

# Kalkulasi nilai metrik agregat
if not df_filter.empty:
    total_penduduk = int(df_filter['Jumlah Penduduk'].sum())
    total_laki = int(df_filter['Laki-laki'].sum())
    total_perempuan = int(df_filter['Perempuan'].sum())
    total_desa = int(df_filter['Desa'].nunique())
else:
    total_penduduk = 0
    total_laki = 0
    total_perempuan = 0
    total_desa = 0

# Menampilkan data ringkasan angka utama di bawah peta
st.markdown("### 📊 Ringkasan Data Makro Konten")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Penduduk", f"{total_penduduk:,} Jiwa")
m2.metric("Laki-laki", f"{total_laki:,} Jiwa")
m3.metric("Perempuan", f"{total_perempuan:,} Jiwa")
m4.metric("Jumlah Wilayah (Desa)", f"{total_desa} Wilayah")

st.markdown(" ")

# Wadah modular tabel detail administrasi horizontal (melebar penuh)
st.markdown("### 📋 Tabel Rekapitulasi Data Wilayah")
tab_tabel, tab_grafik = st.tabs(["Data Tabel Administrasi", "Grafik Perbandingan Demografi"])

with tab_tabel:
    if not df_filter.empty:
        df_tabel_tampil = df_filter.sort_values(by="Jumlah Penduduk", ascending=False).reset_index(drop=True)
        st.dataframe(df_tabel_tampil, use_container_width=True, height=300)
    else:
        st.info("💡 Tidak ada data yang tersedia untuk ditampilkan.")

with tab_grafik:
    if not df_filter.empty:
        df_chart = df_filter.set_index("Desa")[["Laki-laki", "Perempuan"]]
        st.bar_chart(df_chart, use_container_width=True, height=300)
    else:
