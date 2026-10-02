import streamlit as st
import folium
from streamlit_folium import st_folium
import json
from folium.plugins import Search  # Memanggil plugin pencarian peta otomatis

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

# 5. BARU: MENAMBAHKAN FITUR KOLOM PENCARIAN (SEARCH BAR)
# Mengindeks layer GeoJSON berdasarkan kolom 'KEL_DES' (Nama Desa)
peta_search = Search(
    layer=choro_layer,
    geom_type="Polygon",
    placeholder="Cari nama desa/kelurahan...", # Teks pembuka di kolom input
    collapsed=False,                            # Membuat kolom pencarian langsung terbuka lebar
    search_label="KEL_DES",                     # Kolom GeoJSON yang dijadikan target ketik
    search_zoom=14,                             # Tingkat kedekatan zoom otomatis saat lokasi ditemukan
    weight=3,
    fill_color="#ff7800",                       # Efek warna wilayah saat terpilih di hasil pencarian
    fill_opacity=0.4
).add_to(m)

# 6. FITUR HOVER TOOLTIP: Nama desa muncul dinamis saat kursor menyentuh wilayah (Anti-Kabut)
folium.features.GeoJsonTooltip(
    fields=["KEL_DES", "KEC"],
    aliases=["Desa/Kelurahan: ", "Kecamatan: "],
    labels=True,
    sticky=True,
    style="font-family: sans-serif; font-size: 12px; background-color: white; color: black; font-weight: bold; padding: 5px; border-radius: 3px;"
).add_to(choro_layer)

# 7. MENAMBAHKAN KOTAK LEGENDA SOLID (TIDAK TRANSPARAN)
legenda_html = '''
<div style="
    position: fixed; 
    bottom: 50px; left: 50px; width: 220px; height: 180px; 
    border:2px solid #666666; z-index:9999; font-size:12px;
    background-color: #ffffff;
    color: #000000;
    padding: 10px;
    font-family: sans-serif;
    border-radius: 5px;
    box-shadow: 3px 3px 5px rgba(0,0,0,0.3);
    ">
    <b>Legenda Penduduk (Jiwa)</b><br><br>
    <i style="background:#081d58; width:18px; height:18px; float:left; margin-right:8px; opacity:0.9; border:1px solid #fff;"></i> <span>&gt; 6.000</span><br>
    <i style="background:#253494; width:18px; height:18px; float:left; margin-right:8px; opacity:0.9; border:1px solid #fff;"></i> <span>4.501 - 6.000</span><br>
    <i style="background:#1d91c0; width:18px; height:18px; float:left; margin-right:8px; opacity:0.9; border:1px solid #fff;"></i> <span>3.001 - 4.500</span><br>
    <i style="background:#41b6c4; width:18px; height:18px; float:left; margin-right:8px; opacity:0.9; border:1px solid #fff;"></i> <span>2.001 - 3.000</span><br>
    <i style="background:#7fcdbb; width:18px; height:18px; float:left; margin-right:8px; opacity:0.9; border:1px solid #fff;"></i> <span>1.001 - 2.000</span><br>
    <i style="background:#ffffcc; width:18px; height:18px; float:left; margin-right:8px; opacity:0.9; border:1px solid #fff;"></i> <span>&le; 1.000</span><br>
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
