import streamlit as st
from streamlit_navigation_bar import st_navbar
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="SKY HOME", page_icon="🏠", layout="wide")

# 🔗 URL API Web App Google Apps Script Anda
API_URL = "https://script.google.com/macros/s/AKfycbyVFXZf4SGZ1McuyEvWXGGlKMWMYgG0cGU5LwcY2i7GAbaRl0ls5Mbda6AxndtbN1F94A/exec"

# Fungsi mengambil data dari Google Sheets
def ambil_data():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data)
    except:
        pass
    return pd.DataFrame(columns=["Tanggal", "Jenis", "Nominal", "Keterangan"])

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏠 SKY HOME")
    st.write("Sistem Manajemen Rumah")
    st.markdown("---")
    st.caption("Status: Terhubung via Web App API 🟢")

# --- MENU NAVIGASI ---
styles = {
    "nav": {"background-color": "#f0f2f6", "justify-content": "center"},
    "span": {"color": "#31333F", "padding": "14px"},
    "active": {"background-color": "#ff4b4b", "color": "white", "font-weight": "bold"}
}
menu_pilihan = st_navbar(["💰 Keuangan", "📦 Stok Barang", "📋 Catatan"], styles=styles)

if menu_pilihan == "💰 Keuangan":
    st.header("🪙 Menu Keuangan - SKY HOME")
    
    df_keuangan = ambil_data()
    total_masuk = 0
    total_keluar = 0
    
    if not df_keuangan.empty:
        df_keuangan["Nominal"] = pd.to_numeric(df_keuangan["Nominal"], errors='coerce').fillna(0)
        total_masuk = df_keuangan[df_keuangan["Jenis"] == "Pemasukan"]["Nominal"].sum()
        total_keluar = df_keuangan[df_keuangan["Jenis"] == "Pengeluaran"]["Nominal"].sum()
    
    saldo_akhir = total_masuk - total_keluar
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pemasukan", f"Rp {total_masuk:,.0f}")
    col2.metric("Total Pengeluaran", f"Rp {total_keluar:,.0f}")
    col3.metric("Sisa Saldo", f"Rp {saldo_akhir:,.0f}")
    
    st.markdown("---")
    col_form, col_tabel = st.columns([1, 2])
    
    with col_form:
        st.subheader("📝 Input Transaksi")
        with st.form("form_keuangan", clear_on_submit=True):
            jenis = st.selectbox("Jenis", ["Pemasukan", "Pengeluaran"])
            nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000)
            keterangan = st.text_input("Keterangan")
            submit = st.form_submit_button("Simpan Transaksi")
            
            if submit and nominal > 0:
                payload = {
                    "tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "jenis": jenis,
                    "nominal": nominal,
                    "keterangan": keterangan
                }
                # Kirim data ke Google Sheets via Apps Script
                res = requests.post(API_URL, json=payload)
                if res.status_code == 200:
                    st.success("Berhasil menyimpan data!")
                    st.rerun()
                else:
                    st.error("Gagal mengirim data ke server.")

    with col_tabel:
        st.subheader("📋 Riwayat Transaksi")
        if not df_keuangan.empty:
            # Menampilkan data dari yang paling baru di atas
            st.dataframe(df_keuangan.iloc[::-1], use_container_width=True)
        else:
            st.info("Belum ada riwayat transaksi.")