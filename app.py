import streamlit as st
import folium
from streamlit_folium import st_folium
import json
from folium.plugins import Search
import pandas as pd
import branca.colormap as cm

# 1. KONFIGURASI HALAMAN UTAMA (WIDE MODE)
st.set_page_config(layout="wide", page_title="Visualisasi Data Kependudukan", page_icon="🌐")

# Menambahkan CSS kustom agar layout lebih presisi dan clean mirip gambar
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    div[data-testid="stVerticalBlock"] > div:has(div.stDataFrame) { margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA MANAGEMENT (MEMBACA & EKSTRAK DATA)
# ==========================================
try:
    with open("kab_lamongan_popmap.geojson", "r") as f:
        geo_data = json.load(f)
except FileNotFoundError:
    st.error("❌ File 'kab_lamongan_popmap.geojson' tidak ditemukan. Harap pastikan file spasial berada di folder yang sama.")
    st.stop()

records = []
for fitur in geo_data['features']:
    props = fitur['properties']
    records.append({
        'Kecamatan': props.get('KEC', 'Tidak Diketahui'),
        'Desa': props.get('KEL_DES', 'Tidak Diketahui'),
        'Jumlah Penduduk': props.get('jumlah_penduduk', 0),
        'Laki-laki': props.get('laki_laki', 0),
        'Perempuan': props.get('perempuan', 0)
    })
df = pd.DataFrame(records)

# ==========================================
# 3. HEADER APLIKASI (MIRIP TOP BAR DUKCAPIL)
# ==========================================
col_logo, col_title = st.columns([1, 11])
with col_logo:
    try:
        st.image("logo_lamongan.png", width=60)
    except:
        st.text("🌐")
with col_title:
    st.subheader("VISUALISISASI DATA KEPENDUDUKAN")
    st.caption("KABUPATEN LAMONGAN - DINAS KEPENDUDUKAN DAN PENCATATAN SIPIL")

st.markdown("---")

# ==========================================
# 4. PEMBAGIAN KOLOM UTAMA (KIRI: FILTER, KANAN: PETA)
# ==========================================
# Kolom kiri diset lebih kecil (3) untuk panel kontrol, kolom kanan lebih besar (9) untuk peta
col_kontrol, col_peta = st.columns([3, 9])

# --- PANEL KONTROL SEBELAH KIRI ---
with col_kontrol:
    st.markdown("### 🔍 Cari Data Wilayah")
    
    daftar_kecamatan = sorted(df['Kecamatan'].unique())
    
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
        daftar_desa = sorted(df['Desa'].unique())

    desa_terpilih = st.multiselect(
        "Kelurahan/Desa:",
        options=daftar_desa,
        placeholder="- Pilih Desa -",
        key="desa_box"
    )
    
    # Logika filter data spasial & tabel
    if desa_terpilih:
        df_filter = df[df['Desa'].isin(desa_terpilih)]
        geo_data_filter = geo_data.copy()
        geo_data_filter['features'] = [
            f for f in geo_data['features'] if f['properties'].get('KEL_DES') in desa_terpilih
        ]
        label_status = "Hasil Seleksi Desa"
    elif kecamatan_terpilih != "-- Semua Kecamatan --":
        df_filter = df_kec
        list_desa_kec = df_kec['Desa'].tolist()
        geo_data_filter = geo_data.copy()
        geo_data_filter['features'] = [
            f for f in geo_data['features'] if f['properties'].get('KEL_DES') in list_desa_kec
        ]
        label_status = f"Kec. {kecamatan_terpilih}"
    else:
        df_filter = df
        geo_data_filter = geo_data
        label_status = "Total Lamongan"

    st.markdown("---")
    
    # Menu Tambahan (Daftar Peta) mirip sisi kiri gambar
    st.markdown("### 📂 Daftar Layer Peta")
    st.checkbox("🔘 Kepadatan Penduduk", value=True)
    st.checkbox("⚪ Fasilitas Pendidikan", value=False)
    st.checkbox("⚪ Fasilitas Kesehatan", value=False)
    
    # Aksi data / Download ditaruh di bawah panel kontrol
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
    # Informasi singkat di atas peta (Alert/Info Box)
    st.info("💡 Batas wilayah administrasi yang digunakan dalam peta ini bersifat indikatif.")
    
    # Setup Folium Map
    map_center = [-7.14, 112.33]
    map_zoom = 10
    
    m = folium.Map(location=map_center, zoom_start=map_zoom, tiles=None, control_scale=True)
    
    # Menggunakan peta satelit/hybrid agar estetikanya mirip basemap pada gambar
    folium.TileLayer(
        tiles='https://google.com{x}&y={y}&z={z}',
        attr='Google Hybrid',
        name='Google Satelit (Hybrid)'
    ).add_to(m)

    # Skema Klasifikasi Warna
    colormap_peta = cm.StepColormap(
        colors=['#ffffcc', '#7fcdbb', '#41b6c4', '#1d91c0', '#253494', '#081d58'],
        index=[0, 1000, 2000, 3000, 4500, 6000, 10000],
        vmin=0, vmax=10000,
        caption="Jumlah Penduduk per Desa (Jiwa)"
    )

    def ganti_warna(fitur):
        jumlah_pop = fitur['properties'].get('jumlah_penduduk', 0)
        return {
            'fillColor': colormap_peta(jumlah_pop), 
            'color': '#ff1a1a',  # Outline merah tipis agar mirip dengan gambar contoh
            'weight': 1.2,           
            'fillOpacity': 0.4       
        }

    choro_layer = folium.GeoJson(
        geo_data_filter,
        name="Kloroplet Penduduk",
        style_function=ganti_warna,
        control=True,
        highlight_function=lambda x: {'weight': 2.5, 'color': '#ffff00', 'fillOpacity': 0.6}
    ).add_to(m)

    if kecamatan_terpilih != "-- Semua Kecamatan --" or desa_terpilih:
        if geo_data_filter['features']: 
            bounds = choro_layer.get_bounds()
            m.fit_bounds(bounds) 

    # Fitur pencarian peta
    peta_search = Search(
        layer=choro_layer, geom_type="Polygon", placeholder="Cari desa...",
        collapsed=True, position="topright", search_label="KEL_DES", search_zoom=14
    ).add_to(m)

    # Pop-up & Tooltip
    folium.features.GeoJsonPopup(
        fields=["KEC", "KEL_DES", "jumlah_penduduk", "laki_laki", "perempuan"],
        aliases=["Kecamatan:", "Desa:", "Penduduk:", "Laki-laki:", "Perempuan:"],
        labels=True
    ).add_to(choro_layer)

    folium.features.GeoJsonTooltip(fields=["KEL_DES"], aliases=["Desa: "], labels=False, sticky=True).add_to(choro_layer)
    colormap_peta.add_to(m)

    # Render peta dengan ukuran penuh di sisi kanan
    st_folium(m, width='100%', height=550, returned_objects=[])

# ==========================================
# 5. TABEL STRUKTUR REKAPITULASI (DI BAGIAN BAWAH)
# ==========================================
st.markdown("---")
st.markdown("### 📊 Tabel Data Berdasarkan Wilayah")

# Membuat tab ringkasan data agar terlihat rapi dan modular
tab_tabel, tab_grafik = st.tabs(["📋 Data Tabel Administrasi", "📈 Grafik Perbandingan"])

with tab_tabel:
    df_tabel_tampil = df_filter.sort_values(by="Jumlah Penduduk", ascending=False).reset_index(drop=True)
    # Tampilan tabel melebar penuh di bawah peta
    st.dataframe(df_tabel_tampil, use_container_width=True, height=300)

with tab_grafik:
    if not df_filter.empty:
        df_chart = df_filter.set_index("Desa")[["Laki-laki", "Perempuan"]]
        st.bar_chart(df_chart, use_container_width=True, height=300)
    else:
        st.info("💡 Tidak ada data untuk grafik.")
