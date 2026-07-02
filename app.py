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


def format_rupiah(angka):
    return f"Rp {angka:,.0f}"


def hitung_jumlah_transaksi(df_keuangan):
    if df_keuangan.empty:
        return 0
    return len(df_keuangan.index)


def inject_custom_css():
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(59, 130, 246, 0.10), transparent 24%),
                radial-gradient(circle at top right, rgba(14, 165, 233, 0.08), transparent 28%),
                linear-gradient(180deg, #f8fbff 0%, #f3f7fb 52%, #eef4f8 100%);
        }
        [data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.82);
            border-right: 1px solid rgba(148, 163, 184, 0.14);
            backdrop-filter: blur(10px);
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stRadio label {
            color: #334155;
        }
        [data-testid="stSidebar"] .stRadio > div {
            gap: 0.3rem;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label {
            padding: 0.35rem 0.5rem;
            border-radius: 10px;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: rgba(59, 130, 246, 0.08);
        }
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .hero-card {
            padding: 1.15rem 1.25rem;
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 24px;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(248, 250, 252, 0.92));
            box-shadow: 0 18px 42px rgba(148, 163, 184, 0.16);
            backdrop-filter: blur(10px);
            margin-bottom: 0.85rem;
            animation: floatUp 0.7s ease-out;
        }
        .hero-kicker {
            color: #2563eb;
            font-size: 0.86rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }
        .hero-title {
            color: #0f172a;
            font-size: 1.45rem;
            font-weight: 800;
            line-height: 1.15;
            margin: 0;
        }
        .hero-subtitle {
            color: #cbd5e1;
            font-size: 0.9rem;
            margin-top: 0.45rem;
            margin-bottom: 0;
        }
        .hero-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            margin-top: 0.8rem;
        }
        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.42rem 0.72rem;
            border-radius: 999px;
            border: 1px solid rgba(148, 163, 184, 0.18);
            background: #ffffff;
            color: #334155;
            font-size: 0.78rem;
            font-weight: 600;
        }
        .hero-badge-dot {
            width: 0.55rem;
            height: 0.55rem;
            border-radius: 999px;
            background: #22c55e;
            box-shadow: 0 0 0 6px rgba(34, 197, 94, 0.14);
        }
        .summary-card {
            position: relative;
            overflow: hidden;
            padding: 1.2rem;
            border-radius: 22px;
            border: 1px solid rgba(148, 163, 184, 0.15);
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(248, 250, 252, 0.92));
            box-shadow: 0 16px 34px rgba(148, 163, 184, 0.14);
            min-height: 122px;
            margin-bottom: 0.85rem;
            animation: floatUp 0.85s ease-out;
            transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
        }
        .summary-card::after {
            content: "";
            position: absolute;
            inset: auto -20px -36px auto;
            width: 110px;
            height: 110px;
            border-radius: 999px;
            background: rgba(59, 130, 246, 0.10);
            filter: blur(2px);
        }
        .summary-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 20px 40px rgba(148, 163, 184, 0.18);
        }
        .summary-label {
            color: #64748b;
            font-size: 0.82rem;
            margin-bottom: 0.45rem;
        }
        .summary-value {
            color: #0f172a;
            font-size: 1.65rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 0.2rem;
        }
        .summary-income {
            border-color: rgba(34, 197, 94, 0.28);
        }
        .summary-expense {
            border-color: rgba(248, 113, 113, 0.28);
        }
        .summary-balance {
            border-color: rgba(56, 189, 248, 0.3);
        }
        .section-card {
            padding: 1rem;
            border-radius: 24px;
            border: 1px solid rgba(148, 163, 184, 0.16);
            background: rgba(255, 255, 255, 0.92);
            box-shadow: 0 14px 34px rgba(148, 163, 184, 0.12);
            height: 100%;
            animation: floatUp 1s ease-out;
        }
        .section-title {
            color: #0f172a;
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.8rem;
        }
        .mobile-note {
            display: none;
            margin-bottom: 0.7rem;
            padding: 0.6rem 0.8rem;
            border-radius: 14px;
            background: rgba(59, 130, 246, 0.08);
            border: 1px solid rgba(59, 130, 246, 0.12);
            color: #2563eb;
            font-size: 0.8rem;
        }
        div[data-testid="stForm"] {
            border: 0;
            padding: 0;
            background: transparent;
        }
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            border-radius: 14px;
            background: #ffffff;
        }
        div[data-testid="stNumberInput"] button,
        div[data-testid="stFormSubmitButton"] button {
            border-radius: 14px;
        }
        div[data-testid="stFormSubmitButton"] button {
            min-height: 3rem;
            background: linear-gradient(135deg, #38bdf8, #8b5cf6);
            color: white;
            font-weight: 700;
            border: 0;
            box-shadow: 0 14px 30px rgba(56, 189, 248, 0.28);
        }
        div[data-testid="stFormSubmitButton"] button:hover {
            background: linear-gradient(135deg, #0ea5e9, #7c3aed);
        }
        div[data-testid="stDataFrame"] {
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid rgba(148, 163, 184, 0.16);
            background: white;
        }
        @keyframes floatUp {
            from {
                opacity: 0;
                transform: translateY(12px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        @media (max-width: 768px) {
            .main .block-container {
                padding-top: 1rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }
            .hero-card,
            .section-card,
            .summary-card {
                border-radius: 18px;
            }
            .hero-title {
                font-size: 1.2rem;
            }
            .summary-value {
                font-size: 1.35rem;
            }
            .hero-badges {
                gap: 0.45rem;
            }
            .hero-badge {
                width: 100%;
                justify-content: center;
            }
            .mobile-note {
                display: block;
            }
            [data-testid="stSidebar"] {
                min-width: 240px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero_section(jumlah_transaksi):
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-kicker">SKY HOME</div>
            <h1 class="hero-title">Dashboard Keuangan Rumah</h1>
            <div class="hero-badges">
                <div class="hero-badge"><span class="hero-badge-dot"></span>Online</div>
                <div class="hero-badge">📊 {jumlah_transaksi} transaksi</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title):
    st.markdown(
        f"""
        <div class="section-title">{title}</div>
        """,
        unsafe_allow_html=True,
    )


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
    cards = [
        (col1, "summary-card summary-income", "Total Pemasukan", format_rupiah(total_masuk)),
        (col2, "summary-card summary-expense", "Total Pengeluaran", format_rupiah(total_keluar)),
        (col3, "summary-card summary-balance", "Sisa Saldo", format_rupiah(saldo_akhir)),
    ]

    for column, card_class, label, value in cards:
        column.markdown(
            f"""
            <div class="{card_class}">
                <div class="summary-label">{label}</div>
                <div class="summary-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_form_transaksi():
    st.markdown('<div class="mobile-note">Mode mobile aktif.</div>', unsafe_allow_html=True)
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

    st.markdown('<div class="mobile-note">Tampilan ringkas untuk mobile.</div>', unsafe_allow_html=True)
    df_tampil = df_keuangan.iloc[::-1].copy()
    if "Nominal" in df_tampil.columns:
        df_tampil["Nominal"] = pd.to_numeric(df_tampil["Nominal"], errors="coerce").fillna(0)
        df_tampil["Nominal"] = df_tampil["Nominal"].map(format_rupiah)
    st.dataframe(df_tampil, use_container_width=True, hide_index=True)


inject_custom_css()

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏠 SKY HOME")
    st.caption("Sistem Manajemen Rumah")
    menu_pilihan = st.radio("Navigasi", ["💰 Keuangan", "📦 Stok Barang", "📋 Catatan"])

if menu_pilihan == "💰 Keuangan":
    with st.spinner("Memuat data keuangan..."):
        df_keuangan = ambil_data()
    jumlah_transaksi = hitung_jumlah_transaksi(df_keuangan)
    render_hero_section(jumlah_transaksi)
    total_masuk, total_keluar, saldo_akhir = hitung_ringkasan(df_keuangan)
    render_ringkasan(total_masuk, total_keluar, saldo_akhir)

    col_form, col_tabel = st.columns([1, 2])

    with col_form:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        render_section_header("📝 Input Transaksi")
        render_form_transaksi()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_tabel:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        render_section_header("📋 Riwayat Transaksi")
        render_tabel_transaksi(df_keuangan)
        st.markdown('</div>', unsafe_allow_html=True)

elif menu_pilihan == "📦 Stok Barang":
    render_hero_section(0)
    st.header("📦 Menu Stok Barang")
    st.info("Menu stok barang siap dikembangkan.")

elif menu_pilihan == "📋 Catatan":
    render_hero_section(0)
    st.header("📋 Menu Catatan")
    st.info("Menu catatan siap dikembangkan.")
