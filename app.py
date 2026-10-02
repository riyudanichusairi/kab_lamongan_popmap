import streamlit as st
import json

st.title("Uji Coba Pembacaan Data GeoJSON Lamongan")

try:
    with open("kab_lamongan_popmap.geojson", "r") as f:
        geo_data = json.load(f)
    
    st.success("File GeoJSON BERHASIL dibaca oleh sistem!")
    
    # Menampilkan 1 contoh data paling atas untuk melihat nama kolom asli dari QGIS Anda
    st.write("Daftar nama kolom di file Anda saat ini:")
    contoh_fitur = geo_data['features'][0]['properties']
    st.json(contoh_fitur)

except Exception as e:
    st.error(f"File GeoJSON GAGAL dibaca! Keterangan Error: {e}")
