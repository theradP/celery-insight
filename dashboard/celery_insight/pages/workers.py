import reflex as rx
from celery_insight.state import AppState
from celery_insight.template import page_shell, BG_PRIMARY, BG_CARD, BG_SECONDARY, BORDER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED, ACCENT_AMBER


def _status_badge(status: str) -> rx.Component:
    return rx.match(
        status,
        ("online",  rx.box(
            rx.hstack(
                rx.box(width="5px", height="5px", border_radius="50%", background=ACCENT_GREEN, flex_shrink="0"),
                rx.text(status, size="1", weight="bold", color=ACCENT_GREEN, text_transform="uppercase", letter_spacing="0.04em"),
                spacing="1", align="center",
            ),
            background="rgba(63,185,80,0.1)", border="1px solid rgba(63,185,80,0.25)",
            border_radius="4px", padding="0.15rem 0.45rem", display="inline-flex",
        )),
        ("offline", rx.box(
            rx.hstack(
                rx.box(width="5px", height="5px", border_radius="50%", background=ACCENT_RED, flex_shrink="0"),
                rx.text(status, size="1", weight="bold", color=ACCENT_RED, text_transform="uppercase", letter_spacing="0.04em"),
                spacing="1", align="center",
            ),
            background="rgba(248,81,73,0.1)", border="1px solid rgba(248,81,73,0.25)",
            border_radius="4px", padding="0.15rem 0.45rem", display="inline-flex",
        )),
        rx.box(
            rx.text(status, size="1", color=TEXT_MUTED),
            background="rgba(72,79,88,0.1)", border=f"1px solid {BORDER}",
            border_radius="4px", padding="0.15rem 0.45rem",
        ),
    )


def _progress_bar(value: rx.Var, from_color: str, to_color: str, label: str) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text(label, size="1", color=TEXT_MUTED),
            rx.spacer(),
            rx.text(value, size="1", color=TEXT_SECONDARY),
            width="100%",
            align="center",
        ),
        rx.box(
            rx.box(
                height="100%",
                border_radius="2px",
                background=f"linear-gradient(90deg, {from_color}, {to_color})",
                width="40%",  # static stand-in - dynamic width needs JS
                transition="width 0.5s ease",
            ),
            height="4px",
            background="rgba(48,54,61,0.8)",
            border_radius="2px",
            overflow="hidden",
            width="100%",
        ),
        spacing="1",
        width="100%",
    )


def _worker_card(worker: dict) -> rx.Component:
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.hstack(
                    rx.icon("server", size=14, color=ACCENT_BLUE),
                    rx.text(worker["hostname"], size="2", weight="bold", color=TEXT_PRIMARY),
                    spacing="2",
                    align="center",
                ),
                _status_badge(worker["status"]),
                justify="between",
                width="100%",
                align="center",
            ),
            rx.divider(color=BORDER, margin_y="0.5rem"),
            # Resource metrics
            _progress_bar(worker["cpu_usage"], ACCENT_BLUE, "#a371f7", "CPU"),
            _progress_bar(worker["memory_usage"], ACCENT_GREEN, ACCENT_BLUE, "Memory"),
            # Footer
            rx.hstack(
                rx.icon("activity", size=12, color=TEXT_MUTED),
                rx.text(worker["active_tasks"], size="1", color=TEXT_SECONDARY),
                rx.text("active tasks", size="1", color=TEXT_MUTED),
                spacing="1",
                align="center",
                margin_top="0.25rem",
            ),
            align_items="start",
            spacing="2",
            padding="1.25rem",
        ),
        background=BG_CARD,
        border=f"1px solid {BORDER}",
        border_radius="10px",
        backdrop_filter="blur(10px)",
        _hover={"border_color": "rgba(88,166,255,0.3)", "box_shadow": "0 0 20px rgba(88,166,255,0.06)"},
        transition="border-color 0.2s ease, box-shadow 0.2s ease",
    )


def _empty_state(emoji: str, title: str, subtitle: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(emoji, size="7"),
            rx.text(title, size="3", weight="bold", color=TEXT_SECONDARY),
            rx.text(subtitle, size="2", color=TEXT_MUTED, text_align="center", max_width="400px"),
            spacing="3",
            align="center",
        ),
        padding="4rem",
        text_align="center",
        background=BG_CARD,
        border=f"1px solid {BORDER}",
        border_radius="10px",
        width="100%",
    )


@rx.page(route="/workers", title="Workers — Celery Insight", on_load=AppState.fetch_workers)
def workers() -> rx.Component:
    return page_shell(
        rx.vstack(
            # Header
            rx.hstack(
                rx.vstack(
                    rx.text("Workers", size="6", weight="bold", color=TEXT_PRIMARY, letter_spacing="-0.02em"),
                    rx.text("Live worker health and resource utilization", size="2", color=TEXT_SECONDARY),
                    spacing="1",
                    align_items="start",
                ),
                rx.spacer(),
                rx.cond(
                    AppState.is_loading,
                    rx.spinner(size="2"),
                    rx.box(
                        rx.hstack(
                            rx.icon("refresh-cw", size=13, color=TEXT_MUTED),
                            rx.text("Refresh", size="1", color=TEXT_MUTED),
                            spacing="2",
                            align="center",
                        ),
                        background=BG_CARD,
                        border=f"1px solid {BORDER}",
                        border_radius="6px",
                        padding="0.375rem 0.75rem",
                        cursor="pointer",
                        on_click=AppState.fetch_workers,
                        _hover={"border_color": ACCENT_BLUE},
                        transition="border-color 0.15s ease",
                    ),
                ),
                width="100%",
                align="start",
                margin_bottom="1.5rem",
            ),

            # Workers grid
            rx.grid(
                rx.foreach(AppState.workers, _worker_card),
                columns="3",
                spacing="4",
                width="100%",
            ),

            # Empty state
            rx.cond(
                AppState.workers.length() == 0,
                _empty_state("🖥️", "No workers online", "Workers will appear here as soon as they connect and send heartbeats."),
                rx.box(),
            ),

            align_items="stretch",
            spacing="0",
            width="100%",
            max_width="1200px",
        )
    )
