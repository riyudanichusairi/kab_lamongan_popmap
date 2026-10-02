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
    col_left, col_center, col_right = st.columns([1.5, 7, 1.5])
    with col_center:
        st.write("") 
        # Menggunakan parameter standar Streamlit untuk responsivitas gambar logo
        st.image("logo_lamongan.png", use_column_width=True) 
    
    st.title("WebGIS Lamongan")
    st.write(
        "Aplikasi Dashboard Geospasial Interaktif untuk visualisasi dan analisis data "
        "kependudukan tingkat Desa/Kelurahan di wilayah Kabupaten Lamongan, Provinsi Jawa Timur."
    )
    st.markdown("---")
    st.write("📌 **Panduan Penggunaan:**")
    st.caption("1. Gunakan filter 'Kecamatan' di atas peta untuk mempersempit wilayah.")
    st.caption("2. Gunakan filter 'Desa' untuk memilih atau mencentang beberapa desa tertentu saja.")
    st.caption("3. Gunakan kolom pencarian di kanan atas peta jika ingin melacak lokasi desa secara instan.")
    st.caption("4. Arahkan kursor (*hover*) atau klik pada wilayah desa di peta untuk melihat detail data demografi.")
    
    st.markdown("---")
    st.write("📊 **Aksi Data:**")

# ==========================================
# 2. DATA MANAGEMENT (MEMBACA & EKSTRAK DATA)
# ==========================================
# Buka file GeoJSON
with open("kab_lamongan_popmap.geojson", "r") as f:
    geo_data = json.load(f)

# Ekstrak properti data GeoJSON ke dalam Pandas DataFrame
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
# 3. FITUR SELEKSI BERJENJANG (KECAMATAN & DESA)
# ==========================================
st.title("Dashboard WebGIS Kepadatan Penduduk Kabupaten Lamongan")

# Ambil daftar semua kecamatan unik secara alfabetis
daftar_kecamatan = sorted(df['Kecamatan'].unique())

# Widget Dropdown Pilihan untuk menyaring Kecamatan terlebih dahulu
kecamatan_terpilih = st.selectbox(
    "📍 **Langkah 1: Filter Berdasarkan Kecamatan (Opsional):**",
    options=["-- Semua Kecamatan --"] + daftar_kecamatan
)

# Menyesuaikan opsi pilihan desa berdasarkan kecamatan yang aktif
if kecamatan_terpilih != "-- Semua Kecamatan --":
    # Jika kecamatan tertentu dipilih, filter data frame sementara dan ambil desa di kecamatan itu saja
    df_kec = df[df['Kecamatan'] == kecamatan_terpilled] if 'df_kec' in locals() else df[df['Kecamatan'] == kecamatan_terpilih]
    daftar_desa = sorted(df_kec['Desa'].unique())
else:
    # Jika memilih Semua Kecamatan, tampilkan opsi seluruh desa di Kabupaten Lamongan
    df_kec = df
    daftar_desa = sorted(df['Desa'].unique())

# Widget Pilihan Ganda untuk memilih/mencentang beberapa desa
desa_terpilih = st.multiselect(
    "🔍 **Langkah 2: Pilih / Centang Beberapa Desa yang Diinginkan:**",
    options=daftar_desa,
    placeholder="Ketik atau pilih nama beberapa desa..."
)

# ==========================================
# 4. LOGIKA FILTERING DATA UNTUK PETA & METRIK
# ==========================================
if desa_terpilih:
    # Skenario A: Jika pengguna mencentang beberapa desa secara spesifik
    df_filter = df[df['Desa'].isin(desa_terpilih)]
    
    geo_data_filter = geo_data.copy()
    geo_data_filter['features'] = [
        f for f in geo_data['features'] 
        if f['properties'].get('KEL_DES') in desa_terpilih
    ]
    label_status = "Hasil Seleksi Desa"

elif kecamatan_terpilih != "-- Semua Kecamatan --":
    # Skenario B: Jika pengguna hanya memilih Kecamatan tanpa mencentang desa (Otomatis menampilkan se-kecamatan)
    df_filter = df_kec
    
    list_desa_kec = df_kec['Desa'].tolist()
    geo_data_filter = geo_data.copy()
    geo_data_filter['features'] = [
        f for f in geo_data['features'] 
        if f['properties'].get('KEL_DES') in list_desa_kec
    ]
    label_status = f"Kec. {kecamatan_terpilih}"

else:
    # Skenario C: Jika tidak ada filter yang digunakan (Tampilan default seluruh Lamongan)
    df_filter = df
    geo_data_filter = geo_data
    label_status = "Total Lamongan"

# Hitung kalkulasi statistik dinamis berdasarkan data yang lolos filter
total_penduduk = int(df_filter['Jumlah Penduduk'].sum())
total_laki = int(df_filter['Laki-laki'].sum())
total_perempuan = int(df_filter['Perempuan'].sum())
total_desa = int(df_filter['Desa'].nunique())

# Tambahkan tombol unduh data terfilter di Sidebar secara dinamis
csv_data = df_filter.to_csv(index=False).encode('utf-8')
with st.sidebar:
    st.download_button(
        label="📥 Unduh Data Terfilter (CSV)",
        data=csv_data,
        file_name=f"data_penduduk_lamongan_{label_status.replace(' ', '_')}.csv",
        mime="text/csv"
    )

# ==========================================
# 5. MENAMPILKAN RINGKASAN METRIK
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
# 6. MEMBANGUN PETA FOLIUM DENGAN GEOMETRI FILTER
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

# Fungsi pewarnaan gradasi kepadatan penduduk wilayah
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

# Memasukkan data geo_data_filter yang dinamis ke dalam peta
choro_layer = folium.GeoJson(
    geo_data_filter,
    name="Kloroplet Penduduk Lamongan",
    style_function=ganti_warna,
    control=True,
    highlight_function=lambda x: {'weight': 2.5, 'color': '#ff7800', 'fillOpacity': 0.9}
).add_to(m)

# Fitur Pencarian di dalam peta
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

# Tooltip saat kursor diarahkan ke poligon desa
folium.features.GeoJsonTooltip(
    fields=["KEL_DES", "KEC"],
    aliases=["Desa/Kelurahan: ", "Kecamatan: "],
    labels=True,
    sticky=True,
    style="font-family: sans-serif; font-size: 12px; background-color: white; color: black; font-weight: bold; padding: 5px; border-radius: 3px;"
).add_to(choro_layer)

# Desain Legenda Peta
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

# Pop-up detail informasi saat poligon desa diklik (Tanda Kurung Sudah Ditutup Sempurna)
folium.features.GeoJsonPopup(
