# ==========================================
# 5. MENAMPILKAN ELEMEN VISUAL (TATA LETAK BARU)
# ==========================================

# --- POSISI 1: KARTU METRIK DI ATAS ---
st.markdown("### 📊 Ringkasan Data Konten")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Penduduk", f"{total_penduduk:,} Jiwa")
m2.metric("Laki-laki", f"{total_laki:,} Jiwa")
m3.metric("Perempuan", f"{total_perempuan:,} Jiwa")
m4.metric("Jumlah Wilayah (Desa)", f"{total_desa} Wilayah")

st.markdown("---")

# --- POSISI 2: TABEL & GRAFIK (DI ATAS PETA) ---
st.markdown("### 📈 Analisis dan Detail Data Terfilter")
col_tabel, col_grafik = st.columns(2)

with col_tabel:
    st.markdown("#### 📋 Tabel Detail Penduduk per Desa")
    # Mengurutkan tabel berdasarkan Jumlah Penduduk terbanyak agar mudah dibaca
    df_tabel_tampil = df_filter.sort_values(by="Jumlah Penduduk", ascending=False).reset_index(drop=True)
    st.dataframe(df_tabel_tampil, use_container_width=True, height=350)

with col_grafik:
    st.markdown("#### 📊 Grafik Perbandingan Populasi Desa")
    if not df_filter.empty:
        # Menyiapkan data khusus untuk kebutuhan sumbu grafik
        df_chart = df_filter.set_index("Desa")[["Laki-laki", "Perempuan"]]
        st.bar_chart(df_chart, use_container_width=True, height=350)
    else:
        st.info("💡 Tidak ada data yang tersedia untuk dibuatkan grafik berdasarkan filter saat ini.")

st.markdown("---")

# --- POSISI 3: PETA INTERAKTIF KLOROPLET (DI PALING BAWAH) ---
st.markdown("### 🗺️ Peta Interaktif Kloroplet Desa")

map_center = [-7.12, 112.41]
map_zoom = 11

m = folium.Map(
    location=map_center, 
    zoom_start=map_zoom, 
    tiles=None,
    control_scale=True
)

folium.TileLayer(
    tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attr='&copy; OpenStreetMap contributors',
    name='Peta Jalan (OpenStreetMap)'
).add_to(m)

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

choro_layer = folium.GeoJson(
    geo_data_filter,
    name="Kloroplet Penduduk Lamongan",
    style_function=ganti_warna,
    control=True,
    highlight_function=lambda x: {'weight': 2.5, 'color': '#ff7800', 'fillOpacity': 0.9}
).add_to(m)

# FUNGSI DYNAMIC AUTO-ZOOM PETA
if kecamatan_terpilih != "-- Semua Kecamatan --" or desa_terpilih:
    if geo_data_filter['features']: 
        bounds = choro_layer.get_bounds()
        m.fit_bounds(bounds) 

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

folium.features.GeoJsonTooltip(
    fields=["KEL_DES", "KEC"],
    aliases=["Desa/Kelurahan: ", "Kecamatan: "],
    labels=True,
    sticky=True,
    style="font-family: sans-serif; font-size: 12px; background-color: white; color: black; font-weight: bold; padding: 5px; border-radius: 3px;"
).add_to(choro_layer)

# Legenda HTML
legenda_html = '''
<div style="
    position: fixed; 
    bottom: 25px; 
    left: 50%; 
    transform: translateX(-50%);
    width: 750px; 
    height: 45px; 
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

# Jalankan Peta di bagian paling bawah halaman
st_folium(m, width='100%', height=550, returned_objects=[])
