import streamlit as st
import folium
from streamlit_folium import st_folium
import json

st.set_page_config(layout="wide")
st.title("WebGIS Kepadatan Penduduk Kabupaten Lamongan")

# 1. Buka file GeoJSON
with open("kab_lamongan_popmap.geojson", "r") as f:
    geo_data = json.load(f)

# 2. Buat objek peta dengan OpenStreetMap (OSM) asli + AKTIFKAN KONTROL SKALA PETA
m = folium.Map(
    location=[-7.12, 112.41], 
    zoom_start=10, 
    tiles="OpenStreetMap",
    control_scale=True  # <-- Baris ini otomatis memunculkan skala meter/kilometer di pojok kiri bawah peta
)

# 3. Fungsi mewarnai peta otomatis berdasarkan angka penduduk desa
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
        'fillOpacity': 0.8       
    }

# 4. Memasukkan data GeoJSON ke peta
choro_layer = folium.GeoJson(
    geo_data,
    name="Kloroplet Penduduk Lamongan",
    style_function=ganti_warna,
    highlight_function=lambda x: {'weight': 2.5, 'color': '#ff7800', 'fillOpacity': 0.9}
).add_to(m)

# 5. MENAMBAHKAN KOTAK LEGENDA MANUAl (Agar terbaca di HP & Laptop)
legenda_html = '''
<div style="
    position: fixed; 
    bottom: 50px; left: 50px; width: 220px; height: 180px; 
    border:2px solid grey; z-index:9999; font-size:12px;
    background-color:white;
    padding: 10px;
    opacity: 0.85;
    font-family: sans-serif;
    border-radius: 5px;
    ">
    <b>Legenda Penduduk (Jiwa)</b><br>
    <i style="background:#081d58; width:18px; height:18px; float:left; margin-right:8px; opacity:0.8;"></i> > 6.000<br>
    <i style="background:#253494; width:18px; height:18px; float:left; margin-right:8px; opacity:0.8;"></i> 4.501 - 6.000<br>
    <i style="background:#1d91c0; width:18px; height:18px; float:left; margin-right:8px; opacity:0.8;"></i> 3.001 - 4.500<br>
    <i style="background:#41b6c4; width:18px; height:18px; float:left; margin-right:8px; opacity:0.8;"></i> 2.001 - 3.000<br>
    <i style="background:#7fcdbb; width:18px; height:18px; float:left; margin-right:8px; opacity:0.8;"></i> 1.001 - 2.000<br>
    <i style="background:#ffffcc; width:18px; height:18px; float:left; margin-right:8px; opacity:0.8;"></i> &le; 1.000<br>
</div>
'''
m.get_root().html.add_child(folium.Element(legenda_html))

# 6. Menambahkan Fitur Pop-up
folium.features.GeoJsonPopup(
    fields=["KEC", "KEL_DES", "jumlah_penduduk"],
    aliases=["Kecamatan: ", "Desa/Kelurahan: ", "Jumlah Penduduk: "],
    localize=True
).add_to(choro_layer)

# 7. Tampilkan peta ke web Streamlit (Menggunakan use_container_width agar responsif di HP)
st_folium(m, height=650, use_container_width=True)
