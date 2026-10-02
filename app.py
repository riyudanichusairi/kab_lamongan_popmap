import streamlit as st
import folium
from streamlit_folium import st_folium
import json

st.set_page_config(layout="wide")
st.title("WebGIS Kepadatan Penduduk Kabupaten Lamongan")

# 1. Buka file GeoJSON menggunakan penanganan error yang aman
try:
    with open("kab_lamongan_popmap.geojson", "r") as f:
        geo_data = json.load(f)
except Exception as e:
    st.error(f"Gagal memuat berkas GeoJSON: {e}")
    st.stop()

# 2. Buat objek peta dasar OpenStreetMap (OSM) asli
m = folium.Map(location=[-7.12, 112.41], zoom_start=10, tiles="OpenStreetMap")

# 3. Fungsi mewarnai peta yang fleksibel dan kebal error data
def ganti_warna(fitur):
    props = fitur.get('properties', {})
    
    # Deteksi ganda untuk kolom warna buatan QGIS Anda
    warna = props.get('warna_hex', props.get('WARNA_HEX', None))
    
    # Jika kolom warna QGIS kosong atau tidak terbaca, gunakan kalkulasi otomatis berbasis jumlah penduduk
    if not warna:
        jumlah_pop = props.get('jumlah_penduduk', props.get('JUMLAH_PENDUDUK', 0))
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
        'color': '#666666',      # Garis batas wilayah abu-abu tipis
        'weight': 0.6,           
        'fillOpacity': 0.8       # Warna tegas, terang, dan tidak berkabut
    }

# 4. Memasukkan data GeoJSON ke peta
choro_layer = folium.GeoJson(
    geo_data,
    name="Kloroplet Penduduk Lamongan",
    style_function=ganti_warna,
    highlight_function=lambda x: {'weight': 2.5, 'color': '#ff7800', 'fillOpacity': 0.9}
).add_to(m)

# 5. Menambahkan Fitur Pop-up yang fleksibel (otomatis membaca data yang tersedia)
props_sample = geo_data['features'][0].get('properties', {}) if geo_data.get('features') else {}
list_fields = [k for k in ["KEC", "KEL_DES", "jumlah_penduduk"] if k in props_sample]
list_aliases = ["Kecamatan: ", "Desa/Kelurahan: ", "Jumlah Penduduk: "][:len(list_fields)]

if list_fields:
    folium.features.GeoJsonPopup(
        fields=list_fields,
        aliases=list_aliases,
        localize=True
    ).add_to(choro_layer)

# 6. Tampilkan peta ke web Streamlit
st_folium(m, width=1100, height=650)
