import streamlit as st
import folium
from streamlit_folium import st_folium
import json
from folium.plugins import Search, Draw
import pandas as pd
from shapely.geometry import shape, box

# Konfigurasi halaman penuh (wide mode)
st.set_page_config(layout="wide", page_title="WebGIS Lamongan", page_icon="🌐")

# ==========================================
# 1. MEMBUAT PANEL SAMPING (SIDEBAR)
# ==========================================
with st.sidebar:
    col_left, col_center, col_right = st.columns([1.5, 7, 1.5])
    with col_center:
        st.write("") 
        st.image("logo_lamongan.png", use_container_width=True) 
    
    st.title("WebGIS Lamongan")
    st.write(
        "Aplikasi Dashboard Geospasial Interaktif untuk visualisasi dan analisis data "
        "kependudukan tingkat Desa/Kelurahan di wilayah Kabupaten Lamongan, Provinsi Jawa Timur."
    )
    st.markdown("---")
    st.write("📌 **Panduan Penggunaan Tool Seleksi Peta:**")
    st.caption("1. Gunakan ikon 🔳 **Kotak (Draw a rectangle)** pada menu toolbar di kiri peta.")
    st.caption("2. Klik dan seret mouse pada peta untuk membuat area kotak seleksi.")
    st.caption("3. Angka metrik di atas peta akan otomatis menjumlahkan desa yang masuk ke dalam area kotak tersebut.")
    st.caption("4. Untuk menghapus area kotak, klik ikon 🗑️ pada toolbar peta.")
    
    st.markdown("---")
    st.write("📊 **Aksi Data:**")

# ==========================================
# 2. DATA MANAGEMENT & INISIALISASI
# ==========================================
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
        'Laki-laki': props.get('laki_laki', 0),
        'Perempuan': props.get('perempuan', 0)
    })
df = pd.DataFrame(records)

# Inisialisasi Session State untuk menyimpan nama-nama desa yang terjaring dalam kotak gambar mouse
if "desa_terseksi_spatial" not in st.session_state:
    st.session_state.desa_terseksi_spatial = []

# ==========================================
# 3. KONTEN UTAMA & LOGIKA FILTER SPASIAL MOUSE
# ==========================================
st.title("Dashboard WebGIS Kepadatan Penduduk Kabupaten Lamongan")

# Menentukan apakah filter spasial aktif
if st.session_state.desa_terseksi_spatial:
    df_filter = df[df['Desa'].isin(st.session_state.desa_terseksi_spatial)]
    label_status = "Hasil Seleksi Mouse"
    total_desa = len(st.session_state.desa_terseksi_spatial)
else:
    df_filter = df
    label_status = "Total Lamongan"
    total_desa = int(df['Desa'].nunique())

# Hitung ringkasan statistik
total_penduduk = int(df_filter['Jumlah Penduduk'].sum())
total_laki = int(df_filter['Laki-laki'].sum())
total_perempuan = int(df_filter['Perempuan'].sum())

# ==========================================
# 4. MENAMPILKAN 4 KOLOM METRIK (HASIL FILTER SPASIAL)
# ==========================================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(f"Total Penduduk ({label_status})", f"{total_penduduk:,} Jiwa")
with col2:
    st.metric(f"Jumlah Laki-laki ({label_status})", f"{total_laki:,} Jiwa")
with col3:
    st.metric(f"Jumlah Perempuan ({label_status})", f"{total_perempuan:,} Jiwa")
with col4:
    st.metric("Jumlah Desa Terseleksi", f"{total_desa} Desa")

st.markdown("### 🗺️ Peta Interaktif Kloroplet Desa")

# ==========================================
# 5. MEMBANGUN PETA FOLIUM DENGAN TOOL DRAW (SELEKSI MOUSE)
# ==========================================
m = folium.Map(
    location=[-7.12, 112.41], 
    zoom_start=11, 
    tiles=None,
    control_scale=True
)

folium.TileLayer(
    tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attr='&copy; OpenStreetMap contributors',
    name='Peta Jalan (OpenStreetMap)'
).add_to(m)

# Tambahkan Tool Gambar Kotak Seleksi (Draw Plugin) di sisi kiri peta
plugin_gambar = Draw(
    export=False,
    position="topleft",
    draw_options={
        'polyline': False,
        'polygon': False,
        'circle': False,
        'marker': False,
        'circlemarker': False,
        'rectangle': True  # Hanya aktifkan gambar persegi/kotak seleksi
    },
    edit_options={
        'poly': {'allowIntersection': False}
    }
)
plugin_gambar.add_to(m)

def ganti_warna(fitur):
    jumlah_pop = fitur['properties'].get('jumlah_penduduk', 0)
    nama_desa_fitur = fitur['properties'].get('KEL_DES')
    
    # Beri warna khusus jika desa masuk ke dalam area seleksi mouse
    if st.session_state.desa_terseksi_spatial and nama_desa_fitur in st.session_state.desa_terseksi_spatial:
        return {
            'fillColor': '#ff7800', 
            'color': '#ff0000',      
            'weight': 1.5,           
            'fillOpacity': 0.85       
        }
        
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

choro_layer = folium.GeoJson(
    geo_data,
    name="Kloroplet Penduduk Lamongan",
    style_function=ganti_warna,
    control=True,
    highlight_function=lambda x: {'weight': 2.5, 'color': '#ff7800', 'fillOpacity': 0.9}
).add_to(m)

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

folium.features.GeoJsonTooltip(
    fields=["KEL_DES", "KEC"],
    aliases=["Desa/Kelurahan: ", "Kecamatan: "],
    labels=True,
    sticky=True,
    style="font-family: sans-serif; font-size: 12px; background-color: white; color: black; font-weight: bold; padding: 5px; border-radius: 3px;"
).add_to(choro_layer)

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

folium.features.GeoJsonPopup(
    fields=["KEC", "KEL_DES", "laki_laki", "perempuan", "jumlah_penduduk"],
    aliases=["Kecamatan: ", "Desa/Kelurahan: ", "Laki-laki: ", "Perempuan: ", "Jumlah Penduduk: "],
    localize=True
).add_to(choro_layer)

folium.LayerControl(position='topleft').add_to(m)

# Tampilkan peta dan tangkap data geometri dari mouse
st_peta_data = st_folium(m, height=550, use_container_width=True, key="peta_lamongan_draw")

# LOGIKA SPASIAL: Mendeteksi gambar kotak dari mouse pengguna
if st_peta_data and "last_active_drawing" in st_peta_data:
    info_gambar = st_peta_data["last_active_drawing"]
    
    if info_gambar and info_gambar.get("geometry"):
        # Buat bentuk geometri pembatas berdasarkan input kotak mouse
        kotak_seleksi = shape(info_gambar["geometry"])
        
        desa_terjaring = []
        for fitur in geo_data['features']:
            poligon_desa = shape(fitur['geometry'])
            # Jika poligon desa bersinggungan atau masuk ke dalam kotak mouse, masukkan ke daftar seleksi
            if kotak_seleksi.intersects(poligon_desa):
                nama_desa = fitur['properties'].get('KEL_DES')
                if nama_desa:
                    desa_terjaring.append(nama_desa)
        
        # Perbarui metrik layar jika isi seleksi berubah
        if sorted(st.session_state.desa_terseksi_spatial) != sorted(desa_terjaring):
            st.session_state.desa_terseksi_spatial = desa_terjaring
            st.rerun()
            
    # Jika gambar kotak dihapus oleh pengguna lewat tong sampah toolbar peta
    elif info_gambar is None and st.session_state.desa_terseksi_spatial != []:
        st.session_state.desa_terseksi_spatial = []
        st.rerun()

