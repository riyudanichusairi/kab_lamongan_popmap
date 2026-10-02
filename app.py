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

# 2. Buat objek peta dengan OpenStreetMap (OSM) asli + Kontrol Skala
m = folium.Map(
    location=[-7.12, 112.41], 
    zoom_start=11, 
    tiles="OpenStreetMap",
    control_scale=True
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
        'fillOpacity': 0.85       
    }

# 4. Memasukkan data GeoJSON ke peta
choro_layer = folium.GeoJson(
    geo_data,
    name="Kloroplet Penduduk Lamongan",
    style_function=ganti_warna,
    highlight_function=lambda x: {'weight': 2.5, 'color': '#ff7800', 'fillOpacity': 0.9}
).add_to(m)

# 5. PERBAIKAN POSISI: MENAMBAHKAN KOLOM PENCARIAN DI KANAN ATAS
peta_search = Search(
    layer=choro_layer,
    geom_type="Polygon",
    placeholder="Cari nama desa/kelurahan...",
    collapsed=False,
    position="topright",                        # <-- Memindahkan ke pojok kanan atas peta
    search_label="KEL_DES",
    search_zoom=14,
    weight=3,
    fill_color="#ff7800",
    fill_opacity=0.4
).add_to(m)

# 6. FITUR HOVER TOOLTIP: Nama desa muncul dinamis saat kursor menyentuh wilayah
folium.features.GeoJsonTooltip(
    fields=["KEL_DES", "KEC"],
    aliases=["Desa/Kelurahan: ", "Kecamatan: "],
    labels=True,
    sticky=True,
    style="font-family: sans-serif; font-size: 12px; background-color: white; color: black; font-weight: bold; padding: 5px; border-radius: 3px;"
).add_to(choro_layer)

# 7. PERBAIKAN BENTUK: LEGENDA MODEL PERSEGI PANJANG DI BAWAH TENGAH PETA
legenda_html = '''
<div style="
    position: fixed; 
    bottom: 25px; 
    left: 50%; 
    transform: translateX(-50%);               /* Memosisikan kotak pas di tengah-tengah bawah */
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

# 8. Menambahkan Fitur Pop-up saat wilayah diklik
folium.features.GeoJsonPopup(
    fields=["KEC", "KEL_DES", "jumlah_penduduk"],
    aliases=["Kecamatan: ", "Desa/Kelurahan: ", "Jumlah Penduduk: "],
    localize=True
).add_to(choro_layer)

# 9. Tampilkan peta ke web Streamlit
st_folium(m, height=650, use_container_width=True)
