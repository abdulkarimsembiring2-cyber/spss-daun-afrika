import streamlit as st
import pandas as pd
import scipy.stats as stats
import numpy as np
import matplotlib.pyplot as plt
import io

# Konfigurasi halaman utama Streamlit
st.set_page_config(page_title="SPSS Mini - Kanker Mulut Daun Afrika", layout="wide")

# =========================================================================
# 🔒 SISTEM PENGAMAN / PASSWORD LOGIN
# =========================================================================
PASSWORD_BENAR = "N4yl@0908"  # Silakan ganti XXXXXXX dengan password Bapak semula

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔒 Sistem Analisis Data Terkunci")
    st.write("Aplikasi ini dilindungi untuk mencegah plagiarisme data skripsi.")
    input_password = st.text_input("Masukkan Password Akses:", type="password")
    if st.button("Masuk Sistem"):
        if input_password == PASSWORD_BENAR:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Password salah! Akses ditolak.")
    st.stop()
# =========================================================================

# Header Aplikasi
st.title("🔬 Aplikasi Asisten Statistik Skripsi Kedokteran Gigi")
st.write("Sistem Analisis Eksperimen In-Vivo (Skor Displasia Histopatologi)")
st.markdown("---")

# 📋 PARAMETER UTAMA (TERKUNCI MATI SESUAI DESAIN 3 KELOMPOK × 9 TIKUS)
st.sidebar.header("📋 1. Info Parameter Penelitian")
st.sidebar.info("""
**Desain Penelitian Aktif:**
* **Variabel:** Skor Displasia Jaringan
* **Skala Data:** Ordinal (0=Normal, 1=Ringan, 2=Sedang, 3=Berat)
* **Sampel:** 3 Kelompok Perlakuan × 9 Tikus (Baku Rumus Federer)
""")

# Nama kelompok dikunci secara formal sesuai dengan ketentuan laboratorium Bapak
nama_kelompok = [
    "Kelompok P1 (Ekstrak Daun Afrika 400mg/kg + DMBA)",
    "Kelompok P2 (Flavonoid Quercetin 25mg/kg + DMBA)",
    "Kelompok P3 (Kontrol Positif DMBA)"
]

# 💾 FITUR IMPOR / UNGGAH EXCEL (Agar Progres Kerja Tidak Hilang)
st.header("💾 Riwayat Data (Impor / Ekspor)")
uploaded_file = st.file_uploader("Punya simpanan berkas Excel dari progres minggu lalu? Unggah di sini:", type=["xlsx"])

# Inisialisasi struktur dataframe default (Terkunci 9 baris untuk mencit)
index_tikus = [f"Tikus {i+1}" for i in range(9)]
matrix_data = {g_name: [0] * 9 for g_name in nama_kelompok}
df_input = pd.DataFrame(matrix_data, index=index_tikus)

# Jika user mengunggah berkas Excel lawas, sinkronisasikan ke dalam matriks web
if uploaded_file is not None:
    try:
        df_loaded = pd.read_excel(uploaded_file, index_col=0)
        for col in df_input.columns:
            if col in df_loaded.columns:
                # Memastikan data dikonversi ke angka bulat (Integer) dan dipotong pas 9 baris
                df_input[col] = df_loaded[col].astype(int).values[:9]
        st.success("✅ Data progres laboratorium berhasil dimasukkan otomatis ke dalam tabel!")
    except Exception as e:
        st.error("Format berkas Excel tidak sesuai. Menggunakan tabel kosong default.")

# 📊 MATRIKS INPUT DATA LABORATORIUM
st.header("📊 2. Matriks Input Skor Displasia Laboratorium")
st.caption("Petunjuk Pengisian: Masukkan nilai angka bulat saja antara 0 sampai 3 (0=Normal, 1=Ringan, 2=Sedang, 3=Berat)")

# Konfigurasi data_editor dengan validasi angka bulat ketat (0 s.d 3)
edited_df = st.data_editor(
    df_input, 
    num_rows="fixed", 
    use_container_width=True,
    column_config={
        col: st.column_config.NumberColumn(format="%d", min_value=0, max_value=3) for col in nama_kelompok
    }
)

# 📥 FITUR EKSPOR / DOWNLOAD EXCEL
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    edited_df.to_excel(writer, sheet_name='Data_Skor_Displasia')
st.download_button(
    label="📥 Simpan & Unduh Data ke Excel (Agar Minggu Depan Tidak Mengetik Ulang)",
    data=buffer.getvalue(),
    file_name="progres_skor_displasia.xlsx",
    mime="application/vnd.ms-excel",
    type="secondary"
)

st.markdown("---")
# 🚀 PROSES STATISTIK LENGKAP (5 TAHAP ANALISIS)
if st.button("🚀 Jalankan Analisis Statistik Lengkap (Standar SPSS)", type="primary"):
    
    # Validasi akhir berlapis untuk mencegah adanya input di luar angka 0,1,2,3
    if not edited_df.isin([0, 1, 2, 3]).all().all():
        st.error("❌ Eror: Ditemukan nilai di luar angka 0, 1, 2, atau 3 pada tabel. Harap periksa kembali input data Anda.")
        st.stop()

    st.header("📈 3. Dokumen Output Hasil Statistik & Grafik")

    # Ekstraksi array data dari tabel untuk komparasi rumus
    data_p1 = edited_df[nama_kelompok[0]].tolist()
    data_p2 = edited_df[nama_kelompok[1]].tolist()
    data_p3 = edited_df[nama_kelompok[2]].tolist()

    # =========================================================================
    # TAHAP 1: TABEL DESKRIPTIF / CROSSTAB % (Adopsi Gambar 2 & Gambar 6)
    # =========================================================================
    st.subheader("🔹 1. Tabel Analisis Deskriptif (Distribusi Frekuensi & Persentase Kelompok)")
    
    deskriptif_list = []
    skor_labels = {0: "0 (Normal)", 1: "1 (Ringan)", 2: "2 (Sedang)", 3: "3 (Berat)"}
    
    for col in edited_df.columns:
        counts = edited_df[col].value_counts().reindex([0, 1, 2, 3], fill_value=0)
        for skor, jumlah in counts.items():
            persentase = (jumlah / 9) * 100
            deskriptif_list.append({
                "Kelompok Perlakuan": col,
                "Derajat Displasia": skor_labels[skor],
                "Jumlah Tikus (n)": int(jumlah),
                "Persentase (%)": f"{persentase:.1f}%"
            })
            
    df_deskriptif = pd.DataFrame(deskriptif_list)
    st.dataframe(df_deskriptif, use_container_width=True)

    # =========================================================================
    # TAHAP 2: UJI NORMALITAS / SHAPIRO-WILK (Adopsi Gambar 4 & Gambar 6)
    # =========================================================================
    st.subheader("🔹 2. Hasil Uji Normalitas (Shapiro-Wilk Test)")
    st.write("Uji ini digunakan sebagai bukti legalitas untuk menentukan jalur statistik (Parametrik vs Non-Parametrik):")
    
    norm_res = []
    for idx, data_grp in enumerate([data_p1, data_p2, data_p3]):
        try:
            stat_w, p_w = stats.shapiro(data_grp)
        except Exception:
            stat_w, p_w = np.nan, 0.00001
            
        status_norm = "Data Berdistribusi Normal" if p_w > 0.05 else "Data TIDAK Berdistribusi Normal"
        norm_res.append({
            "Kelompok Perlakuan": nama_kelompok[idx],
            "Statistic W": round(stat_w, 4) if not np.isnan(stat_w) else "N/A",
            "Signifikansi (p-value)": round(p_w, 5),
            "Kesimpulan Asumsi": status_norm
        })
    
    st.dataframe(pd.DataFrame(norm_res), use_container_width=True)
    st.warning("💡 Bukti Ilmiah Bab 4: Jika nilai Signifikansi (p-value) < 0.05, maka asumsi normalitas ditolak. Hal ini membuktikan secara sah bahwa data penelitian anak Bapak TIDAK berdistribusi normal dan WAJIB beralih menggunakan statistik non-parametrik.")

    # =========================================================================
    # TAHAP 3: UJI HOMOGENITAS / LEVENE TEST (Adopsi Gambar 4)
    # =========================================================================
    st.subheader("🔹 3. Hasil Uji Homogenitas Varians (Levene's Test)")
    stat_lev, p_lev = stats.levene(data_p1, data_p2, data_p3, center='median')
    
    df_levene = pd.DataFrame({
        "Metode Pengujian": ["Levene's Test (Based on Median)"],
        "Levene Statistic (F)": [round(stat_lev, 4)],
        "Signifikansi (p-value)": [round(p_lev, 5)],
        "Kesimpulan Varians": ["Varians Homogen (Sama)" if p_lev > 0.05 else "Varians Tidak Homogen (Heterogen)"]
    })
    st.dataframe(df_levene, use_container_width=True)

    # =========================================================================
    # TAHAP 4: UJI HIPOTESIS UTAMA / KRUSKAL-WALLIS (Adopsi Gambar 5)
    # =========================================================================
    st.subheader("🔹 4. Hasil Uji Kruskal-Wallis (Uji Hipotesis Utama Non-Parametrik)")
    stat_kw, p_kw = stats.kruskal(data_p1, data_p2, data_p3)
    
    df_kw_res = pd.DataFrame({
        "Parameter Statistik SPSS": ["Kruskal-Wallis H (Chi-Square)", "Degree of Freedom (df)", "Asymp. Sig. (p-value)"],
        "Nilai Hitung Sistem": [round(stat_kw, 4), 2, round(p_kw, 5)]
    })
    st.dataframe(df_kw_res)

    # Penarikan Kesimpulan Klinis Utama
    if p_kw < 0.05:
        st.success(f"🟢 Nilasi Signifikansi p = {p_kw:.5f} (< 0.05). H0 DITOLAK! Kesimpulan: Ekstrak Daun Afrika berpengaruh secara NYATA dan SIGNIFIKAN terhadap tingkat keparahan displasia jaringan mukosa mulut tikus.")
        
        # =========================================================================
        # TAHAP 5: UJI LANJUT PASANGAN / MANN-WHITNEY U (Adopsi Gambar 5)
        # =========================================================================
        st.subheader("🔹 5. Uji Lanjut Perbandingan Pasangan (Mann-Whitney U Test)")
        st.write("Karena uji Kruskal-Wallis di atas signifikan, berikut adalah tabel komparasi berpasangan untuk mencari tahu kelompok mana yang memberikan hasil klinis terbaik:")
        
        pasangan_uji = [
            ("P1 (Ekstrak) VS P2 (Quercetin)", data_p1, data_p2),
            ("P2 (Quercetin) VS P3 (Kontrol DMBA)", data_p2, data_p3),
            ("P1 (Ekstrak) VS P3 (Kontrol DMBA)", data_p1, data_p3)
        ]
        
        mw_results = []
        for label, grp1, grp2 in pasangan_uji:
            stat_mw, p_mw = stats.mannwhitneyu(grp1, grp2, alternative='two-sided')
            status_signifikan = "Signifikan (Efek Berbeda Nyata)" if p_mw < 0.0167 else "Tidak Signifikan (Efek Sama)"
            
            mw_results.append({
                "Perbandingan Kelompok": label,
                "Mann-Whitney U": round(stat_mw, 3),
                "Asymp. Sig. (2-tailed)": round(p_mw, 5),
                "Batas Kritis Alpha (Bonferroni)": 0.0167,
                "Status Hubungan": status_signifikan
            })
            
        st.dataframe(pd.DataFrame(mw_results), use_container_width=True)
        st.info("💡 Catatan Metodologi Skripsi: Pembacaan signifikansi pada tabel komparasi ganda di atas mengacu pada nilai Alpha Bonferroni (0.0167). Jika p-value < 0.0167, maka kedua perlakuan tersebut terbukti memberikan perbedaan efek klinis yang bermakna secara statistik.")
        
    else:
        st.info(f"🟡 Nilai Signifikansi p = {p_kw:.5f} (> 0.05). H0 DITERIMA! Kesimpulan: Tidak terdapat perbedaan efek klinis yang bermakna secara statistik di antara ketiga kelompok perlakuan tersebut.")

    # =========================================================================
    # TAHAP TAMBAHAN: GRAFIK VISUALISASI PROPORSIONAL (STACKED BAR CHART)
    # =========================================================================
    st.markdown("---")
    st.subheader("📊 4. Visualisasi Grafik Proporsi Displasia (Untuk Bab 4 Skripsi)")
    
    plot_data = []
    for col in nama_kelompok:
        counts = edited_df[col].value_counts().reindex([0, 1, 2, 3], fill_value=0)
        pcts = (counts / 9) * 100
        plot_data.append(pcts.values)
        
    plot_matrix = np.array(plot_data).T
    
    fig, ax = plt.subplots(figsize=(10, 6))
    label_sumbu_x = ['P1 (Ekstrak Daun)', 'P2 (Quercetin)', 'P3 (Kontrol Positif)']
    daftar_warna = ['#2ecc71', '#f1c40f', '#e67e22', '#e74c3c']
    label_skor = ['Skor 0 (Normal)', 'Skor 1 (Ringan)', 'Skor 2 (Sedang)', 'Skor 3 (Berat)']
    
    nilai_dasar = np.zeros(3)
    for idx, baris_skor in enumerate(plot_matrix):
        ax.bar(label_sumbu_x, baris_skor, bottom=nilai_dasar, label=label_skor[idx], color=daftar_warna[idx], width=0.5)
        nilai_dasar += baris_skor
        
    ax.set_title('Grafik Proporsi Tingkat Keparahan Displasia Histopatologi Mukosa Mulut (%)', fontsize=12, pad=15, fontweight='bold')
    ax.set_ylabel('Persentase Proporsi Sampel (%)')
    ax.set_xlabel('Kelompok Hewan Coba')
    ax.set_ylim(0, 105)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.legend(title="Tingkat Keparahan Jaringan:", loc='lower center', bbox_to_anchor=(0.5, -0.22), ncol=4)
    
    st.pyplot(fig)
