import streamlit as st
import folium
from streamlit_folium import st_folium
import json
from shapely.geometry import shape

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
        'fillOpacity': 0.85       # Menaikkan kejelasan warna poligon agar lebih mantap
    }

# 4. Memasukkan data GeoJSON ke peta
choro_layer = folium.GeoJson(
    geo_data,
    name="Kloroplet Penduduk Lamongan",
    style_function=ganti_warna,
    highlight_function=lambda x: {'weight': 2.5, 'color': '#ff7800', 'fillOpacity': 0.9}
).add_to(m)

# 5. SOLUSI ANTI-KABUT: Menampilkan nama desa menggunakan DivIcon teks murni
# Teks akan ditempatkan pas di titik tengah (centroid) masing-masing wilayah desa
for fitur in geo_data['features']:
    nama_desa = fitur['properties'].get('KEL_DES', '')
    geom = fitur.get('geometry')
    
    if geom and nama_desa:
        # Hitung titik tengah poligon desa secara otomatis
        s = shape(geom)
        centroid = s.centroid
        lat, lon = centroid.y, centroid.x
        
        # Cetak teks langsung ke peta tanpa kontainer HTML transparan
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(
                html=f'''
                <div style="
                    font-size: 8px; 
                    font-weight: bold; 
                    color: #000000; 
                    text-align: center;
                    white-space: nowrap;
                    transform: translate(-50%, -50%);
                    text-shadow: 1.5px 1.5px 2px #ffffff, -1.5px -1.5px 2px #ffffff;
                ">{nama_desa}</div>
                '''
            )
        ).add_to(m)

# 6. MENAMBAHKAN KOTAK LEGENDA SOLID (TIDAK TRANSPARAN)
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

# 7. Menambahkan Fitur Pop-up saat wilayah diklik
folium.features.GeoJsonPopup(
    fields=["KEC", "KEL_DES", "jumlah_penduduk"],
    aliases=["Kecamatan: ", "Desa/Kelurahan: ", "Jumlah Penduduk: "],
    localize=True
).add_to(choro_layer)

# 8. Tampilkan peta ke web Streamlit
st_folium(m, height=650, use_container_width=True)
