import streamlit as st
import json

st.set_page_config(layout="wide")
st.title("🔎 Uji Coba Pembacaan Struktur Data GeoJSON Lamongan")

try:
    # 1. Coba buka file GeoJSON
    with open("kab_lamongan_popmap.geojson", "r") as f:
        geo_data = json.load(f)
    
    st.success("✅ File GeoJSON BERHASIL dibaca oleh server Streamlit!")
    
    # 2. Ambil 1 contoh fitur teratas untuk mengintip nama kolom aslinya
    fitur_pertama = geo_data['features'][0]['properties']
    
    st.write("### Daftar Nama Kolom Atribut di File Anda Saat Ini:")
    st.info("Berikut adalah data asli dari file GeoJSON Anda. Perhatikan huruf besar/kecilnya:")
    st.json(fitur_pertama)

except Exception as e:
    st.error("❌ File GeoJSON GAGAL dibaca oleh sistem!")
    st.write(f"**Keterangan Error Fisik File:** {e}")
