import streamlit as st
import leafmap.foliumap as leafmap
import json
import pandas as pd
import branca.colormap as cm

# ==========================================
# 1. KONFIGURASI HALAMAN UTAMA (WIDE MODE)
# ==========================================
st.set_page_config(layout="wide", page_title="WebGIS Lamongan - Leafmap Version", page_icon="🌐")

# ==========================================
# 2. MODIFIKASI PANEL SAMPING (SIDEBAR) & LOGO
# ==========================================
with st.sidebar:
    st.title("🌐 Tentang Aplikasi")
    
    # Memasang gambar bola dunia biru yang Anda berikan di sidebar
    logo_globe = "https://i.imgur.com/UbOXYAU.png" 
    st.image(logo_globe, use_container_width=True)
    
    st.info(
        "Aplikasi Dashboard Geospasial Interaktif ini menggabungkan kekuatan framework **Streamlit** "
        "dan pustaka **Leafmap** untuk menyajikan analisis data kependudukan tingkat Desa/Kelurahan "
        "di wilayah Kabupaten / Kota di indonesia secara real-time."
    )
    st.markdown("---")
    st.write("📌 **Panduan Navigasi Peta:**")
    st.caption("1. Gunakan panel filter di tengah halaman untuk memfilter wilayah.")
    st.caption("2. Peta dilengkapi kontrol **Minimap** di pojok kanan bawah untuk orientasi wilayah.")
    st.caption("3. Gunakan perkakas di sisi peta untuk mengganti jenis basemap (Satelit, Topografi, dll).")

# ==========================================
# 3. MANAJEMEN DATA (MEMBACA & EKSTRAK GEOJSON)
# ==========================================
try:
    with open("kab_lamongan_popmap.geojson", "r") as f:
        geo_data = json.load(f)
except FileNotFoundError:
    st.error("❌ File 'kab_lamongan_popmap.geojson' tidak ditemukan. Pastikan file spasial berada di folder yang sama.")
    st.stop()

records = []
for fitur in geo_data['features']:
    props = fitur['properties']
    records.append({
        'No_Kec': props.get('NO_KEC', '0'),
        'Kecamatan': props.get('KEC', 'Tidak Diketahui'),
        'No_Desa': props.get('NO_KEL_DES', '0'),
        'Desa': props.get('KEL_DES', 'Tidak Diketahui'),
        'Jumlah Penduduk': props.get('jumlah_penduduk', 0),
        'Laki-laki': props.get('laki_laki', 0),
        'Perempuan': props.get('perempuan', 0)
    })
df_raw = pd.DataFrame(records)

# Agregasi data agar sinkron berdasarkan nomor ID unik wilayah
df = df_raw.groupby(['No_Kec', 'Kecamatan', 'No_Desa', 'Desa'], as_index=False).agg({
    'Jumlah Penduduk': 'sum',
    'Laki-laki': 'sum',
    'Perempuan': 'sum'
})

# Judul Utama Dashboard bergaya Geospatial Apps
st.title("🗺️ WebGIS Kepadatan Penduduk Kabupaten Lamongan")
st.markdown(
    "Selamat datang di portal geospasial Lamongan. Silakan berinteraksi dengan widget filter di bawah ini "
    "untuk melihat perubahan data demografi populasi secara dinamis."
)

# ==========================================
# 4. WIDGET FILTER INTERAKTIF
# ==========================================
filter_container = st.container()
daftar_kecamatan = sorted(df['Kecamatan'].unique())

with filter_container:
    st.markdown("### 🔍 Penyaringan Data Wilayah")
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        kecamatan_terpilih = st.selectbox(
            "📍 **Pilih Kecamatan (Opsional):**",
            options=["-- Semua Kecamatan --"] + daftar_kecamatan,
            key="kecamatan_box"
        )

if kecamatan_terpilih != "-- Semua Kecamatan --":
    df_kec = df[df['Kecamatan'] == kecamatan_terpilih]
    daftar_desa = sorted(df_kec['Desa'].unique())
else:
    df_kec = df
    daftar_desa = sorted(df['Desa'].unique())

with col_f2:
    desa_terpilih = st.multiselect(
        "🔍 **Pilih Beberapa Desa/Kelurahan:**",
        options=daftar_desa,
        placeholder="Ketik nama beberapa desa...",
        key="desa_box"
    )

# Filterisasi data spasial & tabel
if desa_terpilih:
    df_filter = df[df['Desa'].isin(desa_terpilih)]
    geo_data_filter = geo_data.copy()
    geo_data_filter['features'] = [
        f for f in geo_data['features'] if f['properties'].get('KEL_DES') in desa_terpilih
    ]
    label_status = "Hasil Seleksi Desa"
elif kecamatan_terpilih != "-- Semua Kecamatan --":
    df_filter = df_kec
    geo_data_filter = geo_data.copy()
    geo_data_filter['features'] = [
        f for f in geo_data['features'] if f['properties'].get('KEC') == kecamatan_terpilih
    ]
    label_status = f"Kec. {kecamatan_terpilih}"
else:
    df_filter = df
    geo_data_filter = geo_data
    label_status = "Total Lamongan"

# Hitung metrik dinamis
total_penduduk = int(df_filter['Jumlah Penduduk'].sum())
total_laki = int(df_filter['Laki-laki'].sum())
total_perempuan = int(df_filter['Perempuan'].sum())
total_desa = int(len(df_filter))

# Tombol download di sidebar
df_download = df_filter.drop(columns=['No_Kec', 'No_Desa'])
csv_data = df_download.to_csv(index=False).encode('utf-8')
with st.sidebar:
    st.markdown("---")
    st.download_button(
        label="📥 Unduh Data Terfilter (CSV)",
        data=csv_data,
        file_name=f"data_penduduk_lamongan_{label_status.replace(' ', '_')}.csv",
        mime="text/csv"
    )

# ==========================================
# 5. ELEMEN VISUAL: METRIK, TABEL & GRAFIK
# ==========================================
st.markdown("---")
st.markdown("### 📊 Ringkasan Data Konten")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Penduduk", f"{total_penduduk:,} Jiwa")
m2.metric("Laki-laki", f"{total_laki:,} Jiwa")
m3.metric("Perempuan", f"{total_perempuan:,} Jiwa")
m4.metric("Jumlah Wilayah (Desa)", f"{total_desa} Wilayah")

st.markdown("---")
st.markdown("### 📈 Analisis Detail")
col_tabel, col_grafik = st.columns(2)

with col_tabel:
    st.markdown("#### 📋 Tabel Detail Penduduk per Desa")
    df_tabel_tampil = df_filter.sort_values(by="Jumlah Penduduk", ascending=False).reset_index(drop=True)
    df_tabel_tampil = df_tabel_tampil[['Kecamatan', 'Desa', 'Jumlah Penduduk', 'Laki-laki', 'Perempuan']]
    df_tabel_tampil.insert(0, 'No.', df_tabel_tampil.index + 1)
    st.dataframe(df_tabel_tampil, use_container_width=True, height=320, hide_index=True)

with col_grafik:
    st.markdown("#### 📊 Grafik Perbandingan Populasi")
    if not df_filter.empty:
        df_chart = df_filter.set_index("Desa")[["Laki-laki", "Perempuan"]]
        st.bar_chart(df_chart, use_container_width=True, height=320)
    else:
        st.info("💡 Tidak ada data yang tersedia untuk grafik.")

# ==========================================
# 6. INTEGRASI PETA KLOROPLET KUSTOM LEAFMAP 
# ==========================================
st.markdown("---")
st.markdown("### 🗺️ Peta Interaktif Kloroplet Desa (Leafmap Engine)")

# Membuat objek peta leafmap dengan kontrol minimap bawaan template
m = leafmap.Map(center=[-7.14, 112.33], zoom=10, minimap_control=True)

# Menambahkan basemap alternatif OpenTopoMap seperti di template kode Anda
m.add_basemap("OpenTopoMap")

# Membuat skema pewarnaan kloroplet Branca
colormap_peta = cm.StepColormap(
    colors=['#ffffcc', '#7fcdbb', '#41b6c4', '#1d91c0', '#253494', '#081d58'],
    index=[0, 1000, 2000, 3000, 4500, 6000, 10000],
    vmin=0,
    vmax=10000,
    caption="Jumlah Penduduk (Jiwa)"
)

def ganti_warna(fitur):
    jumlah_pop = fitur['properties'].get('jumlah_penduduk', 0)
    return {
        'fillColor': colormap_peta(jumlah_pop), 
        'color': '#666666',      
        'weight': 0.5,           
        'fillOpacity': 0.75       
    }

# Menambahkan data kloroplet desa ke dalam objek peta leafmap
leafmap_geojson = leafmap.folium.GeoJson(
    geo_data_filter,
    name="Kloroplet Penduduk Lamongan",
    style_function=ganti_warna,
    highlight_function=lambda x: {'weight': 2.5, 'color': '#ff7800', 'fillOpacity': 0.9}
)
leafmap_geojson.add_to(m)

# Menambahkan fitur interaksi pop-up informasi saat poligon peta diklik
leafmap.folium.features.GeoJsonPopup(
    fields=["KEC", "KEL_DES", "jumlah_penduduk", "laki_laki", "perempuan"],
    aliases=["Kecamatan:", "Desa/Kelurahan:", "Populasi Penduduk:", "Laki-laki:", "Perempuan:"],
    labels=True,
    style="font-family: sans-serif; font-size: 13px; font-weight: bold; padding: 10px;"
).add_to(leafmap_geojson)

# Menambahkan komponen legenda kustom ke peta leafmap
colormap_peta.add_to(m)

# Me-render peta Leafmap ke komponen antarmuka Streamlit
m.to_streamlit(height=550)
