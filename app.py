import streamlit as st
import folium
from streamlit_folium import st_folium
import json  # Gunakan json, bawaan python (tidak perlu ditulis di requirements.txt)

st.title("WebGIS Kabupaten Lamongan")

# 1. Buka file GeoJSON menggunakan library json biasa
with open("kab_lamongan_popmap.geojson", "r") as f:
    geo_data = json.load(f)

# 2. Buat objek peta folium (sesuaikan koordinat tengah Lamongan)
m = folium.Map(location=[-7.12, 112.41], zoom_start=10)

# 3. Masukkan data GeoJSON ke dalam peta
folium.GeoJson(geo_data, name="Batas Kecamatan").add_to(m)

# 4. Tampilkan peta di Streamlit
st_folium(m, width=700, height=500)
