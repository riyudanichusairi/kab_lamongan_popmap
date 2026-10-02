import streamlit as st
import folium
from streamlit_folium import st_folium
import json

st.set_page_config(layout="wide")
st.title("WebGIS Kepadatan Penduduk Kabupaten Lamongan")

# 1. Buka file GeoJSON
with open("kab_lamongan_popmap.geojson", "r") as f:
    geo_data = json.load(f)

# 2. Buat objek peta folium dasar
m = folium.Map(location=[-7.12, 112.41], zoom_start=10, tiles="CartoDB positron")

# 3. Fungsi untuk menentukan gradasi warna berdasarkan jumlah penduduk
def ganti_warna(fitur):
    # Menggunakan kolom 'jumlah_penduduk' sesuai data asli GeoJSON Anda
    jumlah_pop = fitur['properties'].get('jumlah_penduduk', 0)
    
    if jumlah_pop > 50000:
        return {'fillColor': '#800026', 'color': '#ffffff', 'weight': 1, 'fillOpacity': 0.7} 
    elif jumlah_pop > 40000:
        return {'fillColor': '#BD0026', 'color': '#ffffff', 'weight': 1, 'fillOpacity': 0.7}
    elif jumlah_pop > 30000:
        return {'fillColor': '#E31A1C', 'color': '#ffffff', 'weight': 1, 'fillOpacity': 0.7}
    elif jumlah_pop > 20000:
        return {'fillColor': '#FC4E2A', 'color': '#ffffff', 'weight': 1, 'fillOpacity': 0.7}
    elif jumlah_pop > 10000:
        return {'fillColor': '#FD8D3C', 'color': '#ffffff', 'weight': 1, 'fillOpacity': 0.7}
    else:
        return {'fillColor': '#FFEDA0', 'color': '#ffffff', 'weight': 1, 'fillOpacity': 0.7} 

# 4. Memasukkan data GeoJSON dengan fungsi pewarnaan kloroplet dan pop-up
choro_layer = folium.GeoJson(
    geo_data,
    name="Kloroplet Penduduk",
    style_function=ganti_warna,
    highlight_function=lambda x: {'weight': 3, 'color': '#000000', 'fillOpacity': 0.8} 
).add_to(m)

# 5. Menambahkan Fitur Pop-up saat Kecamatan diklik dengan kolom 'KEC' dan 'jumlah_penduduk'
folium.features.GeoJsonPopup(
    fields=["KEC", "jumlah_penduduk"],
    aliases=["Kecamatan: ", "Jumlah Penduduk: "],
    localize=True
).add_to(choro_layer)

# 6. Tampilkan peta ke web Streamlit
st_folium(m, width=1000, height=600)
