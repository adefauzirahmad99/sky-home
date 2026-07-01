import streamlit as st
from streamlit_navigation_bar import st_navbar

st.set_page_config(page_title="SKY HOME", page_icon="🏠", layout="wide")

with st.sidebar:
    st.title("🏠 SKY HOME")
    st.write("Sistem Manajemen Rumah")
    st.markdown("---")
    st.caption("Status: Online (Render)")

styles = {
    "nav": {"background-color": "#f0f2f6", "justify-content": "center"},
    "span": {"color": "#31333F", "padding": "14px"},
    "active": {"background-color": "#ff4b4b", "color": "white", "font-weight": "bold"},
}
menu_pilihan = st_navbar(["💰 Keuangan", "📦 Stok Barang", "📋 Catatan"], styles=styles)

if menu_pilihan == "💰 Keuangan":
    st.header("🪙 Menu Keuangan - SKY HOME")
    col1, col2 = st.columns(2)
    col1.metric("Pemasukan", "Rp 0")
    col2.metric("Pengeluaran", "Rp 0")

    with st.form("form_keuangan"):
        jenis = st.selectbox("Jenis", ["Pemasukan", "Pengeluaran"])
        nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000)
        keterangan = st.text_input("Keterangan")
        if st.form_submit_button("Simpan Transaksi"):
            st.success(f"Tersimpan: {jenis} Rp {nominal:,}")

elif menu_pilihan == "📦 Stok Barang":
    st.header("📦 Menu Stok Barang")

elif menu_pilihan == "📋 Catatan":
    st.header("📋 Menu Catatan")
