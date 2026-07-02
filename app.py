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
            background-color: var(--background-color);
            background-image:
                radial-gradient(circle at top left, color-mix(in srgb, var(--primary-color) 15%, transparent), transparent 30%),
                radial-gradient(circle at top right, color-mix(in srgb, #8b5cf6 12%, transparent), transparent 35%),
                radial-gradient(circle at bottom left, color-mix(in srgb, #3b82f6 10%, transparent), transparent 40%);
            background-attachment: fixed;
        }
        [data-testid="stSidebar"] {
            background: color-mix(in srgb, var(--secondary-background-color) 60%, transparent);
            border-right: 1px solid color-mix(in srgb, var(--text-color) 8%, transparent);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stRadio label {
            color: var(--text-color);
            font-weight: 500;
        }
        [data-testid="stSidebar"] .stRadio > div {
            gap: 0.4rem;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label {
            padding: 0.5rem 0.75rem;
            border-radius: 12px;
            transition: all 0.2s ease;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: color-mix(in srgb, var(--primary-color) 10%, transparent);
            transform: translateX(4px);
        }
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        .hero-card {
            position: relative;
            overflow: hidden;
            padding: 1.5rem 1.75rem;
            border: 1px solid color-mix(in srgb, var(--text-color) 8%, transparent);
            border-radius: 28px;
            background: linear-gradient(145deg, color-mix(in srgb, var(--secondary-background-color) 85%, transparent), color-mix(in srgb, var(--background-color) 60%, transparent));
            box-shadow: 
                0 10px 30px -10px color-mix(in srgb, var(--text-color) 10%, transparent),
                inset 0 1px 0 color-mix(in srgb, #ffffff 20%, transparent);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            margin-bottom: 1.25rem;
            animation: floatUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .hero-card::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary-color), #8b5cf6, #3b82f6);
            opacity: 0.8;
        }
        .hero-kicker {
            color: var(--primary-color);
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .hero-title {
            color: var(--text-color);
            font-size: 1.75rem;
            font-weight: 800;
            line-height: 1.2;
            margin: 0;
            letter-spacing: -0.02em;
        }
        .hero-subtitle {
            color: var(--text-color);
            opacity: 0.7;
            font-size: 0.95rem;
            margin-top: 0.5rem;
            margin-bottom: 0;
            max-width: 600px;
            line-height: 1.5;
        }
        .hero-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            margin-top: 1.25rem;
        }
        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.4rem 0.85rem;
            border-radius: 999px;
            border: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent);
            background: color-mix(in srgb, var(--background-color) 50%, transparent);
            color: var(--text-color);
            font-size: 0.8rem;
            font-weight: 600;
            backdrop-filter: blur(8px);
            box-shadow: 0 2px 8px color-mix(in srgb, var(--text-color) 4%, transparent);
        }
        .hero-badge-dot {
            width: 0.5rem;
            height: 0.5rem;
            border-radius: 999px;
            background: #10b981;
            box-shadow: 0 0 0 4px color-mix(in srgb, #10b981 20%, transparent);
            animation: pulse 2s infinite;
        }
        .summary-card {
            position: relative;
            overflow: hidden;
            padding: 1.5rem;
            border-radius: 24px;
            border: 1px solid color-mix(in srgb, var(--text-color) 8%, transparent);
            background: linear-gradient(180deg, color-mix(in srgb, var(--secondary-background-color) 80%, transparent), color-mix(in srgb, var(--background-color) 60%, transparent));
            box-shadow: 
                0 12px 30px -10px color-mix(in srgb, var(--text-color) 8%, transparent),
                inset 0 1px 0 color-mix(in srgb, #ffffff 15%, transparent);
            min-height: 130px;
            margin-bottom: 1.25rem;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            animation: floatUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .summary-card::after {
            content: "";
            position: absolute;
            top: -50px;
            right: -50px;
            width: 150px;
            height: 150px;
            border-radius: 999px;
            background: color-mix(in srgb, var(--primary-color) 8%, transparent);
            filter: blur(20px);
            z-index: 0;
            transition: all 0.4s ease;
        }
        .summary-card:hover {
            transform: translateY(-6px) scale(1.02);
            box-shadow: 
                0 20px 40px -15px color-mix(in srgb, var(--text-color) 12%, transparent),
                inset 0 1px 0 color-mix(in srgb, #ffffff 25%, transparent);
            border-color: color-mix(in srgb, var(--primary-color) 30%, transparent);
        }
        .summary-card:hover::after {
            background: color-mix(in srgb, var(--primary-color) 15%, transparent);
            transform: scale(1.2);
        }
        .summary-content {
            position: relative;
            z-index: 1;
        }
        .summary-label {
            color: var(--text-color);
            opacity: 0.7;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }
        .summary-value {
            color: var(--text-color);
            font-size: 1.85rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 0;
            letter-spacing: -0.02em;
        }
        .summary-income {
            border-left: 4px solid #10b981;
        }
        .summary-expense {
            border-left: 4px solid #ef4444;
        }
        .summary-balance {
            border-left: 4px solid var(--primary-color);
        }
        .section-card {
            padding: 1.5rem;
            border-radius: 28px;
            border: 1px solid color-mix(in srgb, var(--text-color) 8%, transparent);
            background: color-mix(in srgb, var(--secondary-background-color) 70%, transparent);
            box-shadow: 
                0 15px 35px -15px color-mix(in srgb, var(--text-color) 8%, transparent),
                inset 0 1px 0 color-mix(in srgb, #ffffff 10%, transparent);
            height: 100%;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            animation: floatUp 1s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .section-title {
            color: var(--text-color);
            font-size: 1.25rem;
            font-weight: 800;
            margin-bottom: 1.25rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            letter-spacing: -0.01em;
        }
        .mobile-note {
            display: none;
            margin-bottom: 1rem;
            padding: 0.75rem 1rem;
            border-radius: 16px;
            background: color-mix(in srgb, var(--primary-color) 8%, transparent);
            border: 1px solid color-mix(in srgb, var(--primary-color) 15%, transparent);
            color: var(--primary-color);
            font-size: 0.85rem;
            font-weight: 500;
        }
        div[data-testid="stForm"] {
            border: 0;
            padding: 0;
            background: transparent;
        }
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            border-radius: 16px;
            background: color-mix(in srgb, var(--background-color) 80%, transparent);
            color: var(--text-color);
            border: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent);
            padding: 0.5rem 1rem;
            transition: all 0.2s ease;
        }
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stNumberInput"] input:focus,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px color-mix(in srgb, var(--primary-color) 20%, transparent);
            background: var(--background-color);
        }
        div[data-testid="stNumberInput"] button {
            border-radius: 12px;
            background: color-mix(in srgb, var(--text-color) 5%, transparent);
        }
        div[data-testid="stFormSubmitButton"] button {
            border-radius: 16px;
            min-height: 3.25rem;
            background: linear-gradient(135deg, var(--primary-color), #6366f1);
            color: white;
            font-weight: 700;
            font-size: 1rem;
            border: 0;
            box-shadow: 0 10px 25px -5px color-mix(in srgb, var(--primary-color) 40%, transparent);
            transition: all 0.3s ease;
            margin-top: 0.5rem;
        }
        div[data-testid="stFormSubmitButton"] button:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 30px -5px color-mix(in srgb, var(--primary-color) 50%, transparent);
            filter: brightness(1.05);
        }
        div[data-testid="stFormSubmitButton"] button:active {
            transform: translateY(1px);
        }
        div[data-testid="stDataFrame"] {
            border-radius: 20px;
            overflow: hidden;
            border: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent);
            background: color-mix(in srgb, var(--background-color) 70%, transparent);
            box-shadow: 0 4px 15px color-mix(in srgb, var(--text-color) 3%, transparent);
        }
        @keyframes floatUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 color-mix(in srgb, #10b981 40%, transparent); }
            70% { box-shadow: 0 0 0 6px color-mix(in srgb, #10b981 0%, transparent); }
            100% { box-shadow: 0 0 0 0 color-mix(in srgb, #10b981 0%, transparent); }
        }
        @media (max-width: 768px) {
            .main .block-container {
                padding-top: 1rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }
            .hero-card {
                padding: 1.25rem;
                border-radius: 24px;
            }
            .section-card {
                padding: 1.25rem;
                border-radius: 24px;
            }
            .summary-card {
                border-radius: 20px;
                padding: 1.25rem;
            }
            .hero-title {
                font-size: 1.4rem;
            }
            .summary-value {
                font-size: 1.5rem;
            }
            .hero-badges {
                gap: 0.5rem;
            }
            .hero-badge {
                width: 100%;
                justify-content: center;
                padding: 0.5rem;
            }
            .mobile-note {
                display: block;
            }
            [data-testid="stSidebar"] {
                min-width: 260px;
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
