import threading
from datetime import datetime

import flet as ft
import requests


API_URL = "https://script.google.com/macros/s/AKfycbyVFXZf4SGZ1McuyEvWXGGlKMWMYgG0cGU5LwcY2i7GAbaRl0ls5Mbda6AxndtbN1F94A/exec"
TIMEOUT_SECONDS = 10
MAX_ROWS = 50


def format_rupiah(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0
    return f"Rp {number:,.0f}".replace(",", ".")


def parse_nominal(value):
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = str(value).replace("Rp", "").replace(".", "").replace(",", ".").strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0


def extract_rows(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("data", "items", "rows", "result"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    return []


def normalize_item(item):
    tanggal = item.get("Tanggal") or item.get("tanggal") or "-"
    jenis = item.get("Jenis") or item.get("jenis") or "-"
    nominal = parse_nominal(item.get("Nominal") or item.get("nominal") or 0)
    keterangan = item.get("Keterangan") or item.get("keterangan") or "-"
    return {
        "Tanggal": str(tanggal),
        "Jenis": str(jenis),
        "Nominal": nominal,
        "Keterangan": str(keterangan),
    }


def fetch_transactions():
    response = requests.get(API_URL, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return [normalize_item(item) for item in extract_rows(response.json())]


def post_transaction(payload):
    response = requests.post(API_URL, json=payload, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return response


def main(page: ft.Page):
    page.title = "SKY HOME"
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.theme = ft.Theme(
        use_material3=True,
        color_scheme_seed=ft.Colors.INDIGO,
    )
    page.dark_theme = ft.Theme(
        use_material3=True,
        color_scheme_seed=ft.Colors.INDIGO,
    )
    page.bgcolor = ft.Colors.SURFACE
    page.window_min_width = 360
    page.window_min_height = 740

    state = {
        "transactions": [],
        "selected_index": 0,
        "mobile": False,
    }

    def is_mobile_width():
        return (page.width or 0) < 920

    def show_message(message, error=False):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.ERROR if error else ft.Colors.PRIMARY,
            behavior=ft.SnackBarBehavior.FLOATING,
        )
        page.snack_bar.open = True
        page.update()

    def set_loading(value):
        loading_ring.visible = value
        refresh_button.disabled = value
        submit_button.disabled = value
        page.update()

    def build_summary_card(title, amount, icon, accent, subtitle):
        return ft.Container(
            expand=True,
            border_radius=24,
            padding=20,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[
                    ft.Colors.with_opacity(0.16, accent),
                    ft.Colors.with_opacity(0.04, accent),
                ],
            ),
            border=ft.border.all(1, ft.Colors.with_opacity(0.08, accent)),
            content=ft.Column(
                spacing=14,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text(title, size=13, weight=ft.FontWeight.W_600, color=ft.Colors.GREY_700),
                                    ft.Text(subtitle, size=11, color=ft.Colors.GREY_600),
                                ],
                            ),
                            ft.Container(
                                width=42,
                                height=42,
                                border_radius=14,
                                bgcolor=ft.Colors.with_opacity(0.14, accent),
                                alignment=ft.alignment.center,
                                content=ft.Icon(icon, color=accent, size=22),
                            ),
                        ],
                    ),
                    ft.Text(amount, size=28, weight=ft.FontWeight.W_700, color=ft.Colors.ON_SURFACE),
                ],
            ),
        )

    def build_placeholder(title, description, icon):
        return ft.Container(
            expand=True,
            padding=32,
            alignment=ft.alignment.center,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
                controls=[
                    ft.Container(
                        width=72,
                        height=72,
                        border_radius=24,
                        bgcolor=ft.Colors.with_opacity(0.10, ft.Colors.PRIMARY),
                        alignment=ft.alignment.center,
                        content=ft.Icon(icon, size=36, color=ft.Colors.PRIMARY),
                    ),
                    ft.Text(title, size=24, weight=ft.FontWeight.W_700),
                    ft.Text(description, size=14, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),
                ],
            ),
        )

    def build_history_table():
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Tanggal")),
                ft.DataColumn(ft.Text("Jenis")),
                ft.DataColumn(ft.Text("Nominal"), numeric=True),
                ft.DataColumn(ft.Text("Keterangan")),
            ],
            rows=[],
            column_spacing=24,
            horizontal_margin=12,
            divider_thickness=0.4,
            heading_row_height=42,
            data_row_min_height=46,
        )

    def build_history_cards(items):
        cards = []
        for item in items:
            accent = ft.Colors.GREEN if item["Jenis"] == "Pemasukan" else ft.Colors.RED
            cards.append(
                ft.Container(
                    border_radius=20,
                    padding=16,
                    bgcolor=ft.Colors.BLUE_GREY_50,
                    border=ft.border.all(1, ft.Colors.with_opacity(0.05, accent)),
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(item["Jenis"], weight=ft.FontWeight.W_700, color=accent),
                                    ft.Text(format_rupiah(item["Nominal"]), weight=ft.FontWeight.W_700),
                                ],
                            ),
                            ft.Text(item["Keterangan"], color=ft.Colors.GREY_700),
                            ft.Text(item["Tanggal"], size=12, color=ft.Colors.GREY_600),
                        ],
                    ),
                )
            )
        return cards

    def refresh_history_view():
        latest_items = list(reversed(state["transactions"]))[:MAX_ROWS]
        if state["mobile"]:
            history_table_container.visible = False
            history_cards_column.visible = True
            history_cards_column.controls = build_history_cards(latest_items)
            if not latest_items:
                history_cards_column.controls = [
                    ft.Container(
                        padding=18,
                        border_radius=18,
                        bgcolor=ft.Colors.BLUE_GREY_50,
                        content=ft.Text("Belum ada riwayat transaksi."),
                    )
                ]
        else:
            history_table_container.visible = True
            history_cards_column.visible = False
            history_table.rows.clear()
            for item in latest_items:
                accent = ft.Colors.GREEN if item["Jenis"] == "Pemasukan" else ft.Colors.RED
                history_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(item["Tanggal"])),
                            ft.DataCell(ft.Text(item["Jenis"], color=accent)),
                            ft.DataCell(ft.Text(format_rupiah(item["Nominal"]))),
                            ft.DataCell(ft.Text(item["Keterangan"])),
                        ]
                    )
                )
        page.update()

    def refresh_summary():
        pemasukan = sum(item["Nominal"] for item in state["transactions"] if item["Jenis"] == "Pemasukan")
        pengeluaran = sum(item["Nominal"] for item in state["transactions"] if item["Jenis"] == "Pengeluaran")
        saldo = pemasukan - pengeluaran
        summary_row.controls = [
            build_summary_card("Total Pemasukan", format_rupiah(pemasukan), ft.Icons.TRENDING_UP, ft.Colors.GREEN, "Arus kas masuk"),
            build_summary_card("Total Pengeluaran", format_rupiah(pengeluaran), ft.Icons.RECEIPT_LONG, ft.Colors.RED, "Pengeluaran rumah"),
            build_summary_card("Sisa Saldo", format_rupiah(saldo), ft.Icons.ACCOUNT_BALANCE_WALLET, ft.Colors.INDIGO, "Saldo tersedia"),
        ]

    def load_transactions():
        set_loading(True)

        def worker():
            try:
                items = fetch_transactions()
                state["transactions"] = items
                refresh_summary()
                refresh_history_view()
                show_message("Data transaksi berhasil diperbarui.")
            except requests.RequestException:
                show_message("Tidak bisa mengambil data dari API.", error=True)
            finally:
                set_loading(False)

        threading.Thread(target=worker, daemon=True).start()

    def submit_transaction(_):
        nominal_raw = nominal_input.value or ""
        nominal_value = parse_nominal(nominal_raw)
        if nominal_value <= 0:
            show_message("Nominal harus lebih dari 0.", error=True)
            return

        payload = {
            "Tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Jenis": jenis_dropdown.value or "Pemasukan",
            "Nominal": nominal_value,
            "Keterangan": (keterangan_input.value or "").strip() or "-",
        }

        set_loading(True)

        def worker():
            try:
                post_transaction(payload)
                nominal_input.value = ""
                keterangan_input.value = ""
                load_transactions()
                show_message("Transaksi berhasil disimpan.")
            except requests.RequestException:
                show_message("Gagal menyimpan transaksi ke API.", error=True)
                set_loading(False)

        threading.Thread(target=worker, daemon=True).start()

    def on_resize(_):
        mobile_now = is_mobile_width()
        if state["mobile"] == mobile_now:
            return
        state["mobile"] = mobile_now
        rail.extended = not mobile_now
        rail.label_type = ft.NavigationRailLabelType.NONE if mobile_now else ft.NavigationRailLabelType.ALL
        shell.spacing = 0 if mobile_now else 8
        content_wrapper.padding = 16 if mobile_now else 24
        hero_container.padding = 20 if mobile_now else 28
        summary_row.wrap = True
        summary_row.run_spacing = 12
        form_fields.controls = [jenis_dropdown, nominal_input, keterangan_input] if mobile_now else [jenis_dropdown, nominal_input, keterangan_input]
        history_section.height = None if mobile_now else 460
        refresh_history_view()
        page.update()

    def switch_page(index):
        state["selected_index"] = index
        rail.selected_index = index
        views = [finance_view, stock_view, notes_view]
        content_switcher.content = views[index]
        page.update()

    def on_nav_change(event):
        switch_page(event.control.selected_index)

    loading_ring = ft.ProgressRing(width=18, height=18, stroke_width=2.4, visible=False)

    refresh_button = ft.IconButton(
        icon=ft.Icons.REFRESH,
        tooltip="Muat ulang data",
        on_click=lambda _: load_transactions(),
    )

    hero_container = ft.Container(
        border_radius=30,
        padding=28,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[
                ft.Colors.with_opacity(0.18, ft.Colors.INDIGO),
                ft.Colors.with_opacity(0.10, ft.Colors.BLUE),
                ft.Colors.with_opacity(0.08, ft.Colors.CYAN),
            ],
        ),
        content=ft.Column(
            spacing=18,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=6,
                            controls=[
                                ft.Text("SKY HOME", size=12, weight=ft.FontWeight.W_700, color=ft.Colors.PRIMARY),
                                ft.Text("Dashboard Keuangan Rumah", size=32, weight=ft.FontWeight.W_700),
                                ft.Text(
                                    "Pantau pemasukan, pengeluaran, dan riwayat transaksi dari satu dashboard Flet yang rapi.",
                                    size=14,
                                    color=ft.Colors.GREY_700,
                                ),
                            ],
                        ),
                        ft.Row(spacing=12, controls=[loading_ring, refresh_button]),
                    ],
                ),
                ft.Row(
                    wrap=True,
                    spacing=10,
                    controls=[
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=14, vertical=10),
                            border_radius=999,
                            bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.GREEN),
                            content=ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=14, color=ft.Colors.GREEN),
                                    ft.Text("API aktif", weight=ft.FontWeight.W_600),
                                ],
                            ),
                        ),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=14, vertical=10),
                            border_radius=999,
                            bgcolor=ft.Colors.with_opacity(0.10, ft.Colors.INDIGO),
                            content=ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(ft.Icons.STORAGE, size=14, color=ft.Colors.INDIGO),
                                    ft.Text("Sinkron real-time", weight=ft.FontWeight.W_600),
                                ],
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )

    summary_row = ft.ResponsiveRow(spacing=14, run_spacing=14)

    jenis_dropdown = ft.Dropdown(
        label="Jenis Transaksi",
        value="Pemasukan",
        expand=True,
        options=[ft.dropdown.Option("Pemasukan"), ft.dropdown.Option("Pengeluaran")],
        border_radius=16,
        filled=True,
    )
    nominal_input = ft.TextField(
        label="Nominal (Rp)",
        keyboard_type=ft.KeyboardType.NUMBER,
        expand=True,
        border_radius=16,
        filled=True,
    )
    keterangan_input = ft.TextField(
        label="Keterangan",
        expand=True,
        border_radius=16,
        filled=True,
    )

    submit_button = ft.FilledButton(
        text="Simpan Transaksi",
        icon=ft.Icons.SAVE,
        on_click=submit_transaction,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=16), padding=ft.padding.symmetric(horizontal=18, vertical=16)),
    )

    form_fields = ft.ResponsiveRow(
        run_spacing=12,
        spacing=12,
        controls=[
            ft.Container(col={"xs": 12, "md": 4}, content=jenis_dropdown),
            ft.Container(col={"xs": 12, "md": 4}, content=nominal_input),
            ft.Container(col={"xs": 12, "md": 4}, content=keterangan_input),
        ],
    )

    form_section = ft.Container(
        border_radius=26,
        padding=22,
        bgcolor=ft.Colors.WHITE,
        content=ft.Column(
            spacing=18,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text("Input Transaksi", size=22, weight=ft.FontWeight.W_700),
                                ft.Text("Tambahkan transaksi baru ke sistem rumah tangga SKY HOME.", color=ft.Colors.GREY_700),
                            ],
                        ),
                        ft.Container(
                            width=44,
                            height=44,
                            border_radius=14,
                            bgcolor=ft.Colors.with_opacity(0.10, ft.Colors.PRIMARY),
                            alignment=ft.alignment.center,
                            content=ft.Icon(ft.Icons.EDIT_NOTE, color=ft.Colors.PRIMARY),
                        ),
                    ],
                ),
                form_fields,
                ft.Row(alignment=ft.MainAxisAlignment.END, controls=[submit_button]),
            ],
        ),
    )

    history_table = build_history_table()
    history_table_container = ft.Container(
        visible=True,
        expand=True,
        content=ft.Column(scroll=ft.ScrollMode.AUTO, controls=[history_table]),
    )
    history_cards_column = ft.Column(visible=False, spacing=12)

    history_section = ft.Container(
        border_radius=26,
        padding=22,
        bgcolor=ft.Colors.WHITE,
        height=460,
        content=ft.Column(
            spacing=18,
            expand=True,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text("Riwayat Transaksi", size=22, weight=ft.FontWeight.W_700),
                                ft.Text("Menampilkan 50 transaksi terbaru dari Google Apps Script.", color=ft.Colors.GREY_700),
                            ],
                        ),
                        ft.Text("Terbaru", color=ft.Colors.PRIMARY, weight=ft.FontWeight.W_700),
                    ],
                ),
                history_table_container,
                history_cards_column,
            ],
        ),
    )

    finance_view = ft.Container(
        expand=True,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=18,
            controls=[hero_container, summary_row, form_section, history_section],
        ),
    )

    stock_view = build_placeholder("Stok Barang", "Modul stok barang disiapkan untuk tahap berikutnya.", ft.Icons.INVENTORY_2)
    notes_view = build_placeholder("Catatan", "Modul catatan akan tersedia setelah dashboard keuangan final.", ft.Icons.NOTE_ALT)

    content_switcher = ft.AnimatedSwitcher(
        expand=True,
        duration=350,
        reverse_duration=220,
        transition=ft.AnimatedSwitcherTransition.FADE,
        content=finance_view,
    )

    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=88,
        min_extended_width=220,
        extended=True,
        bgcolor=ft.Colors.BLUE_GREY_50,
        leading=ft.Container(
            padding=ft.padding.only(top=20, left=12, right=12, bottom=8),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Container(
                                width=40,
                                height=40,
                                border_radius=14,
                                bgcolor=ft.Colors.PRIMARY,
                                alignment=ft.alignment.center,
                                content=ft.Icon(ft.Icons.HOME, color=ft.Colors.WHITE),
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text("SKY HOME", weight=ft.FontWeight.W_700),
                                    ft.Text("Finance Suite", size=12, color=ft.Colors.GREY_700),
                                ],
                            ),
                        ],
                    )
                ],
            ),
        ),
        trailing=ft.Container(
            padding=16,
            content=ft.Text("Material 3", size=12, color=ft.Colors.GREY_700),
        ),
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED, selected_icon=ft.Icons.ACCOUNT_BALANCE_WALLET, label="Keuangan"),
            ft.NavigationRailDestination(icon=ft.Icons.INVENTORY_2_OUTLINED, selected_icon=ft.Icons.INVENTORY_2, label="Stok Barang"),
            ft.NavigationRailDestination(icon=ft.Icons.EDIT_NOTE_OUTLINED, selected_icon=ft.Icons.EDIT_NOTE, label="Catatan"),
        ],
        on_change=on_nav_change,
    )

    content_wrapper = ft.Container(expand=True, padding=24, content=content_switcher)

    shell = ft.Row(
        expand=True,
        spacing=8,
        controls=[
            rail,
            ft.VerticalDivider(width=1),
            content_wrapper,
        ],
    )

    page.add(shell)
    page.on_resize = on_resize
    state["mobile"] = is_mobile_width()
    on_resize(None)
    switch_page(0)
    load_transactions()


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8501, host="0.0.0.0")
