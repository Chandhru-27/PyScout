import flet as ft
from datetime import datetime
import time

# --- Color Palette & Theme ---
BACKGROUND_GRADIENT = ft.LinearGradient(
    begin=ft.alignment.top_center,
    end=ft.alignment.bottom_center,
    colors=["#1a1a2e", "#16213e", "#0f3460"]
)
GLASS_EFFECT_COLOR = ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
ACCENT_COLOR = "#e94560"
PRIMARY_TEXT = ft.Colors.WHITE
SECONDARY_TEXT = ft.Colors.WHITE70

# --- Animated Navigation Button ---
class NavButton(ft.UserControl):
    def __init__(self, text, icon_name, on_click_callback, selected=False):
        super().__init__()
        self.text = text
        self.icon_name = icon_name
        self.on_click_callback = on_click_callback
        self.selected = selected

    def build(self):
        return ft.Container(
            on_click=self.handle_click,
            on_hover=self.handle_hover,
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            border_radius=ft.border_radius.all(8),
            bgcolor=ACCENT_COLOR if self.selected else ft.Colors.TRANSPARENT,
            scale=ft.transform.Scale(1),
            animate_scale=ft.animation.Animation(300, "easeOutCubic"),
            content=ft.Row(
                spacing=20,
                controls=[
                    ft.Icon(self.icon_name, color=PRIMARY_TEXT),
                    ft.Text(self.text, color=PRIMARY_TEXT, weight=ft.FontWeight.W_600)
                ]
            )
        )
    
    def handle_hover(self, e):
        self.scale = 1.05 if e.data == "true" else 1
        self.update()

    def handle_click(self, e):
        self.on_click_callback(self)
    
    def select(self):
        self.selected = True
        self.bgcolor = ACCENT_COLOR
        self.update()

    def deselect(self):
        self.selected = False
        self.bgcolor = ft.Colors.TRANSPARENT
        self.update()

# --- Reusable View Header ---
def create_view_header(title: str):
    return ft.Column(
        spacing=2,
        controls=[
            ft.Text(title, size=32, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
            ft.Text(datetime.now().strftime("%A, %B %d, %Y"), size=16, color=SECONDARY_TEXT),
        ]
    )

# --- Dashboard View ---
class DashboardView(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.screen_time_progress = ft.ProgressBar(value=0, color=ACCENT_COLOR, bgcolor=ft.Colors.WHITE24, height=10, animate=True)
        self.break_time_progress = ft.ProgressBar(value=0, color=ACCENT_COLOR, bgcolor=ft.Colors.WHITE24, height=10, animate=True)

    def did_mount(self):
        """Animate progress bars when the view is loaded."""
        time.sleep(0.5) # small delay for visual effect
        self.screen_time_progress.value = 0.45
        self.break_time_progress.value = 0.15
        self.update()

    def build(self):
        def create_info_card(icon, title, value, expand_factor):
            return ft.Container(
                expand=expand_factor,
                padding=20,
                border_radius=15,
                gradient=ft.LinearGradient(Colors=[ft.Colors.with_opacity(0.2, ACCENT_COLOR), ft.Colors.with_opacity(0.1, ACCENT_COLOR)]),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(icon, color=ACCENT_COLOR, size=30),
                        ft.Text(title, color=SECONDARY_TEXT, size=14),
                        ft.Text(value, color=PRIMARY_TEXT, size=36, weight=ft.FontWeight.BOLD),
                    ]
                )
            )

        def create_progress_section(title, progress_bar, value_text):
            return ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(title, size=16, weight=ft.FontWeight.W_500),
                            ft.Text(value_text, size=14, color=SECONDARY_TEXT),
                        ]
                    ),
                    progress_bar,
                ]
            )

        return ft.Column(
            spacing=25,
            controls=[
                create_view_header("Dashboard"),
                ft.ResponsiveRow(
                    spacing=20,
                    controls=[
                        create_info_card(ft.Icons.TIMER_OUTLINED, "Today's Usage", "4h 32m", {"xs": 12, "md": 6}),
                        create_info_card(ft.Icons.INSIGHTS_ROUNDED, "Weekly Avg", "5h 16m", {"xs": 12, "md": 6}),
                    ]
                ),
                create_progress_section("Screen Time Progress", self.screen_time_progress, "4h 32m / 8h"),
                create_progress_section("Break Time Today", self.break_time_progress, "0h 45m / 1h"),
            ],
            expand=True
        )

# --- History View ---
class HistoryView(ft.UserControl):
    def build(self):
        history_data = [
            ("1", "2025-08-21", "4:32:15", "0:45:03"),
            ("2", "2025-08-20", "6:10:40", "1:10:00"),
            ("3", "2025-08-19", "5:21:28", "0:55:49"),
            ("4", "2025-08-18", "7:27:50", "1:30:12"),
        ]

        return ft.Column(
            spacing=20,
            controls=[
                create_view_header("Usage History"),
                ft.DataTable(
                    heading_row_color=ft.Colors.with_opacity(0.1, ACCENT_COLOR),
                    border_radius=10,
                    columns=[
                        ft.DataColumn(ft.Text("Sno", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Date", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Screen Time", weight=ft.FontWeight.BOLD), numeric=True),
                        ft.DataColumn(ft.Text("Break Time", weight=ft.FontWeight.BOLD), numeric=True),
                    ],
                    rows=[
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(item[0], color=SECONDARY_TEXT)),
                                ft.DataCell(ft.Text(item[1])),
                                ft.DataCell(ft.Text(item[2])),
                                ft.DataCell(ft.Text(item[3])),
                            ],
                            color={"hovered": ft.Colors.with_opacity(0.1, ft.Colors.WHITE)}
                        ) for item in history_data
                    ],
                )
            ],
            expand=True
        )

# --- Restricted View ---
class RestrictedView(ft.UserControl):
    def build(self):
        def create_restricted_section(title: str):
            return ft.Container(
                padding=20,
                border_radius=15,
                border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                bgcolor=GLASS_EFFECT_COLOR,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(title, size=16, weight=ft.FontWeight.W_500),
                        ft.ElevatedButton(
                            text="+ Add",
                            bgcolor=ACCENT_COLOR,
                            color=PRIMARY_TEXT,
                        )
                    ]
                )
            )

        return ft.Column(
            spacing=20,
            controls=[
                create_view_header("Restricted Apps & Domains"),
                create_restricted_section("Blocked Apps"),
                create_restricted_section("Blocked URLs"),
                create_restricted_section("Suppress Notifications"),
            ],
            expand=True
        )
        
# --- Main Application ---
def main(page: ft.Page):
    page.title = "PyScout"
    page.window_width = 1200
    page.window_height = 800
    page.window_min_width = 800
    page.window_min_height = 600
    page.fonts = {
        "Poppins": "https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap"
    }
    page.theme = ft.Theme(font_family="Poppins")
    page.padding = 0
    
    # --- Views Dictionary ---
    views = {
        "Home": DashboardView(),
        "History": HistoryView(),
        "Restricted": RestrictedView(),
    }
    
    # --- View Switching Logic ---
    def switch_view(selected_button: NavButton):
        for button in nav_buttons:
            button.deselect()
        selected_button.select()

        # Animate out
        main_content_area.opacity = 0
        main_content_area.offset = ft.transform.Offset(0, 0.1)
        page.update()
        time.sleep(0.15)
        
        main_content_area.content = views[selected_button.text]
        
        # Animate in
        main_content_area.opacity = 1
        main_content_area.offset = ft.transform.Offset(0, 0)
        page.update()

    # --- Navigation Buttons ---
    home_button = NavButton("Home", ft.Icons.HOME_ROUNDED, switch_view, selected=True)
    history_button = NavButton("History", ft.Icons.HISTORY, switch_view)
    restricted_button = NavButton("Restricted", ft.Icons.BLOCK, switch_view)
    nav_buttons = [home_button, history_button, restricted_button]

    # --- Sidebar Content ---
    sidebar_content = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Icon(ft.Icons.ANALYTICS, color=ACCENT_COLOR),
                    ft.Text("PyScout", size=24, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            ),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            *nav_buttons,
        ]
    )
    
    # --- Sidebar / Drawer ---
    sidebar = ft.Container(
        width=250,
        padding=ft.padding.symmetric(horizontal=15, vertical=20),
        border=ft.border.only(right=ft.border.BorderSide(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))),
        bgcolor=GLASS_EFFECT_COLOR,
        blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
        content=sidebar_content
    )
    
    page.drawer = ft.NavigationDrawer(
        controls=[
            ft.Container(height=12),
            sidebar_content
        ],
        bgcolor=ft.Colors.with_opacity(0.9, "#16213e")
    )
    
    def toggle_drawer(e):
        page.drawer.open = not page.drawer.open
        page.drawer.update()

    # --- Main Content Area ---
    main_content_area = ft.Container(
        content=views["Home"],
        padding=ft.padding.all(25),
        expand=True,
        opacity=1,
        offset=ft.transform.Offset(0, 0),
        animate_opacity=ft.animation.Animation(300, "ease"),
        animate_offset=ft.animation.Animation(300, "ease")
    )
    
    # --- Responsive Layout Logic ---
    def on_resize(e):
        is_small_screen = page.window_width < 850
        sidebar.visible = not is_small_screen
        page.appbar.visible = is_small_screen
        page.update()

    page.on_resize = on_resize

    # --- App Bar for Mobile ---
    page.appbar = ft.AppBar(
        leading=ft.IconButton(icon=ft.Icons.MENU, on_click=toggle_drawer),
        title=ft.Text("PyScout"),
        bgcolor=ft.Colors.with_opacity(0.8, "#16213e"),
        visible=False
    )

    # --- Final Page Layout ---
    page.add(
        ft.Container(
            gradient=BACKGROUND_GRADIENT,
            expand=True,
            content=ft.Row(
                controls=[
                    sidebar,
                    main_content_area
                ],
                expand=True,
                spacing=0
            )
        )
    )
    
    # Initial responsive check
    on_resize(None)

if __name__ == "__main__":
    ft.app(target=main)