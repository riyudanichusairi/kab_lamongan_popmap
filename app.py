import streamlit as st
import folium
from streamlit_folium import st_folium
import json

st.set_page_config(layout="wide")
st.title("WebGIS Kepadatan Penduduk Kabupaten Lamongan")

# 1. Buka file GeoJSON
with open("kab_lamongan_popmap.geojson", "r") as f:
    geo_data = json.load(f)

# 2. Buat objek peta dengan OpenStreetMap (OSM) asli agar gratis 100% tanpa API Key
m = folium.Map(location=[-7.12, 112.41], zoom_start=10, tiles="OpenStreetMap")

# 3. Fungsi menentukan gradasi warna BIRU yang kontras dan terang
def ganti_warna(fitur):
    jumlah_pop = fitur['properties'].get('jumlah_penduduk', 0)
    
    # Gradasi dari Biru Sangat Tua (Padat) ke Biru Muda/Kuning Terang (Jarang)
    if jumlah_pop > 50000:
        return {'fillColor': '#081d58', 'color': '#41b6c4', 'weight': 1.5, 'fillOpacity': 0.85} # Biru Navy Tua
    elif jumlah_pop > 40000:
        return {'fillColor': '#253494', 'color': '#41b6c4', 'weight': 1.5, 'fillOpacity': 0.80} # Biru Royal
    elif jumlah_pop > 30000:
        return {'fillColor': '#1d91c0', 'color': '#7fcdbb', 'weight': 1.2, 'fillOpacity': 0.75} # Biru Cerah
    elif jumlah_pop > 20000:
        return {'fillColor': '#41b6c4', 'color': '#a1dab4', 'weight': 1.2, 'fillOpacity': 0.70} # Biru Toska
    elif jumlah_pop > 10000:
        return {'fillColor': '#7fcdbb', 'color': '#ffffcc', 'weight': 1.0, 'fillOpacity': 0.65} # Biru Pudar
    else:
        return {'fillColor': '#ffffcc', 'color': '#cccccc', 'weight': 1.0, 'fillOpacity': 0.60} # Kuning/Putih Terang

# 4. Memasukkan data GeoJSON ke peta
choro_layer = folium.GeoJson(
    geo_data,
    name="Kloroplet Penduduk",
    style_function=ganti_warna,
    highlight_function=lambda x: {'weight': 3, 'color': '#ff7800', 'fillOpacity': 0.9} # Efek garis oranye menyala saat disorot
).add_to(m)

# 5. Menambahkan Fitur Pop-up saat wilayah diklik
folium.features.GeoJsonPopup(
    fields=["KEC", "jumlah_penduduk"],
    aliases=["Kecamatan: ", "Jumlah Penduduk: "],
    localize=True
).add_to(choro_layer)

# 6. Tampilkan peta ke web Streamlit
st_folium(m, width=1100, height=650)
