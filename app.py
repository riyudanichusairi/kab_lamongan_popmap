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

# 3. Membuat Peta Kloroplet & Pop-up Informasi
# PENTING: Ganti 'KECAMATAN' dan 'penduduk' sesuai nama kolom asli di file GeoJSON Anda
choro = folium.Choropleth(
    geo_data=geo_data,
    name="Kloroplet Penduduk",
    data=geo_data,
    columns=["properties.KECAMATAN", "properties.penduduk"], # Kolom wilayah & data angka
    key_on="feature.properties.KECAMATAN",                 # Kunci penghubung GeoJSON
    fill_color="YlOrRd",                                    # Gradasi warna (Kuning ke Merah)
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Jumlah Penduduk (Jiwa)",
    highlight=True                                          # Efek menyala saat kursor di atasnya
).add_to(m)

# 4. Menambahkan Fitur Pop-up saat Kecamatan diklik
choro.geojson.add_child(
    folium.features.GeoJsonPopup(
        fields=["KECAMATAN", "penduduk"],                   # Kolom yang ingin ditampilkan di pop-up
        aliases=["Kecamatan: ", "Jumlah Penduduk: "],       # Label teks di dalam kotak pop-up
        localize=True
    )
)

# 5. Tampilkan peta ke web Streamlit
st_folium(m, width=1000, height=600)
