import reflex as rx

# ─── Design Tokens ───────────────────────────────────────────────
BG_PRIMARY = "#0d1117"
BG_SECONDARY = "#161b22"
BG_CARD = "rgba(22, 27, 34, 0.9)"
BORDER = "#21262d"
BORDER_SUBTLE = "rgba(48, 54, 61, 0.8)"
TEXT_PRIMARY = "#e6edf3"
TEXT_SECONDARY = "#8b949e"
TEXT_MUTED = "#484f58"
ACCENT_BLUE = "#58a6ff"
ACCENT_GREEN = "#3fb950"
ACCENT_RED = "#f85149"
ACCENT_AMBER = "#d29922"
ACCENT_PURPLE = "#bc8cff"
SIDEBAR_W = "220px"

# ─── Colour maps ─────────────────────────────────────────────────
_STATE_COLORS = {
    "SUCCESS": (ACCENT_GREEN, "rgba(63,185,80,0.12)", "rgba(63,185,80,0.25)"),
    "FAILURE": (ACCENT_RED,   "rgba(248,81,73,0.12)", "rgba(248,81,73,0.25)"),
    "STARTED": (ACCENT_BLUE,  "rgba(88,166,255,0.12)","rgba(88,166,255,0.25)"),
    "RETRY":   (ACCENT_AMBER, "rgba(210,153,34,0.12)","rgba(210,153,34,0.25)"),
    "RECEIVED":(ACCENT_PURPLE,"rgba(188,140,255,0.12)","rgba(188,140,255,0.25)"),
}


def _nav_btn(label: str, icon: str, href: str) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.icon(icon, size=14, color=TEXT_SECONDARY),
            rx.text(label, size="2", color=TEXT_SECONDARY),
            spacing="2",
            align="center",
            padding="0.45rem 0.75rem",
            border_radius="6px",
            width="100%",
            _hover={
                "background": "rgba(88,166,255,0.08)",
                "color": TEXT_PRIMARY,
            },
            transition="all 0.15s ease",
        ),
        href=href,
        text_decoration="none",
        width="100%",
        display="block",
    )


def sidebar() -> rx.Component:
    return rx.box(
        # Logo
        rx.hstack(
            rx.box(
                rx.text("🌿", size="3"),
                background="linear-gradient(135deg, #388bfd, #a371f7)",
                border_radius="8px",
                width="32px",
                height="32px",
                display="flex",
                align_items="center",
                justify_content="center",
                flex_shrink="0",
            ),
            rx.vstack(
                rx.hstack(
                    rx.text("Celery", size="2", weight="bold", color=TEXT_PRIMARY),
                    rx.text("Insight", size="2", weight="bold", color=ACCENT_BLUE),
                    spacing="1",
                ),
                rx.box(
                    rx.text("LIVE", size="1", color=ACCENT_BLUE, weight="bold"),
                    background="rgba(56,139,253,0.1)",
                    border="1px solid rgba(56,139,253,0.3)",
                    border_radius="3px",
                    padding="1px 5px",
                    display="inline-block",
                ),
                spacing="1",
                align_items="start",
            ),
            align="center",
            spacing="3",
            padding="1.25rem 1rem",
            border_bottom=f"1px solid {BORDER}",
        ),
        # Nav
        rx.vstack(
            rx.text(
                "OBSERVABILITY",
                size="1",
                weight="bold",
                color=TEXT_MUTED,
                letter_spacing="0.08em",
                padding="0.75rem 0.75rem 0.25rem",
            ),
            _nav_btn("Dashboard", "layout-dashboard", "/"),
            _nav_btn("Task History", "list-todo", "/tasks"),
            _nav_btn("Workers", "server", "/workers"),
            _nav_btn("Queue Health", "layers", "/queues"),
            spacing="0",
            align_items="stretch",
            padding="0.5rem 0.5rem",
        ),
        # Status footer
        rx.box(
            rx.hstack(
                rx.box(
                    width="8px",
                    height="8px",
                    border_radius="50%",
                    background=ACCENT_GREEN,
                    box_shadow=f"0 0 6px {ACCENT_GREEN}",
                    flex_shrink="0",
                ),
                rx.text("Live monitoring", size="1", color=TEXT_MUTED),
                spacing="2",
                align="center",
            ),
            margin_top="auto",
            padding="1rem",
            border_top=f"1px solid {BORDER}",
        ),
        # Sidebar container
        position="fixed",
        top="0",
        left="0",
        width=SIDEBAR_W,
        height="100vh",
        background=BG_PRIMARY,
        border_right=f"1px solid {BORDER}",
        display="flex",
        flex_direction="column",
        z_index="100",
        overflow_y="auto",
    )


def page_shell(content: rx.Component) -> rx.Component:
    """Full page with sidebar + scrollable content area."""
    return rx.box(
        sidebar(),
        rx.box(
            content,
            margin_left=SIDEBAR_W,
            padding="1.75rem 2.25rem",
            min_height="100vh",
            background=BG_PRIMARY,
        ),
        background=BG_PRIMARY,
        min_height="100vh",
    )
