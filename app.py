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
# PENTING: Silakan sesuaikan nilai angka pemisah (10000, 30000, dst) dengan rentang asli data Anda
def ganti_warna(fitur):
    # Ambil nilai angka dari properti GeoJSON Anda. 
    # PASTIKAN nama 'penduduk' di bawah ini huruf kecil/besarnya sama persis dengan yang ada di file GeoJSON Anda
    jumlah_pop = fitur['properties'].get('penduduk', 0)
    
    if jumlah_pop > 50000:
        return {'fillColor': '#800026', 'color': '#ffffff', 'weight': 1, 'fillOpacity': 0.7} # Merah Tua
    elif jumlah_pop > 40000:
        return {'fillColor': '#BD0026', 'color': '#ffffff', 'weight': 1, 'fillOpacity': 0.7}
    elif jumlah_pop > 30000:
        return {'fillColor': '#E31A1C', 'color': '#ffffff', 'weight': 1, 'fillOpacity': 0.7}
    elif jumlah_pop > 20000:
        return {'fillColor': '#FC4E2A', 'color': '#ffffff', 'weight': 1, 'fillOpacity': 0.7}
    elif jumlah_pop > 10000:
        return {'fillColor': '#FD8D3C', 'color': '#ffffff', 'weight': 1, 'fillOpacity': 0.7}
    else:
        return {'fillColor': '#FFEDA0', 'color': '#ffffff', 'weight': 1, 'fillOpacity': 0.7} # Kuning Muda

# 4. Memasukkan data GeoJSON dengan fungsi pewarnaan kloroplet dan pop-up
choro_layer = folium.GeoJson(
    geo_data,
    name="Kloroplet Penduduk",
    style_function=ganti_warna,
    highlight_function=lambda x: {'weight': 3, 'color': '#000000', 'fillOpacity': 0.8} # Efek tebal hitam saat disorot kursor
).add_to(m)

# 5. Menambahkan Fitur Pop-up saat Kecamatan diklik
# PASTIKAN nama 'KECAMATAN' dan 'penduduk' sesuai dengan struktur kolom di file GeoJSON Anda
folium.features.GeoJsonPopup(
    fields=["KECAMATAN", "penduduk"],
    aliases=["Kecamatan: ", "Jumlah Penduduk (Jiwa): "],
    localize=True
).add_to(choro_layer)

# 6. Tampilkan peta ke web Streamlit
st_folium(m, width=1000, height=600)
