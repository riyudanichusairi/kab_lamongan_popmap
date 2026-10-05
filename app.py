import streamlit as st
import folium
from streamlit_folium import st_folium
import json
from folium.plugins import Search
import pandas as pd
import branca.colormap as cm

# Konfigurasi halaman penuh (wide mode)
st.set_page_config(layout="wide", page_title="WebGIS Lamongan", page_icon="🌐")

# ==========================================
# 1. MEMBUAT PANEL SAMPING (SIDEBAR)
# ==========================================
with st.sidebar:
    col_left, col_center, col_right = st.columns([1.5, 7, 1.5])
    with col_center:
        st.write("") 
        try:
            st.image("logo_lamongan.png", use_container_width=True)
        except:
            st.warning("⚠️ Logo logo_lamongan.png tidak ditemukan.")
    
    st.title("WebGIS Penduduk Lamongan 2024")
    st.write(
        "Aplikasi Dashboard Geospasial Interaktif untuk visualisasi dan analisis data "
        "kependudukan tingkat Desa/Kelurahan di wilayah Kabupaten Lamongan, Provinsi Jawa Timur."
    )
    st.markdown("---")
    st.write("📌 **Panduan Penggunaan:**")
    st.caption("1. Gunakan panel filter di bawah untuk menyaring data berdasarkan 'Kecamatan' atau 'Desa'.")
    st.caption("2. Peta akan otomatis melakukan ZOOM ke area wilayah terfilter secara real-time.")
    st.caption("3. Peta, Metrik Utama, Tabel, dan Grafik akan berubah otomatis secara bersamaan.")
    st.caption("4. Arahkan kursor (*hover*) untuk melihat nama desa, dan **klik** wilayah desa untuk melihat tabel demografi lengkap.")
    
    st.markdown("---")
    st.write("📊 **Aksi Data:**")

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

# Title Utama Aplikasi
st.title("Dashboard WebGIS Kepadatan Penduduk Kabupaten Lamongan 2024")

# ==========================================
# 3. WIDGET FILTER (DEKLARASI CONTAINER PLACEHOLDER)
# ==========================================
filter_container = st.container()

daftar_kecamatan = sorted(df['Kecamatan'].unique())

if 'kec_key' not in st.session_state:
    st.session_state.kec_key = "-- Semua Kecamatan --"

# ==========================================
# 4. LOGIKA FILTERING DATA UNTUK SEMUA ELEMEN
# ==========================================
with filter_container:
    st.markdown("---")
    st.markdown("### 🔍 Penyaringan Data Dashboard")
    
    kecamatan_terpilih = st.selectbox(
        "📍 **Langkah 1: Filter Berdasarkan Kecamatan (Opsional):**",
        options=["-- Semua Kecamatan --"] + daftar_kecamatan,
        key="kecamatan_box"
    )

if kecamatan_terpilih != "-- Semua Kecamatan --":
    df_kec = df[df['Kecamatan'] == kecamatan_terpilih]
    daftar_desa = sorted(df_kec['Desa'].unique())
else:
    df_kec = df
    daftar_desa = sorted(df['Desa'].unique())

with filter_container:
    desa_terpilih = st.multiselect(
        "🔍 **Langkah 2: Pilih Beberapa Desa/Kelurahan:**",
        options=daftar_desa,
        placeholder="Ketik atau pilih nama beberapa desa...",
        key="desa_box"
    )

# Proses sinkronisasi data tabel dan spasial geojson
if desa_terpilih:
    df_filter = df[df['Desa'].isin(desa_terpilih)]
    geo_data_filter = geo_data.copy()
    geo_data_filter['features'] = [
        f for f in geo_data['features'] 
        if f['properties'].get('KEL_DES') in desa_terpilih
    ]
    label_status = "Hasil Seleksi Desa"

elif kecamatan_terpilih != "-- Semua Kecamatan --":
    df_filter = df_kec
    list_desa_kec = df_kec['Desa'].tolist()
    geo_data_filter = geo_data.copy()
    geo_data_filter['features'] = [
        f for f in geo_data['features'] 
        if f['properties'].get('KEL_DES') in list_desa_kec
    ]
    label_status = f"Kec. {kecamatan_terpilih}"

else:
    df_filter = df
    geo_data_filter = geo_data
    label_status = "Total Lamongan"

# Penghitungan metrik utama secara dinamis
total_penduduk = int(df_filter['Jumlah Penduduk'].sum())
total_laki = int(df_filter['Laki-laki'].sum())
total_perempuan = int(df_filter['Perempuan'].sum())
total_desa = int(df_filter['Desa'].nunique())

# Pembuatan tombol download data di sidebar
csv_data = df_filter.to_csv(index=False).encode('utf-8')
with st.sidebar:
    st.download_button(
        label="📥 Unduh Data Terfilter (CSV)",
        data=csv_data,
        file_name=f"data_penduduk_lamongan_{label_status.replace(' ', '_')}.csv",
        mime="text/csv"
    )

# ==========================================
# 5. MENAMPILKAN ELEMEN VISUAL 
# ==========================================

# --- POSISI 1: KARTU METRIK DI ATAS ---
st.markdown("### 📊 Ringkasan Data Konten")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Penduduk", f"{total_penduduk:,} Jiwa")
m2.metric("Laki-laki", f"{total_laki:,} Jiwa")
m3.metric("Perempuan", f"{total_perempuan:,} Jiwa")
m4.metric("Jumlah Wilayah (Desa)", f"{total_desa} Wilayah")

st.markdown("---")

# --- POSISI 2: TABEL & GRAFIK (DI TENGAH) ---
st.markdown("### 📈 Analisis dan Detail Data Terfilter")
col_tabel, col_grafik = st.columns(2)

with col_tabel:
    st.markdown("#### 📋 Tabel Detail Penduduk per Desa")
    df_tabel_tampil = df_filter.sort_values(by="Jumlah Penduduk", ascending=False).reset_index(drop=True)
    st.dataframe(df_tabel_tampil, use_container_width=True, height=350)

with col_grafik:
    st.markdown("#### 📊 Grafik Perbandingan Populasi Desa")
    if not df_filter.empty:
        df_chart = df_filter.set_index("Desa")[["Laki-laki", "Perempuan"]]
        st.bar_chart(df_chart, use_container_width=True, height=350)
    else:
        st.info("💡 Tidak ada data yang tersedia untuk dibuatkan grafik berdasarkan filter saat ini.")

st.markdown("---")

# --- POSISI 3: PETA INTERAKTIF KLOROPLET (DI PALING BAWAH) ---
st.markdown("### 🗺️ Peta Interaktif Kloroplet Desa")

# Koordinat default yang stabil untuk area Lamongan
map_center = [-7.12, 112.41]
map_zoom = 10

m = folium.Map(
    location=map_center, 
    zoom_start=map_zoom, 
    tiles=None,              
    control_scale=True
)

# Perbaikan Basemap 1: OpenStreetMap standar
base_osm = folium.TileLayer(
    tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attr='&copy; OpenStreetMap contributors',
    name='Peta Jalan (OpenStreetMap)',
    overlay=False,
    control=True
).add_to(m)

# Perbaikan Basemap 2: Google Satelit yang stabil dan bebas blokir CORS server cloud
base_google_sat = folium.TileLayer(
    tiles='https://google.com{x}&y={y}&z={z}',
    attr='Map data &copy; Google',
    name='Citra Satelit (Google Satellite)',
    overlay=False,
    control=True
).add_to(m)

# Perbaikan Basemap 3: Peta Minimalis Terang (Sangat bagus untuk kontras kloroplet)
base_carto = folium.TileLayer(
    tiles='https://{s}://{z}/{x}/{y}{r}.png',
    attr='&copy; OpenStreetMap contributors &copy; CARTO',
    name='Peta Ringan (CartoDB Light)',
    overlay=False,
    control=True
).add_to(m)

# Membuat skema klasifikasi warna kloroplet menggunakan Branca Python
colormap_peta = cm.StepColormap(
    colors=['#ffffcc', '#7fcdbb', '#41b6c4', '#1d91c0', '#253494', '#081d58'],
    index=,
    vmin=0,
    vmax=10000,
    caption="Jumlah Penduduk Kabupaten Lamongan per Desa (Jiwa)"
)

def ganti_warna(fitur):
    jumlah_pop = fitur['properties'].get('jumlah_penduduk', 0)
    return {
        'fillColor': colormap_peta(jumlah_pop), 
        'color': '#666666',      
        'weight': 0.5,           
        'fillOpacity': 0.65       # Diturunkan sedikit ke 0.65 agar tekstur satelit Google di bawahnya terlihat membayang cantik
    }

# Render Data Spasial Utama (Kloroplet)
choro_layer = folium.GeoJson(
    geo_data_filter,
    name="Kloroplet Penduduk Lamongan",
    style_function=ganti_warna,
    control=True,
    highlight_function=lambda x: {'weight': 2.5, 'color': '#ff7800', 'fillOpacity': 0.9},
    tooltip=folium.GeoJsonTooltip(
        fields=["KEL_DES", "jumlah_penduduk"],
        aliases=["Desa: ", "Penduduk: "],
        sticky=True
    ),
    popup=folium.GeoJsonPopup(
        fields=["KEC", "KEL_DES", "jumlah_penduduk", "laki_laki", "perempuan"],
        aliases=["Kecamatan:", "Desa/Kelurahan:", "Total Penduduk:", "Laki-laki:", "Perempuan:"],
        labels=True
    )
).add_to(m)

# Logika otomatis auto-zoom peta ke area terfilter (Hanya berjalan jika filter diisi)
if kecamatan_terpilih != "-- Semua Kecamatan --" or desa_terpilih:
    if geo_data_filter['features']: 
        bounds = choro_layer.get_bounds()
        m.fit_bounds(bounds) 

# Membuat lapisan bayangan terpisah khusus untuk menangani fungsionalitas plugin Search 
search_layer = folium.GeoJson(
    geo_data_filter,
    name="Lapisan Pencarian",
    style_function=lambda x: {'fillOpacity': 0, 'weight': 0}, 
    control=False
).add_to(m)

# Memasang fitur pencarian teks ke lapisan pencarian transparan
peta_search = Search(
    layer=search_layer,
    geom_type="Polygon",
    placeholder="Cari nama desa/kelurahan...",
    collapsed=False,
    position="topright",
    search_label="KEL_DES",
    search_zoom=14,
    weight=3,
    fill_color="#ff7800",
    fill_opacity=0.4
).add_to(m)

# Menambahkan legenda Branca ke dalam peta
colormap_peta.add_to(m)

# Menambahkan menu kontrol lapisan di pojok kiri atas peta
folium.LayerControl(position='topleft').add_to(m)

# Menampilkan hasil render peta ke Streamlit
