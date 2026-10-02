import streamlit as st
import folium
from streamlit_folium import st_folium
import json
from folium.plugins import Search

st.set_page_config(layout="wide")
st.title("WebGIS Kepadatan Penduduk Kabupaten Lamongan")

# 1. Buka file GeoJSON
with open("kab_lamongan_popmap.geojson", "r") as f:
    geo_data = json.load(f)

# 2. Buat objek peta dasar
m = folium.Map(
    location=[-7.12, 112.41], 
    zoom_start=11, 
    tiles=None,
    control_scale=True
)

# 3. FIX BASEMAP JALAN & SATELIT: Menambahkan sub-domain alternatif agar bebas dari layar abu-abu
# Opsi 1: Peta Jalan Standar (OpenStreetMap Standar)
folium.TileLayer(
    tiles='https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    attr='&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors',
    name='Peta Jalan (OpenStreetMap)'
).add_to(m)

# Opsi 2: Peta Citra Satelit (Google Satellite) - Sangat Stabil
folium.TileLayer(
    tiles='https://google.com{x}&y={y}&z={z}',
    attr='Google Satellite',
    name='Citra Satelit (Google Satellite)'
).add_to(m)

# Opsi 3: Peta Jalan + Satelit (Google Hybrid) - Membantu melihat nama jalan di atas citra satelit
folium.TileLayer(
    tiles='https://google.com{x}&y={y}&z={z}',
    attr='Google Hybrid',
    name='Satelit + Jalan (Google Hybrid)'
).add_to(m)

# Opsi 4: Mode Gelap Eksklusif (Stadia Alidade Smooth Dark)
folium.TileLayer(
    tiles='https://stadiamaps.com{z}/{x}/{y}.png',
    attr='&copy; Stadia Maps, &copy; OpenStreetMap',
    name='Mode Gelap (Stadia Dark)'
).add_to(m)


# 4. Fungsi mewarnai peta otomatis berdasarkan angka penduduk desa
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

# 5. Memasukkan data GeoJSON ke peta
choro_layer = folium.GeoJson(
    geo_data,
    name="Kloroplet Penduduk Lamongan",
    style_function=ganti_warna,
    control=True,
    highlight_function=lambda x: {'weight': 2.5, 'color': '#ff7800', 'fillOpacity': 0.9}
).add_to(m)


# 6. KOLOM PENCARIAN DI POJOK KANAN ATAS
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

# 7. FITUR HOVER TOOLTIP
folium.features.GeoJsonTooltip(
    fields=["KEL_DES", "KEC"],
    aliases=["Desa/Kelurahan: ", "Kecamatan: "],
    labels=True,
    sticky=True,
    style="font-family: sans-serif; font-size: 12px; background-color: white; color: black; font-weight: bold; padding: 5px; border-radius: 3px;"
).add_to(choro_layer)

# 8. LEGENDA PERSEGI PANJANG DI BAWAH TENGAH PETA
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

# 9. Menambahkan Fitur Pop-up saat wilayah diklik
folium.features.GeoJsonPopup(
    fields=["KEC", "KEL_DES", "jumlah_penduduk"],
    aliases=["Kecamatan: ", "Desa/Kelurahan: ", "Jumlah Penduduk: "],
    localize=True
).add_to(choro_layer)

# 10. TOMBOL PENGENDALI LAYER DI SEBELAH KIRI ATAS
folium.LayerControl(position='topleft').add_to(m)

# 11. Tampilkan peta ke web Streamlit
st_folium(m, height=650, use_container_width=True)
