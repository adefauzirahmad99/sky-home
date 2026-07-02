import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="SKY HOME", page_icon="🏠", layout="wide")

# 🔗 URL API Web App Google Apps Script Anda
API_URL = "https://script.google.com/macros/s/AKfycbyVFXZf4SGZ1McuyEvWXGGlKMWMYgG0cGU5LwcY2i7GAbaRl0ls5Mbda6AxndtbN1F94A/exec"

TIMEOUT_SECONDS = 10
DATA_COLUMNS = ["Tanggal", "Jenis", "Nominal", "Keterangan"]


def data_kosong():
    return pd.DataFrame(columns=DATA_COLUMNS)


def ambil_data():
    try:
        response = requests.get(API_URL, timeout=TIMEOUT_SECONDS)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return pd.DataFrame(data)
    except requests.RequestException:
        return data_kosong()
    return data_kosong()


def kirim_transaksi(payload):
    response = requests.post(API_URL, json=payload, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return response


def hitung_ringkasan(df_keuangan):
    if df_keuangan.empty:
        return 0, 0, 0

    df_keuangan = df_keuangan.copy()
    df_keuangan["Nominal"] = pd.to_numeric(df_keuangan["Nominal"], errors="coerce").fillna(0)
    total_masuk = df_keuangan[df_keuangan["Jenis"] == "Pemasukan"]["Nominal"].sum()
    total_keluar = df_keuangan[df_keuangan["Jenis"] == "Pengeluaran"]["Nominal"].sum()
    saldo_akhir = total_masuk - total_keluar
    return total_masuk, total_keluar, saldo_akhir


def render_ringkasan(total_masuk, total_keluar, saldo_akhir):
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pemasukan", f"Rp {total_masuk:,.0f}")
    col2.metric("Total Pengeluaran", f"Rp {total_keluar:,.0f}")
    col3.metric("Sisa Saldo", f"Rp {saldo_akhir:,.0f}")


def render_form_transaksi():
    with st.form("form_keuangan", clear_on_submit=True):
        jenis = st.selectbox("Jenis", ["Pemasukan", "Pengeluaran"])
        nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000)
        keterangan = st.text_input("Keterangan")
        submit = st.form_submit_button("Simpan Transaksi", use_container_width=True)

        if submit and nominal <= 0:
            st.error("Nominal harus lebih dari Rp 0.")
            return

        if submit:
            payload = {
                "tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "jenis": jenis,
                "nominal": nominal,
                "keterangan": keterangan.strip(),
            }

            try:
                with st.spinner("Menyimpan transaksi..."):
                    kirim_transaksi(payload)
                st.success("Berhasil menyimpan data!")
                st.rerun()
            except requests.RequestException:
                st.error("Tidak dapat terhubung ke server. Coba lagi beberapa saat.")


def render_tabel_transaksi(df_keuangan):
    if df_keuangan.empty:
        st.info("Belum ada riwayat transaksi.")
        return

    st.dataframe(df_keuangan.iloc[::-1], use_container_width=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏠 SKY HOME")
    st.write("Sistem Manajemen Rumah")
    st.markdown("---")
    st.caption("Status: Terhubung via Web App API 🟢")
    menu_pilihan = st.radio("Navigasi", ["💰 Keuangan", "📦 Stok Barang", "📋 Catatan"])

if menu_pilihan == "💰 Keuangan":
    st.header("🪙 Menu Keuangan - SKY HOME")

    with st.spinner("Memuat data keuangan..."):
        df_keuangan = ambil_data()
    total_masuk, total_keluar, saldo_akhir = hitung_ringkasan(df_keuangan)
    render_ringkasan(total_masuk, total_keluar, saldo_akhir)

    st.markdown("---")
    col_form, col_tabel = st.columns([1, 2])

    with col_form:
        st.subheader("📝 Input Transaksi")
        render_form_transaksi()

    with col_tabel:
        st.subheader("📋 Riwayat Transaksi")
        render_tabel_transaksi(df_keuangan)

elif menu_pilihan == "📦 Stok Barang":
    st.header("📦 Menu Stok Barang")
    st.info("Menu stok barang siap dikembangkan.")

elif menu_pilihan == "📋 Catatan":
    st.header("📋 Menu Catatan")
    st.info("Menu catatan siap dikembangkan.")
