import os
import streamlit as st

# 1. PENGATURAN HALAMAN (Wajib ditaruh di baris paling atas setelah import)
st.set_page_config(
    page_title="Dashboard WebGIS Lamongan",
    page_icon="📊",
    layout="wide",  # Mengaktifkan mode layar penuh/lebar sesuai gambar Anda
    initial_sidebar_state="expanded"
)

# 2. PENANGANAN JALUR LOGO ABSOLUT
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "logo_lamongan.png")

# ==========================================
# 3. STRUKTUR SIDEBAR (BILAH SAMPING)
# ==========================================
with st.sidebar:
    # Mengatur layout kolom agar logo berada di tengah sidebar
    col_left, col_center, col_right = st.columns([1.5, 7, 1.5])
    with col_center:
        st.write("") 
        try:
            # Memanggil berkas menggunakan jalur absolut yang aman
            st.image(logo_path, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ Logo logo_lamongan.png tidak ditemukan. Eror: {e}")

    # Informasi Aplikasi di Sidebar
    st.markdown("### WebGIS Lamongan")
    st.caption(
        "Aplikasi Dashboard Geospasial Interaktif untuk visualisasi dan "
        "analisis data kependudukan tingkat Desa/Kelurahan di wilayah "
        "Kabupaten Lamongan, Provinsi Jawa Timur."
    )
    
    st.write("---")
    
    # Panduan Penggunaan
    st.markdown("#### 📌 Panduan Penggunaan:")
    st.markdown(
        "1. Gunakan panel filter di bawah untuk menyaring data berdasarkan 'Kecamatan' atau 'Desa'.\n"
        "2. Peta akan otomatis melakukan ZOOM ke area wilayah yang terpilih."
    )


# ==========================================
# 4. STRUKTUR KONTEN UTAMA (MAIN DASHBOARD)
# ==========================================

# Judul Utama Dashboard
st.title("Dashboard WebGIS Kepadatan Penduduk Kabupaten Lamongan")
st.write("---")

# Bagian 1: Penyaringan Data Dashboard
st.markdown("### 🔍 Penyaringan Data Dashboard")

# Filter Kecamatan
st.markdown("**📍 Langkah 1: Filter Berdasarkan Kecamatan :**")
pilihan_kecamatan = st.selectbox(
    "Pilih Kecamatan",
    options=["- Semua Kecamatan -", "Lamongan", "Babot", "Glagah", "Sukodadi"],
    label_visibility="collapsed" # Menyembunyikan label bawaan agar rapi mirip gambar Anda
)

# Filter Desa/Kelurahan
st.markdown("**🔍 Langkah 2: Pilih Berdasarkan Desa/Kelurahan :**")
pilihan_desa = st.multiselect(
    "Ketik atau pilih nama beberapa desa...",
    options=["Desa A", "Desa B", "Kelurahan C"],
    placeholder="Ketik atau pilih nama beberapa desa..."
)

st.write("")

# Bagian 2: Ringkasan Data Webgis (Metric Cards)
st.markdown("### 📊 Ringkasan Data Webgis")

# Membuat 4 kolom untuk menampilkan metrik angka sesuai di gambar
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(label="Total Penduduk", value="1,327,897 Jiwa")

with kpi2:
    st.metric(label="Laki-laki", value="670,136 Jiwa")

with kpi3:
    st.metric(label="Perempuan", value="657,743 Jiwa")

with kpi4:
    st.metric(label="Jumlah Wilayah (Desa)", value="444 Wilayah")

st.write("---")

# Area Peta (Silakan integrasikan dengan objek Folium atau Plotly Anda di bawah ini)
st.markdown("### 🗺️ Visualisasi Peta Spasial")
st.info("Tempatkan komponen peta interaktif Anda (st_folium / st.plotly_chart) di area ini.")
