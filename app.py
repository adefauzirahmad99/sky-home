import streamlit as st
from streamlit_navigation_bar import st_navbar
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="SKY HOME", page_icon="🏠", layout="wide")

# --- KONEKSI DATABASE GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Fungsi untuk mengambil data terbaru dari Google Sheets
def ambil_data():
    try:
        # Membaca data dari sheet bernama 'Keuangan'
        return conn.read(worksheet="Keuangan", ttl="0m")
    except:
        # Jika sheet masih kosong / baru dibuat
        return pd.DataFrame(columns=["Tanggal", "Jenis", "Nominal", "Keterangan"])

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏠 SKY HOME")
    st.write("Sistem Manajemen Rumah")
    st.markdown("---")
    st.caption("Status: Terhubung ke Google Sheets 🟢")

# --- MENU NAVIGASI ---
styles = {
    "nav": {"background-color": "#f0f2f6", "justify-content": "center"},
    "span": {"color": "#31333F", "padding": "14px"},
    "active": {"background-color": "#ff4b4b", "color": "white", "font-weight": "bold"}
}
menu_pilihan = st_navbar(["💰 Keuangan", "📦 Stok Barang", "📋 Catatan"], styles=styles)

# --- LOGIKA MENU ---
if menu_pilihan == "💰 Keuangan":
    st.header("🪙 Menu Keuangan - SKY HOME")
    
    # 1. Ambil data saat ini dari Google Sheets
    df_keuangan = ambil_data()
    
    # Hitung total Pemasukan & Pengeluaran secara otomatis dari Google Sheets
    total_masuk = 0
    total_keluar = 0
    
    if not df_keuangan.empty:
        # Pastikan kolom Nominal dibaca sebagai angka
        df_keuangan["Nominal"] = pd.to_numeric(df_keuangan["Nominal"], errors='coerce').fillna(0)
        total_masuk = df_keuangan[df_keuangan["Jenis"] == "Pemasukan"]["Nominal"].sum()
        total_keluar = df_keuangan[df_keuangan["Jenis"] == "Pengeluaran"]["Nominal"].sum()
    
    saldo_akhir = total_masuk - total_keluar
    
    # Tampilkan Ringkasan Berdasarkan Data Google Sheets
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pemasukan", f"Rp {total_masuk:,.0f}")
    col2.metric("Total Pengeluaran", f"Rp {total_keluar:,.0f}")
    col3.metric("Sisa Saldo", f"Rp {saldo_akhir:,.0f}")
    
    st.markdown("---")
    
    # 2. Form Input Data Baru
    col_form, col_tabel = st.columns([1, 2])
    
    with col_form:
        st.subheader("📝 Input Transaksi")
        with st.form("form_keuangan", clear_on_submit=True):
            jenis = st.selectbox("Jenis", ["Pemasukan", "Pengeluaran"])
            nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000)
            keterangan = st.text_input("Keterangan")
            submit = st.form_submit_button("Simpan Transaksi")
            
            if submit and nominal > 0:
                # Siapkan baris data baru
                data_baru = pd.DataFrame([{
                    "Tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Jenis": jenis,
                    "Nominal": nominal,
                    "Keterangan": keterangan
                }])
                
                # Gabungkan data lama dengan data baru
                df_diperbarui = pd.concat([df_keuangan, data_baru], ignore_index=True)
                
                # Kirim dan simpan kembali ke Google Sheets
                conn.update(worksheet="Keuangan", data=df_diperbarui)
                st.success(f"Berhasil menyimpan {jenis} ke Google Sheets!")
                st.rerun()

    # 3. Tampilkan Tabel Data langsung dari Google Sheets
    with col_tabel:
        st.subheader("📋 Riwayat Transaksi (Google Sheets)")
        if not df_keuangan.empty:
            # Tampilkan tabel dibalik agar data terbaru ada di paling atas
            st.dataframe(df_keuangan.iloc[::-1], use_container_width=True)
        else:
            st.info("Belum ada riwayat transaksi.")

elif menu_pilihan == "📦 Stok Barang":
    st.header("📦 Menu Stok Barang")

elif menu_pilihan == "📋 Catatan":
    st.header("📋 Menu Catatan")