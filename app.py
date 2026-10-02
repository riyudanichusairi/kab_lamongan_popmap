import streamlit as st
import folium
from streamlit_folium import st_folium
import json

st.set_page_config(layout="wide")
st.title("WebGIS Kepadatan Penduduk Kabupaten Lamongan")

# 1. Buka file GeoJSON
with open("kab_lamongan_popmap.geojson", "r") as f:
    geo_data = json.load(f)

# 2. Buat objek peta dengan OpenStreetMap (OSM) asli
m = folium.Map(location=[-7.12, 112.41], zoom_start=10, tiles="OpenStreetMap")

# 3. Fungsi menentukan gradasi warna BIRU yang kontras dan terang
def ganti_warna(fitur):
    jumlah_pop = fitur['properties'].get('jumlah_penduduk', 0)
    
    if jumlah_pop > 50000:
        return {'fillColor': '#081d58', 'color': '#41b6c4', 'weight': 1.5, 'fillOpacity': 0.85} 
    elif jumlah_pop > 40000:
        return {'fillColor': '#253494', 'color': '#41b6c4', 'weight': 1.5, 'fillOpacity': 0.80} 
    elif jumlah_pop > 30000:
        return {'fillColor': '#1d91c0', 'color': '#7fcdbb', 'weight': 1.2, 'fillOpacity': 0.75} 
    elif jumlah_pop > 20000:
        return {'fillColor': '#41b6c4', 'color': '#a1dab4', 'weight': 1.2, 'fillOpacity': 0.70} 
    elif jumlah_pop > 10000:
        return {'fillColor': '#7fcdbb', 'color': '#ffffcc', 'weight': 1.0, 'fillOpacity': 0.65} 
    else:
        return {'fillColor': '#ffffcc', 'color': '#cccccc', 'weight': 1.0, 'fillOpacity': 0.60} 

# 4. Memasukkan data GeoJSON ke peta
choro_layer = folium.GeoJson(
    geo_data,
    name="Kloroplet Penduduk",
    style_function=ganti_warna,
    highlight_function=lambda x: {'weight': 3, 'color': '#ff7800', 'fillOpacity': 0.9} 
).add_to(m)

# 5. MENAMPILKAN SEMUA KETERANGAN ATRIBUT DI POP-UP
# Mendaftarkan seluruh nama atribut asli yang ada di dalam berkas GeoJSON Anda
folium.features.GeoJsonPopup(
    fields=[
        "KEC", "KEL_DES", "jumlah_penduduk", "laki_laki", 
        "PROV", "KAB_KOTA", "Connect", 
        "NO_KAB_KOTA", "NO_KEC", "NO_KEL_DES", "source"
    ],
    aliases=[
        "Kecamatan: ", "Kelurahan/Desa: ", "Total Penduduk: ", "Penduduk Laki-laki: ",
        "Provinsi: ", "Kabupaten/Kota: ", "Koneksi: ",
        "No Kab/Kota: ", "No Kecamatan: ", "No Kel/Desa: ", "Sumber Data: "
    ],
    localize=True,
    labels=True,
    style="font-family: sans-serif; font-size: 12px; max-width: 300px;"
).add_to(choro_layer)

# 6. Tampilkan peta ke web Streamlit
st_folium(m, width=1100, height=650)
