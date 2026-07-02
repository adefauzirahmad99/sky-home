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
                radial-gradient(circle at top left, rgba(56, 189, 248, 0.16), transparent 24%),
                radial-gradient(circle at top right, rgba(168, 85, 247, 0.14), transparent 28%),
                linear-gradient(180deg, #0b1020 0%, #111827 52%, #0f172a 100%);
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(17, 24, 39, 0.96));
            border-right: 1px solid rgba(148, 163, 184, 0.16);
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stRadio label {
            color: #e5eefb;
        }
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .hero-card {
            padding: 1.4rem 1.5rem;
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 24px;
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.86), rgba(30, 41, 59, 0.72));
            box-shadow: 0 24px 60px rgba(15, 23, 42, 0.28);
            backdrop-filter: blur(10px);
            margin-bottom: 1rem;
            animation: floatUp 0.7s ease-out;
        }
        .hero-kicker {
            color: #38bdf8;
            font-size: 0.86rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }
        .hero-title {
            color: #f8fafc;
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.15;
            margin: 0;
        }
        .hero-subtitle {
            color: #cbd5e1;
            font-size: 0.98rem;
            margin-top: 0.65rem;
            margin-bottom: 0;
        }
        .hero-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            margin-top: 1rem;
        }
        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.5rem 0.8rem;
            border-radius: 999px;
            border: 1px solid rgba(148, 163, 184, 0.18);
            background: rgba(15, 23, 42, 0.72);
            color: #e2e8f0;
            font-size: 0.85rem;
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
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.6));
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.22);
            min-height: 140px;
            margin-bottom: 1rem;
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
            background: rgba(56, 189, 248, 0.14);
            filter: blur(2px);
        }
        .summary-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 24px 50px rgba(15, 23, 42, 0.28);
        }
        .summary-label {
            color: #cbd5e1;
            font-size: 0.9rem;
            margin-bottom: 0.7rem;
        }
        .summary-value {
            color: #f8fafc;
            font-size: 1.85rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 0.5rem;
        }
        .summary-foot {
            color: #94a3b8;
            font-size: 0.86rem;
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
            padding: 1.15rem;
            border-radius: 24px;
            border: 1px solid rgba(148, 163, 184, 0.16);
            background: rgba(15, 23, 42, 0.72);
            box-shadow: 0 18px 40px rgba(15, 23, 42, 0.18);
            height: 100%;
            animation: floatUp 1s ease-out;
        }
        .section-title {
            color: #f8fafc;
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }
        .section-subtitle {
            color: #94a3b8;
            font-size: 0.92rem;
            margin-bottom: 1rem;
        }
        .mobile-note {
            display: none;
            margin-bottom: 0.85rem;
            padding: 0.75rem 0.9rem;
            border-radius: 14px;
            background: rgba(56, 189, 248, 0.14);
            border: 1px solid rgba(56, 189, 248, 0.2);
            color: #dbeafe;
            font-size: 0.85rem;
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
            background: rgba(15, 23, 42, 0.92);
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
                font-size: 1.55rem;
            }
            .summary-value {
                font-size: 1.5rem;
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
            <div class="hero-kicker">Smart Home Finance Dashboard</div>
            <h1 class="hero-title">SKY HOME tampil lebih modern, rapi, dan nyaman di desktop maupun HP</h1>
            <p class="hero-subtitle">Kelola pemasukan, pengeluaran, dan pantau saldo rumah tangga dari satu dashboard yang responsif.</p>
            <div class="hero-badges">
                <div class="hero-badge"><span class="hero-badge-dot"></span>API aktif dan siap sinkron</div>
                <div class="hero-badge">📊 {jumlah_transaksi} transaksi tercatat</div>
                <div class="hero-badge">📱 Optimal untuk layar mobile</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title, subtitle):
    st.markdown(
        f"""
        <div class="section-title">{title}</div>
        <div class="section-subtitle">{subtitle}</div>
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
        (col1, "summary-card summary-income", "Total Pemasukan", format_rupiah(total_masuk), "Arus kas masuk rumah tangga"),
        (col2, "summary-card summary-expense", "Total Pengeluaran", format_rupiah(total_keluar), "Belanja dan kebutuhan rutin"),
        (col3, "summary-card summary-balance", "Sisa Saldo", format_rupiah(saldo_akhir), "Posisi saldo yang tersedia saat ini"),
    ]

    for column, card_class, label, value, foot in cards:
        column.markdown(
            f"""
            <div class="{card_class}">
                <div class="summary-label">{label}</div>
                <div class="summary-value">{value}</div>
                <div class="summary-foot">{foot}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_form_transaksi():
    st.markdown('<div class="mobile-note">Mode mobile aktif. Form dibuat lebih ringkas agar input nominal dan keterangan tetap nyaman di layar kecil.</div>', unsafe_allow_html=True)
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

    st.markdown('<div class="mobile-note">Riwayat transaksi dibuat fleksibel. Di HP, fokus utama ada pada nominal dan keterangan agar lebih mudah dipantau.</div>', unsafe_allow_html=True)
    df_tampil = df_keuangan.iloc[::-1].copy()
    if "Nominal" in df_tampil.columns:
        df_tampil["Nominal"] = pd.to_numeric(df_tampil["Nominal"], errors="coerce").fillna(0)
        df_tampil["Nominal"] = df_tampil["Nominal"].map(format_rupiah)
    st.dataframe(df_tampil, use_container_width=True, hide_index=True)


inject_custom_css()

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏠 SKY HOME")
    st.write("Sistem Manajemen Rumah")
    st.markdown("---")
    st.caption("Status: Terhubung via Web App API 🟢")
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
        render_section_header("📝 Input Transaksi", "Tambah transaksi baru dengan cepat dari desktop maupun layar HP.")
        render_form_transaksi()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_tabel:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        render_section_header("📋 Riwayat Transaksi", "Pantau histori transaksi terbaru dengan tampilan yang lebih bersih.")
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
