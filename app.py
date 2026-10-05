import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# 1. Mengatur konfigurasi halaman WebGIS
st.set_page_config(
    page_title="WebGIS Kab. Lamongan",
    page_icon="🗺️",
    layout="wide"
)

# 2. Membuat judul dan deskripsi di halaman web
st.title("🗺️ WebGIS Interaktif Kabupaten Lamongan")
st.markdown("""
Aplikasi WebGIS ini dibuat 100% gratis menggunakan **Streamlit, GitHub, dan QGIS/GeoPandas**. 
Anda dapat melihat visualisasi data spasial secara interaktif di bawah ini.
""")

# 3. Memuat data spasial GeoJSON
# Pastikan file 'kab_lamongan_popmap.geojson' diunggah di folder GitHub yang sama dengan app.py
try:
    @st.cache_data # Fitur ini membuat loading peta jadi lebih cepat setelah dibuka pertama kali
    def load_data():
        gdf = gpd.read_file("kab_lamongan_popmap.geojson")
        # Memastikan sistem koordinat menggunakan WGS 84 (format standar peta web)
        if gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs(epsg=4326)
        return gdf

    data_lamongan = load_data()

    # 4. Membuat layout kolom untuk statistik sederhana di atas peta
    total_fitur = len(data_lamongan)
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Objek/Wilayah Terdata", value=f"{total_fitur} Data")
    with col2:
        st.info("💡 Arahkan kursor atau klik pada objek peta untuk melihat informasi detail.")

    # 5. Membuat Peta Dasar menggunakan Folium
    # Koordinat diatur otomatis di area Lamongan (-7.12, 112.41)
    m = folium.Map(location=[-7.12, 112.41], zoom_start=10, tiles="OpenStreetMap")

    # 6. Memasukkan data GeoJSON ke dalam Peta Folium
    # Fitur pop-up otomatis mendeteksi kolom 'Nama' atau kolom pertama yang ada di data Anda
    folium.GeoJson(
        data_lamongan,
        name="Batas Wilayah Lamongan",
        tooltip=folium.GeoJsonTooltip(
            fields=[data_lamongan.columns[0]], # Mengambil kolom pertama data sebagai teks saat kursor menempel
            aliases=["Info:"],
            localize=True
        )
    ).add_to(m)

    # Kontrol layer peta
    folium.LayerControl().add_to(m)

    # 7. Menampilkan peta ke halaman web Streamlit
    st_folium(m, width="100%", height=600)

except FileNotFoundError:
    st.error("❌ Berkas 'kab_lamongan_popmap.geojson' tidak ditemukan! Pastikan Anda sudah mengunggah berkas peta tersebut ke GitHub dengan nama yang sama.")
except Exception as e:
    st.error(f"⚠️ Terjadi kesalahan saat memuat peta: {e}")
