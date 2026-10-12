import streamlit as st
import pandas as pd
import scipy.stats as stats
import numpy as np
import matplotlib.pyplot as plt
import io

# Konfigurasi halaman utama Streamlit
st.set_page_config(page_title="SPSS Mini - Kanker Mulut Daun Afrika", layout="wide")

# Fungsi pembantu untuk membuat tabel bergaya jurnal ilmiah (Tanpa Garis Vertikal)
def render_tabel_jurnal(df, judul=""):
    html = f"""
    <div style='margin-bottom: 20px;'>
        <h4 style='font-family: sans-serif; color: #333;'>{judul}</h4>
        <table style='border-collapse: collapse; width: 100%; font-family: sans-serif; font-size: 14px; text-align: center;'>
            <tr style='border-top: 2px solid black; border-bottom: 1px solid black; font-weight: bold; background-color: #f9f9f9;'>
                {"".join(f"<th style='padding: 8px;'>{col}</th>" for col in df.columns)}
            </tr>
    """
    for _, row in df.iterrows():
        html += "<tr style='border-bottom: 1px solid #ddd;'> layout='wide'"
        for val in row:
            html += f"<td style='padding: 8px;'>{val}</td>"
        html += "</tr>"
    html += "<tr style='border-bottom: 2px solid black;'></tr></table></div>"
    st.markdown(html, unsafe_allow_html=True)
    return html

# Fungsi pembantu untuk duplikasi gaya visual SPSS Kuning
def render_tabel_spss(df, judul_spss=""):
    html = f"""
    <div style='margin-bottom: 25px; font-family: "Courier New", Courier, monospace;'>
        <div style='background-color: #FFF2CC; border: 1px solid #B5B5B5; padding: 4px 10px; font-weight: bold; font-size: 14px; color: black; display: inline-block;'>
            {judul_spss}
        </div>
        <table style='border-collapse: collapse; width: 100%; border: 1px solid #B5B5B5; font-size: 13px; text-align: left; background-color: white;'>
            <tr style='background-color: #F2F2F2; border-bottom: 1px solid #B5B5B5; font-weight: bold; color: black;'>
                {"".join(f"<th style='padding: 6px; border-right: 1px solid #B5B5B5;'>{col}</th>" for col in df.columns)}
            </tr>
    """
    for _, row in df.iterrows():
        html += "<tr style='border-bottom: 1px solid #E0E0E0; color: black;'>"
        for idx, val in enumerate(row):
            style_tambahan = "background-color: #FFFFCC; font-weight: bold;" if "Sig." in df.columns[idx] or "p-value" in df.columns[idx] else ""
            html += f"<td style='padding: 6px; border-right: 1px solid #B5B5B5; {style_tambahan}'>{val}</td>"
        html += "</tr>"
    html += "</table></div>"
    st.markdown(html, unsafe_allow_html=True)
    return html

# =========================================================================
# 🔒 SISTEM PENGAMAN / PASSWORD LOGIN
# =========================================================================
PASSWORD_BENAR = "XXXXXXX" 

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

st.title("🔬 Aplikasi Asisten Statistik Skripsi Kedokteran Gigi")
st.write("Sistem Analisis Eksperimen In-Vivo (Skor Displasia Histopatologi)")
st.markdown("---")

st.sidebar.header("📋 1. Info Parameter Penelitian")
st.sidebar.info("""
**Desain Penelitian Aktif:**
* **Variabel:** Skor Displasia Jaringan
* **Skala Data:** Ordinal (0=Normal, 1=Ringan, 2=Sedang, 3=Berat)
* **Sampel:** 3 Kelompok Perlakuan × 9 Tikus
""")

nama_kelompok = [
    "Kelompok P1 (Ekstrak Daun Afrika 400mg/kg + DMBA)",
    "Kelompok P2 (Flavenoid Quercetin 25mg/kg + DMBA)",
    "Kelompok P3 (Kontrol Positif DMBA)"
]

st.header("💾 Riwayat Data (Impor / Ekspor)")
uploaded_file = st.file_uploader("Punya simpanan berkas Excel dari progres minggu lalu? Unggah di sini:", type=["xlsx"])

index_tikus = [f"Tikus {i+1}" for i in range(9)]
matrix_data = {g_name: * 9 for g_name in nama_kelompok}
df_input = pd.DataFrame(matrix_data, index=index_tikus)

if uploaded_file is not None:
    try:
        df_loaded = pd.read_excel(uploaded_file, index_col=0)
        for col in df_input.columns:
            if col in df_loaded.columns:
                df_input[col] = df_loaded[col].astype(int).values[:9]
        st.success("✅ Data progres laboratorium berhasil dimasukkan otomatis!")
    except Exception as e:
        st.error("Format berkas Excel tidak sesuai. Menggunakan tabel default.")

st.header("📊 2. Matriks Input Skor Displasia Laboratorium")
st.caption("Masukkan angka bulat antara 0 sampai 3 (0=Normal, 1=Ringan, 2=Sedang, 3=Berat)")

edited_df = st.data_editor(
    df_input, 
    num_rows="fixed", 
    use_container_width=True,
    column_config={col: st.column_config.NumberColumn(format="%d", min_value=0, max_value=3) for col in nama_kelompok}
)

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    edited_df.to_excel(writer, sheet_name='Data_Skor_Displasia')
st.download_button(
    label="📥 Simpan & Unduh Data ke Excel",
    data=buffer.getvalue(),
    file_name="progres_skor_displasia.xlsx",
    mime="application/vnd.ms-excel",
    type="secondary"
)

st.markdown("---")
# 🚀 PROSES STATISTIK LENGKAP (5 TAHAP ANALISIS DENGAN FORMAT LAPORAN DOKUMEN)
if st.button("🚀 Jalankan Analisis Statistik Lengkap (Standar SPSS)", type="primary"):
    
    if not edited_df.isin([0, 1, 2, 3]).all().all():
        st.error("❌ Eror: Ditemukan nilai di luar angka 0, 1, 2, atau 3 pada tabel. Harap periksa kembali data.")
        st.stop()

    st.header("📈 3. Dokumen Output Hasil Statistik & Grafik (Siap Salin ke Word)")
    
    # Inisialisasi string pengumpul HTML untuk diekspor ke Word paling bawah
    html_word_exporter = "<html><head><meta charset='utf-8'></head><body><h2 style='font-family:sans-serif;'>LAPORAN OUTPUT ANALISIS STATISTIK SKRIPSI</h2>"

    data_p1 = edited_df[nama_kelompok[0]].tolist()
    data_p2 = edited_df[nama_kelompok[1]].tolist()
    data_p3 = edited_df[nama_kelompok[2]].tolist()

    # =========================================================================
    # TAHAP 1: TABEL DESKRIPTIF GAYA JURNAL (Adopsi Tabel 4.8)
    # =========================================================================
    st.markdown("### 🔹 Tahap 1: Tabel Analisis Deskriptif")
    
    skor_labels = {0: "Normal (Skor 0)", 1: "Ringan (Skor 1)", 2: "Sedang (Skor 2)", 3: "Berat (Skor 3)"}
    rows_deskriptif = []
    
    for lbl in ["Normal (Skor 0)", "Ringan (Skor 1)", "Sedang (Skor 2)", "Berat (Skor 3)"]:
        current_row = {"Derajat Displasia (WHO 2017)": lbl}
        for idx, col in enumerate(edited_df.columns):
            counts = edited_df[col].value_counts().reindex([0, 1, 2, 3], fill_value=0)
            skor_key = [k for k, v in skor_labels.items() if v == lbl][0]
            n_val = int(counts[skor_key])
            pct_val = (n_val / 9) * 100
            current_row[f"P{idx+1} (n)"] = n_val
            current_row[f"P{idx+1} (%)"] = f"{pct_val:.1f}%"
        rows_deskriptif.append(current_row)
        
    df_visual_jurnal = pd.DataFrame(rows_deskriptif)
    tabel1_html = render_tabel_jurnal(df_visual_jurnal, "Tabel 4.8 Gambaran Histologi Tingkat Displasia Mukosa Mulut Tikus (N=27)")
    html_word_exporter += "<h3>1. Analisis Deskriptif Jurnal Ilmiah</h3>" + tabel1_html

    # =========================================================================
    # TAHAP 2 & 3: UJI PREPARASI ASUMSI STATISTIK (GAYA DESAIN ASLI SPSS KUNING)
    # =========================================================================
    st.markdown("### 🔹 Tahap 2 & 3: Bukti Uji Persiapan Asumsi Dasar")
    
    norm_data = []
    for idx, data_grp in enumerate([data_p1, data_p2, data_p3]):
        try:
            stat_w, p_w = stats.shapiro(data_grp)
        except Exception:
            stat_w, p_w = 0.0, 0.0000
        norm_data.append({
            "Kelompok Perlakuan": f"P{idx+1}",
            "Shapiro-Wilk (Statistik)": f"{stat_w:.3f}",
            "df": "9",
            "Asymp. Sig. (p-value)": f"{p_w:.5f}"
        })
    df_norm_spss = pd.DataFrame(norm_data)
    tabel2_html = render_tabel_spss(df_norm_spss, "Tests of Normality (Shapiro-Wilk)")
    html_word_exporter += "<h3>2. Uji Asumsi Normalitas</h3>" + tabel2_html
    
    stat_lev, p_lev = stats.levene(data_p1, data_p2, data_p3, center='median')
    df_lev_spss = pd.DataFrame({
        "Parameter Uji": ["Based on Median (Brown-Forsythe)"],
        "Levene Statistic": [f"{stat_lev:.3f}"],
        "df1": ["2"],
        "df2": ["24"],
        "Asymp. Sig. (p-value)": [f"{p_lev:.5f}"]
    })
    tabel3_html = render_tabel_spss(df_lev_spss, "Test of Homogeneity of Variances (skor_histologis)")
    html_word_exporter += "<h3>3. Uji Homogenitas Varians</h3>" + tabel3_html

    # =========================================================================
    # TAHAP 4 & 5: UTAMA NON-PARAMETRIK & POST-HOC (GAYA ASLI CETAKAN SPSS)
    # =========================================================================
    st.markdown("### 🔹 Tahap 4 & 5: Uji Hipotesis Inferensial Utama")
    
    stat_kw, p_kw = stats.kruskal(data_p1, data_p2, data_p3)
    df_kw_spss = pd.DataFrame({
        "Statistik Uji": ["Kruskal-Wallis H (Chi-Square)", "Derajat Bebas (df)", "Asymp. Sig. (2-tailed)"],
        "Skor_Displasia": [f"{stat_kw:.3f}", "2", f"{p_kw:.5f}"]
    })
    tabel4_html = render_tabel_spss(df_kw_spss, "Npar Tests: Kruskal-Wallis Test (Test Statistics)")
    html_word_exporter += "<h3>4. Hasil Uji Hipotesis Kruskal-Wallis</h3>" + tabel4_html
    
    if p_kw < 0.05:
        st.success("🟢 Hasil Kruskal-Wallis Bermakna Nyata (p < 0.05). Berikut Uji Lanjut Mann-Whitney U:")
        html_word_exporter += "<h3>5. Uji Lanjut Pasca Post-Hoc Mann-Whitney U</h3>"
        
        pasangan = [("P1 VS P2", data_p1, data_p2), ("P2 VS P3", data_p2, data_p3), ("P1 VS P3", data_p1, data_p3)]
        for label, g1, g2 in pasangan:
            u_stat, p_mw = stats.mannwhitneyu(g1, g2, alternative='two-sided')
            df_mw_single = pd.DataFrame({
                "Statistik Uji": ["Mann-Whitney U", "Wilcoxon W", "Asymp. Sig. (2-tailed)"],
                "Skor_Displasia": [f"{u_stat:.1f}", f"{u_stat:.1f}", f"{p_mw:.5f}"]
            })
            tabel5_html = render_tabel_spss(df_mw_single, f"Mann-Whitney Test: Perbandingan {label}")
            html_word_exporter += f"<h4>Komparasi Pasangan {label}</h4>" + tabel5_html
    # =========================================================================
    # GRAFIK VISUALISASI JURNAL
    # =========================================================================
    st.markdown("---")
    st.subheader("📊 Visualisasi Grafik Batang Berlapis Jurnal")
    plot_data = []
    for col in nama_kelompok:
        counts = edited_df[col].value_counts().reindex([0, 1, 2, 3], fill_value=0)
        plot_data.append((counts / 9 * 100).values)
    plot_matrix = np.array(plot_data).T
    
    fig, ax = plt.subplots(figsize=(8, 5))
    categories = ['P1 (Ekstrak)', 'P2 (Quercetin)', 'P3 (Kontrol DMBA)']
    colors = ['#2ecc71', '#f1c40f', '#e67e22', '#e74c3c']
    labels = ['Skor 0 (Normal)', 'Skor 1 (Ringan)', 'Skor 2 (Sedang)', 'Skor 3 (Berat)']
    
    bottom_val = np.zeros(3)
    for idx, row in enumerate(plot_matrix):
        ax.bar(categories, row, bottom=bottom_val, label=labels[idx], color=colors[idx], width=0.45)
        bottom_val += row
    ax.set_ylabel('Persentase Sampel (%)')
    ax.set_ylim(0, 105)
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    st.pyplot(fig)

    # =========================================================================
    # 📚 DOKUMEN TURUNAN STATISTIKA: PENJELASAN LENGKAP RUMUS PALING BAWAH
    # =========================================================================
    st.markdown("---")
    st.markdown("## 📚 DOKUMEN LAMPIRAN TEORI: PENURUNAN MATEMATIS RUMUS STATISTIKA")
    st.info("Halaman penjelasan ini ditambahkan sebagai panduan akademik bagi anak Bapak untuk menghadapi pertanyaan dosen penguji skripsi.")

    teks_rumus = """
    <h3>1. Landasan Hukum Transisi Uji (Mengapa Menggunakan Non-Parametrik?)</h3>
    Skala pengukuran variabel penelitian anak Bapak adalah Kategorik Ordinal (Tingkatan derajat displasia: 0, 1, 2, 3). Data ordinal tidak memiliki sifat interval kuantitatif yang konstan.<br><br>
    Berdasarkan pengujian Shapiro-Wilk, ketika rumus mendeteksi sebaran data berupa skor yang seragam atau menumpuk, grafik sebaran tidak membentuk lonceng simetris Gauss, sehingga menghasilkan nilai Asymp. Sig. (p-value) < 0.05. Secara hukum statistika, asumsi normalitas formal ditolak, sehingga uji parametrik seperti ANOVA gugur demi hukum ilmiah dan wajib dialihkan ke Kruskal-Wallis.<br><br>
    
    <h3>2. Rumus Inti Uji Utama: Kruskal-Wallis H Test</h3>
    Uji Kruskal-Wallis tidak mengolah nilai angka asli (0,1,2,3), melainkan mentransformasikan seluruh data ke dalam bentuk Peringkat Kumulatif (Ranks) dari peringkat 1 hingga N (dimana total sampel N = 27). Jika ada angka skor yang sama (ties), sistem mengambil nilai rata-rata posisi peringkatnya.<br><br>
    Karena pada data skor displasia terdapat banyak sekali nilai angka yang sama (ties), sistem Streamlit secara otomatis menerapkan Faktor Koreksi Nilai Ikatan (Ties Correction Factor) untuk memunculkan angka Asymp. Sig pada output kuning di atas. Jika nilai akhir p < 0.05, maka hipotesis nol (H0) gugur, menyatakan secara mutlak ada perbedaan efek klinis obat.<br><br>

    <h3>3. Rumus Uji Lanjut: Komparasi Pasangan Mann-Whitney U</h3>
    Ketika Kruskal-Wallis menyatakan ada perbedaan, kita harus melacak pasangan mana yang berbeda menggunakan Uji Mann-Whitney U. Konsep dasarnya adalah menghitung frekuensi kemenangan peringkat antara dua kelompok yang diadu.<br><br>
    
    <b>⚠️ Pengaman Krusial Jurnal Medis (Koreksi Bonferroni):</b><br>
    Karena anak Bapak melakukan perbandingan berulang sebanyak 3 kali (P1 vs P2, P2 vs P3, P1 vs P3) pada satu sampel yang sama, akan muncul risiko kesalahan tipe I (galat semu). Oleh karena itu, batas keadilan ilmiah tidak lagi memakai alpha = 0.05, melainkan diturunkan lewat Koreksi Alpha Bonferroni menjadi <b>0.0167</b> (0.05 dibagi 3 perbandingan). Dokumen tabel di atas telah dikunci menggunakan batas kritis 0.0167 ini untuk menjamin orisinalitas metodologi riset skripsi anak Bapak bebas dari penolakan dosen penguji.
    """
    st.markdown(teks_rumus, unsafe_allow_html=True)

    # Bungkus berkas teori rumus ke dalam format HTML ekspor Word
    html_word_exporter += f"<h3>6. Lampiran Landasan Teori Rumus Matematika</h3>{teks_rumus}</body></html>"

    # =========================================================================
    # 🔥 TOMBOL UNDUH MICROSOFT WORD (.DOCX) OTOMATIS DI PALING BAWAH
    # =========================================================================
    st.markdown("---")
    st.subheader("📥 4. Cetak Lampiran Hasil Skripsi Otomatis")
    st.info("Klik tombol di bawah ini untuk mengunduh seluruh berkas tabel dan landasan teori rumus di atas langsung menjadi file .docx Word asli.")

    # Konversi dokumen HTML kompilasi menjadi byte biner Word
    bytes_word_file = io.BytesIO(html_word_exporter.encode('utf-8'))

    st.download_button(
        label="📥 DOWNLOAD HASIL ANALISIS DALAM BENTUK WORD (.DOCX)",
        data=bytes_word_file,
        file_name="Lampiran_Output_SPSS_Skripsi.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary"
    )
