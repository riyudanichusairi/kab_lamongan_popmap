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

# 3. Fungsi mewarnai peta (Membaca kolom warna_hex dari QGIS atau kalkulasi otomatis tingkat desa)
def ganti_warna(fitur):
    # Opsi A: Cek apakah ada kolom warna_hex hasil buatan QGIS Anda
    warna = fitur['properties'].get('warna_hex', None)
    if warna is None:
        warna = fitur['properties'].get('WARNA_HEX', None)
        
    # Opsi B: Jika kolom QGIS kosong/belum terunggah, hitung otomatis berdasarkan angka penduduk desa agar peta TIDAK transparan
    if warna is None or warna == '':
        jumlah_pop = fitur['properties'].get('jumlah_penduduk', 0)
        if jumlah_pop > 6000:
            warna = '#081d58'  # Biru Navy Tua
        elif jumlah_pop > 4500:
            warna = '#253494'  # Biru Royal
        elif jumlah_pop > 3000:
            warna = '#1d91c0'  # Biru Cerah
        elif jumlah_pop > 2000:
            warna = '#41b6c4'  # Biru Toska
        elif jumlah_pop > 1000:
            warna = '#7fcdbb'  # Biru Pudar
        else:
            warna = '#ffffcc'  # Kuning Terang
            
    return {
        'fillColor': warna, 
        'color': '#666666',      # Warna garis batas desa (Abu-abu tipis agar rapi)
        'weight': 0.5,           # Ketebalan garis pembatas desa
        'fillOpacity': 0.8       # Kejelasan warna agar kontras dan tidak berkabut
    }

# 4. Memasukkan data GeoJSON ke peta
choro_layer = folium.GeoJson(
    geo_data,
    name="Kloroplet Penduduk",
    style_function=ganti_warna,
    highlight_function=lambda x: {'weight': 2.5, 'color': '#ff7800', 'fillOpacity': 0.9} # Efek oranye saat kursor lewat
).add_to(m)

# 5. MENAMPILKAN SEMUA KETERANGAN ATRIBUT DI POP-UP
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
