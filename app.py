import streamlit as st
import folium
from streamlit_folium import st_folium
import json
from folium.plugins import Search
import pandas as pd

# Konfigurasi halaman penuh (wide mode)
st.set_page_config(layout="wide", page_title="WebGIS Lamongan", page_icon="🌐")

# ==========================================
# 1. MEMBUAT PANEL SAMPING (SIDEBAR)
# ==========================================
with st.sidebar:
    # Menggunakan tautan logo alternatif CDN publik yang ringan dan kebal blokir
    st.image("https://icons8.com", width=70) 
    st.title("WebGIS Lamongan")
    st.write(
        "Aplikasi Dashboard Geospasial Interaktif untuk visualisasi dan analisis data "
        "kependudukan tingkat Desa/Kelurahan di wilayah Kabupaten Lamongan, Provinsi Jawa Timur."
    )
    st.markdown("---")
    st.write("📌 **Panduan Penggunaan:**")
    st.caption("1. Gunakan kolom pencarian di kanan atas peta untuk mencari desa tertentu.")
    st.caption("2. Arahkan kursor (*hover*) atau klik pada wilayah desa untuk melihat detail data.")
    st.caption("3. Gunakan ikon kertas bertumpuk di kiri atas untuk mengganti peta latar belakang (basemap).")
    
    st.markdown("---")
    st.write("📊 **Aksi Data:**")

# ==========================================
# 2. MEMBUAT KONTEN UTAMA & DATA MANAGEMENT
# ==========================================
st.title("Dashboard WebGIS Kepadatan Penduduk Kabupaten Lamongan")

# Buka file GeoJSON
with open("kab_lamongan_popmap.geojson", "r") as f:
    geo_data = json.load(f)

# Ekstrak data GeoJSON ke dalam Pandas DataFrame
records = []
for fitur in geo_data['features']:
    props = fitur['properties']
    records.append({
        'Kecamatan': props.get('KEC', 'Tidak Diketahui'),
        'Desa': props.get('KEL_DES', 'Tidak Diketahui'),
        'Jumlah Penduduk': props.get('jumlah_penduduk', 0),
        'Laki-laki': props.get('laki_laki', 0)
    })
df = pd.DataFrame(records)

# Hitung data statistik global
total_penduduk_global = int(df['Jumlah Penduduk'].sum())
desa_terpadat = df.loc[df['Jumlah Penduduk'].idxmax()]
desa_terjarang = df.loc[df['Jumlah Penduduk'].idxmin()]

# Tampilkan data statistik
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Penduduk Terdata", f"{total_penduduk_global:,} Jiwa")
with col2:
    st.metric("Desa Terpadat", f"{desa_terpadat['Desa']}", f"{int(desa_terpadat['Jumlah Penduduk']):,} Jiwa")
with col3:
    st.metric("Desa Terjarang", f"{desa_terjarang['Desa']}", f"{int(desa_terjarang['Jumlah Penduduk']):,} Jiwa")

st.markdown("### 🗺️ Peta Interaktif Kloroplet Desa")

# ==========================================
# 3. MEMBANGUN PETA FOLIUM
# ==========================================
m = folium.Map(
    location=[-7.12, 112.41], 
    zoom_start=11, 
    tiles=None,
    control_scale=True
)

# Mendaftarkan Multi-Basemap alternatif kebal abu-abu
folium.TileLayer(
    tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attr='&copy; OpenStreetMap contributors',
    name='Peta Jalan (OpenStreetMap)'
).add_to(m)

folium.TileLayer(
    tiles='https://google.com{x}&y={y}&z={z}',
    attr='Google Satellite',
    name='Citra Satelit (Google Satellite)'
).add_to(m)

folium.TileLayer(
    tiles='https://google.com{x}&y={y}&z={z}',
    attr='Google Hybrid',
    name='Satelit + Jalan (Google Hybrid)'
).add_to(m)

# Fungsi pewarnaan otomatis kloroplet desa
def ganti_warna(fitur):
    jumlah_pop = fitur['properties'].get('jumlah_penduduk', 0)
    if jumlah_pop > 6000:
        warna = '#081d58'
    elif jumlah_pop > 4500:
        warna = '#253494'
    elif jumlah_pop > 3000:
        warna = '#1d91c0'
    elif jumlah_pop > 2000:
        warna = '#41b6c4'
    elif jumlah_pop > 1000:
        warna = '#7fcdbb'
    else:
        warna = '#ffffcc'
            
    return {
        'fillColor': warna, 
        'color': '#666666',      
        'weight': 0.5,           
        'fillOpacity': 0.75       
    }

# Masukkan layer GeoJSON ke peta
choro_layer = folium.GeoJson(
    geo_data,
    name="Kloroplet Penduduk Lamongan",
    style_function=ganti_warna,
    control=True,
    highlight_function=lambda x: {'weight': 2.5, 'color': '#ff7800', 'fillOpacity': 0.9}
).add_to(m)

# Tambahkan kolom pencarian di pojok kanan atas
peta_search = Search(
    layer=choro_layer,
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

# Hover Tooltip
folium.features.GeoJsonTooltip(
    fields=["KEL_DES", "KEC"],
    aliases=["Desa/Kelurahan: ", "Kecamatan: "],
    labels=True,
    sticky=True,
    style="font-family: sans-serif; font-size: 12px; background-color: white; color: black; font-weight: bold; padding: 5px; border-radius: 3px;"
).add_to(choro_layer)

# Legenda Persegi Panjang di bawah tengah peta
legenda_html = '''
<div style="
    position: fixed; 
    bottom: 25px; 
    left: 50%; 
    transform: translateX(-50%);
    width: 650px; 
    height: 65px; 
    border: 2px solid #666666; 
    z-index: 9999; 
    font-size: 11px;
    background-color: #ffffff;
    color: #000000;
    padding: 8px 15px;
    font-family: sans-serif;
    border-radius: 6px;
    box-shadow: 3px 3px 6px rgba(0,0,0,0.3);
    text-align: center;
    ">
    <b style="display: block; margin-bottom: 6px;">Legenda Jumlah Penduduk Kabupaten Lamongan (Jiwa)</b>
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="display: flex; align-items: center;"><i style="background:#ffffcc; width:15px; height:15px; display:inline-block; margin-right:5px; border:1px solid #aaa;"></i> &le; 1.000</span>
        <span style="display: flex; align-items: center;"><i style="background:#7fcdbb; width:15px; height:15px; display:inline-block; margin-right:5px; border:1px solid #aaa;"></i> 1.001 - 2.000</span>
        <span style="display: flex; align-items: center;"><i style="background:#41b6c4; width:15px; height:15px; display:inline-block; margin-right:5px; border:1px solid #aaa;"></i> 2.001 - 3.000</span>
        <span style="display: flex; align-items: center;"><i style="background:#1d91c0; width:15px; height:15px; display:inline-block; margin-right:5px; border:1px solid #aaa;"></i> 3.001 - 4.500</span>
        <span style="display: flex; align-items: center;"><i style="background:#253494; width:15px; height:15px; display:inline-block; margin-right:5px; border:1px solid #aaa;"></i> 4.501 - 6.000</span>
        <span style="display: flex; align-items: center;"><i style="background:#081d58; width:15px; height:15px; display:inline-block; margin-right:5px; border:1px solid #aaa;"></i> &gt; 6.000</span>
    </div>
</div>
'''
m.get_root().html.add_child(folium.Element(legenda_html))

# Pop-up data lengkap saat diklik
folium.features.GeoJsonPopup(
    fields=["KEC", "KEL_DES", "jumlah_penduduk"],
    aliases=["Kecamatan: ", "Desa/Kelurahan: ", "Jumlah Penduduk: "],
    localize=True
).add_to(choro_layer)

# Tombol kontrol basemap di kiri atas
folium.LayerControl(position='topleft').add_to(m)

# Tampilkan peta ke aplikasi web Streamlit
st_folium(m, height=550, use_container_width=True)

# ==========================================
# 4. MEMBUAT GRAFIK ANALISIS DI BAWAH PETA
# ==========================================
st.markdown("---")
st.markdown("### 📊 Grafik Perbandingan Jumlah Penduduk per Kecamatan")
df_kecamatan = df.groupby('Kecamatan')['Jumlah Penduduk'].sum().reset_index()
df_kecamatan = df_kecamatan.sort_values(by='Jumlah Penduduk', ascending=False)
st.bar_chart(data=df_kecamatan, x='Kecamatan', y='Jumlah Penduduk', use_container_width=True)

# ==========================================
# 5. BUTTON UNDUH DATA PADA SIDEBAR
# ==========================================
with st.sidebar:
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Unduh Data Tabel (.CSV)",
        data=csv_data,
        file_name="data_penduduk_lamongan.csv",
        mime="text/csv",
        use_container_width=True
    )
