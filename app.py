import flet as ft
import requests
from datetime import datetime
import threading

API_URL = "https://script.google.com/macros/s/AKfycbyVFXZf4SGZ1McuyEvWXGGlKMWMYgG0cGU5LwcY2i7GAbaRl0ls5Mbda6AxndtbN1F94A/exec"
TIMEOUT_SECONDS = 10

def format_rupiah(angka):
    try:
        angka = float(angka)
        return f"Rp {angka:,.0f}".replace(",", ".")
    except:
        return "Rp 0"

def main(page: ft.Page):
    page.title = "SKY HOME"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.theme = ft.Theme(use_material3=True, color_scheme_seed="blue")
    page.padding = 0
    
    # State variables
    transaksi_data = []
    
    # UI Elements - Navigation
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
                selected_icon=ft.icons.ACCOUNT_BALANCE_WALLET,
                label="Keuangan",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.INVENTORY_2_OUTLINED,
                selected_icon=ft.icons.INVENTORY_2,
                label="Stok Barang",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.NOTES_OUTLINED,
                selected_icon=ft.icons.NOTES,
                label="Catatan",
            ),
        ],
        on_change=lambda e: ubah_halaman(e.control.selected_index),
    )

    # UI Elements - Keuangan
    pemasukan_text = ft.Text("Rp 0", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN)
    pengeluaran_text = ft.Text("Rp 0", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.RED)
    saldo_text = ft.Text("Rp 0", size=28, weight=ft.FontWeight.W_900, color=ft.colors.BLUE)
    
    jenis_dropdown = ft.Dropdown(
        label="Jenis Transaksi",
        options=[
            ft.dropdown.Option("Pemasukan"),
            ft.dropdown.Option("Pengeluaran"),
        ],
        value="Pemasukan",
        width=200,
    )
    nominal_input = ft.TextField(label="Nominal (Rp)", keyboard_type=ft.KeyboardType.NUMBER, width=300)
    keterangan_input = ft.TextField(label="Keterangan", width=300)
    
    tabel_riwayat = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Tanggal")),
            ft.DataColumn(ft.Text("Jenis")),
            ft.DataColumn(ft.Text("Nominal")),
            ft.DataColumn(ft.Text("Keterangan")),
        ],
        rows=[],
    )
    
    loading_ring = ft.ProgressRing(visible=False)
    
    # Helper Functions
    def muat_data_api():
        try:
            response = requests.get(API_URL, timeout=TIMEOUT_SECONDS)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    return data
        except Exception as e:
            print(f"Error fetching data: {e}")
        return []

    def update_dashboard():
        nonlocal transaksi_data
        loading_ring.visible = True
        page.update()
        
        # Fetch data in background
        def fetch_task():
            nonlocal transaksi_data
            transaksi_data = muat_data_api()
            
            # Hitung ringkasan
            total_masuk = sum(float(item.get("Nominal", 0)) for item in transaksi_data if item.get("Jenis") == "Pemasukan")
            total_keluar = sum(float(item.get("Nominal", 0)) for item in transaksi_data if item.get("Jenis") == "Pengeluaran")
            sisa_saldo = total_masuk - total_keluar
            
            pemasukan_text.value = format_rupiah(total_masuk)
            pengeluaran_text.value = format_rupiah(total_keluar)
            saldo_text.value = format_rupiah(sisa_saldo)
            
            # Update tabel
            tabel_riwayat.rows.clear()
            # Tampilkan maksimal 50 transaksi terbaru
            for item in list(reversed(transaksi_data))[:50]:
                tabel_riwayat.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(item.get("Tanggal", ""))),
                            ft.DataCell(
                                ft.Text(
                                    item.get("Jenis", ""),
                                    color=ft.colors.GREEN if item.get("Jenis") == "Pemasukan" else ft.colors.RED
                                )
                            ),
                            ft.DataCell(ft.Text(format_rupiah(item.get("Nominal", 0)))),
                            ft.DataCell(ft.Text(item.get("Keterangan", ""))),
                        ]
                    )
                )
            
            loading_ring.visible = False
            page.update()
            
        threading.Thread(target=fetch_task).start()

    def simpan_transaksi(e):
        if not nominal_input.value:
            page.snack_bar = ft.SnackBar(ft.Text("Nominal harus diisi!"), bgcolor=ft.colors.ERROR)
            page.snack_bar.open = True
            page.update()
            return
            
        try:
            nominal = float(nominal_input.value)
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("Nominal harus berupa angka!"), bgcolor=ft.colors.ERROR)
            page.snack_bar.open = True
            page.update()
            return

        jenis = jenis_dropdown.value
        keterangan = keterangan_input.value
        tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        payload = {
            "Tanggal": tanggal,
            "Jenis": jenis,
            "Nominal": nominal,
            "Keterangan": keterangan
        }
        
        loading_ring.visible = True
        page.update()
        
        def post_task():
            try:
                response = requests.post(API_URL, json=payload, timeout=TIMEOUT_SECONDS)
                if response.status_code == 200:
                    page.snack_bar = ft.SnackBar(ft.Text("Transaksi berhasil disimpan!"), bgcolor=ft.colors.GREEN)
                    page.snack_bar.open = True
                    # Clear inputs
                    nominal_input.value = ""
                    keterangan_input.value = ""
                    # Refresh data
                    update_dashboard()
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("Gagal menyimpan transaksi."), bgcolor=ft.colors.ERROR)
                    page.snack_bar.open = True
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor=ft.colors.ERROR)
                page.snack_bar.open = True
            finally:
                loading_ring.visible = False
                page.update()

        threading.Thread(target=post_task).start()

    simpan_btn = ft.ElevatedButton("Simpan Transaksi", icon=ft.icons.SAVE, on_click=simpan_transaksi, style=ft.ButtonStyle(bgcolor=ft.colors.BLUE, color=ft.colors.WHITE))

    # Layout Sections
    header_section = ft.Container(
        content=ft.Row([
            ft.Icon(ft.icons.HOME_ROUNDED, size=40, color=ft.colors.BLUE),
            ft.Text("SKY HOME Dashboard", size=28, weight=ft.FontWeight.BOLD),
            loading_ring,
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=20,
    )

    summary_section = ft.Row([
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Total Pemasukan", size=14, color=ft.colors.OUTLINE),
                    pemasukan_text,
                ]),
                padding=20,
                width=250,
            ),
            elevation=4,
        ),
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Total Pengeluaran", size=14, color=ft.colors.OUTLINE),
                    pengeluaran_text,
                ]),
                padding=20,
                width=250,
            ),
            elevation=4,
        ),
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Sisa Saldo", size=16, color=ft.colors.OUTLINE),
                    saldo_text,
                ]),
                padding=20,
                width=300,
                bgcolor=ft.colors.SURFACE_VARIANT,
            ),
            elevation=6,
        ),
    ], wrap=True)

    form_section = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Input Transaksi Baru", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([jenis_dropdown, nominal_input, keterangan_input], wrap=True),
                simpan_btn,
            ]),
            padding=20,
        ),
        elevation=2,
        margin=ft.margin.only(top=20, bottom=20)
    )

    history_section = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Riwayat Transaksi (50 Terbaru)", size=20, weight=ft.FontWeight.BOLD),
                ft.ListView([tabel_riwayat], height=400, expand=1),
            ]),
            padding=20,
        ),
        elevation=2,
        expand=True
    )

    halaman_keuangan = ft.Column([
        header_section,
        summary_section,
        form_section,
        history_section,
    ], scroll=ft.ScrollMode.AUTO, expand=True, padding=20)
    
    halaman_stok = ft.Container(
        content=ft.Text("Modul Stok Barang Belum Tersedia", size=24, color=ft.colors.OUTLINE),
        alignment=ft.alignment.center,
        expand=True
    )
    
    halaman_catatan = ft.Container(
        content=ft.Text("Modul Catatan Belum Tersedia", size=24, color=ft.colors.OUTLINE),
        alignment=ft.alignment.center,
        expand=True
    )

    konten_utama = ft.AnimatedSwitcher(
        content=halaman_keuangan,
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=500,
        expand=True
    )

    def ubah_halaman(index):
        if index == 0:
            konten_utama.content = halaman_keuangan
        elif index == 1:
            konten_utama.content = halaman_stok
        elif index == 2:
            konten_utama.content = halaman_catatan
        page.update()

    # Main Layout
    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                konten_utama,
            ],
            expand=True,
        )
    )
    
    # Inisialisasi data
    update_dashboard()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8501, host="0.0.0.0")
