import streamlit as st
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="SPSS Mini - Kanker Mulut Daun Afrika", layout="wide")

# =========================================================================
# 🔒 SISTEM PENGAMAN / PASSWORD LOGIN
# =========================================================================
# Ganti kata 'RahasiaSkripsi2026' di bawah ini dengan password keinginan Anda!
PASSWORD_BENAR = "N4yl@0908" 

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
            st.error("Password salah! Akses ditolak. Hubungi pemilik data.")
    st.stop() # Menghentikan aplikasi di sini jika belum login
# =========================================================================

# --- JIKA BISA MASUK, BARULAH KODE DI BAWAH INI AKAN TERBUKA ---
st.title("🔬 Aplikasi Asisten Statistik Skripsi Kedokteran Gigi")
st.write("Sistem Analisis Eksperimen In-Vivo (Hewan Coba Tikus/Mencit)")
st.markdown("---")

# FORMULIR PARAMETER UTAMA
st.sidebar.header("📋 1. Formulir Parameter")
nama_variabel = st.sidebar.text_input("Nama Variabel yang Diukur", "Diameter Kanker (mm)")
satuan = st.sidebar.text_input("Satuan Pengukuran", "mm")

jumlah_kelompok = st.sidebar.number_input("Jumlah Kelompok Perlakuan", min_value=2, max_value=10, value=5)
jumlah_ulangan = st.sidebar.number_input("Jumlah Tikus per Kelompok", min_value=2, max_value=20, value=5)

default_groups = ["Kontrol Negatif", "Ekstrak Daun Afrika Dosis 1", "Ekstrak Daun Afrika Dosis 2", "Ekstrak Daun Afrika Dosis 3", "Kontrol Positif"]
nama_kelompok = []

st.sidebar.subheader("Edit Nama Kelompok (Jika Perlu):")
for i in range(int(jumlah_kelompok)):
    def_val = default_groups[i] if i < len(default_groups) else f"Kelompok {i+1}"
    name = st.sidebar.text_input(f"Kelompok {i+1}", value=def_val)
    nama_kelompok.append(name)

# FORMULIR MATRIKS INPUT DATA
st.header("📊 2. Matriks Input Data Laboratorium")
st.write("Silakan isi angka hasil eksperimen laboratorium pada kotak matriks di bawah ini:")

matrix_data = {}
for g_name in nama_kelompok:
    matrix_data[g_name] = [0.0] * int(jumlah_ulangan)

index_tikus = [f"Tikus {i+1}" for i in range(int(jumlah_ulangan))]
df_input = pd.DataFrame(matrix_data, index=index_tikus)

edited_df = st.data_editor(df_input, num_rows="fixed", use_container_width=True)

if st.button("🚀 Jalankan Analisis Statistik (Seperti SPSS)", type="primary"):
    flat_data = []
    flat_groups = []
    for col in edited_df.columns:
        for val in edited_df[col]:
            flat_data.append(val)
            flat_groups.append(col)
            
    df_calc = pd.DataFrame({'Kelompok': flat_groups, 'Nilai': flat_data})
    
    st.markdown("---")
    st.header("📈 3. Hasil Output Statistik & Grafik")
    
    # A. Uji Normalitas
    stat_n, p_n = stats.shapiro(df_calc['Nilai'])
    st.subheader("🔹 A. Uji Normalitas (Shapiro-Wilk)")
    if p_n > 0.05:
        st.success(f"p-value = {p_n:.4f} (> 0.05). Data berdistribusi NORMAL. Syarat terpenuhi!")
    else:
        st.error(f"p-value = {p_n:.4f} (< 0.05). Data TIDAK berdistribusi normal.")
        
    # B. Uji ANOVA
    st.subheader("🔹 B. Hasil Uji ANOVA Satu Arah")
    model = ols('Nilai ~ Kelompok', data=df_calc).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    st.dataframe(anova_table)
    
    p_anova = anova_table['PR(>F)'].iloc[0]
    if p_anova < 0.05:
        st.warning(f"Nilai signifikansi p = {p_anova:.4f} (< 0.05). Kesimpulan: Ekstrak Daun Afrika berpengaruh NYATA terhadap {nama_variabel}.")
        
        # C. Uji Tukey
        st.subheader("🔹 C. Uji Lanjut Post-Hoc (Tukey HSD)")
        tukey = pairwise_tukeyhsd(endog=df_calc['Nilai'], groups=df_calc['Kelompok'], alpha=0.05)
        tukey_df = pd.DataFrame(data=tukey._results_table.data[1:], columns=tukey._results_table.data)
        st.dataframe(tukey_df)
    else:
        st.info(f"Nilai signifikansi p = {p_anova:.4f} (> 0.05). Kesimpulan: Tidak terdapat perbedaan efek yang signifikan.")

    # D. Grafik
    st.subheader("🔹 D. Grafik Visualisasi Hasil (Untuk Bab 4 Skripsi)")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x='Kelompok', y='Nilai', data=df_calc, capsize=0.1, palette='Set2', errorbar='sd', ax=ax)
    ax.set_title(f'Grafik Pengaruh Perlakuan terhadap Rata-rata {nama_variabel}', fontsize=14, pad=15)
    ax.set_ylabel(f'Rata-rata {nama_variabel} ({satuan})')
    ax.set_xlabel('Kelompok Hewan Coba')
    plt.xticks(rotation=15)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    st.pyplot(fig)
