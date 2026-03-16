import reflex as rx
from celery_insight.state import AppState
from celery_insight.template import page_shell, BG_PRIMARY, BG_CARD, BG_SECONDARY, BORDER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED, ACCENT_AMBER, ACCENT_PURPLE

# ─── State badge ─────────────────────────────────────────────────
_BADGE_STYLES = {
    "SUCCESS":  (ACCENT_GREEN,  "rgba(63,185,80,0.1)",    "rgba(63,185,80,0.25)"),
    "FAILURE":  (ACCENT_RED,    "rgba(248,81,73,0.1)",    "rgba(248,81,73,0.25)"),
    "STARTED":  (ACCENT_BLUE,   "rgba(88,166,255,0.1)",   "rgba(88,166,255,0.25)"),
    "RETRY":    (ACCENT_AMBER,  "rgba(210,153,34,0.1)",   "rgba(210,153,34,0.25)"),
    "RECEIVED": (ACCENT_PURPLE, "rgba(188,140,255,0.1)",  "rgba(188,140,255,0.25)"),
}


def _badge(label: rx.Var, color: str, bg: str, border: str) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(width="5px", height="5px", border_radius="50%", background=color, flex_shrink="0"),
            rx.text(label, size="1", weight="bold", color=color, text_transform="uppercase", letter_spacing="0.04em"),
            spacing="1",
            align="center",
        ),
        background=bg,
        border=f"1px solid {border}",
        border_radius="4px",
        padding="0.15rem 0.45rem",
        display="inline-flex",
    )


def _task_state_badge(state: str) -> rx.Component:
    return rx.match(
        state,
        ("SUCCESS",  _badge(state, ACCENT_GREEN,  "rgba(63,185,80,0.1)",   "rgba(63,185,80,0.25)")),
        ("FAILURE",  _badge(state, ACCENT_RED,    "rgba(248,81,73,0.1)",   "rgba(248,81,73,0.25)")),
        ("STARTED",  _badge(state, ACCENT_BLUE,   "rgba(88,166,255,0.1)",  "rgba(88,166,255,0.25)")),
        ("RETRY",    _badge(state, ACCENT_AMBER,  "rgba(210,153,34,0.1)",  "rgba(210,153,34,0.25)")),
        ("RECEIVED", _badge(state, ACCENT_PURPLE, "rgba(188,140,255,0.1)","rgba(188,140,255,0.25)")),
        _badge(state, TEXT_MUTED, "rgba(72,79,88,0.1)", "rgba(72,79,88,0.25)"),
    )


def _task_row(task: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(
            rx.link(
                rx.text(task["task_id"], size="1", color=ACCENT_BLUE, font_family="'JetBrains Mono', monospace", _hover={"text_decoration": "underline"}),
                href=f"/tasks/{task['task_id']}",
                text_decoration="none"
            )
        ),
        rx.table.cell(rx.text(task["task_name"], size="2", color=TEXT_PRIMARY)),
        rx.table.cell(_task_state_badge(task["state"])),
        rx.table.cell(rx.text(task["worker_id"], size="1", color=TEXT_SECONDARY, font_family="'JetBrains Mono', monospace")),
        rx.table.cell(rx.text(task["runtime"], size="2", color=TEXT_SECONDARY)),
        style={"border_bottom": f"1px solid {BORDER}", "_hover": {"background": "rgba(88,166,255,0.03)"}},
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
        width="100%",
    )


@rx.page(route="/tasks", title="Task History — Celery Insight", on_load=AppState.fetch_tasks)
def tasks() -> rx.Component:
    return page_shell(
        rx.vstack(
            # Header
            rx.hstack(
                rx.vstack(
                    rx.text("Task History", size="6", weight="bold", color=TEXT_PRIMARY, letter_spacing="-0.02em"),
                    rx.text("Recent Celery task executions across all workers", size="2", color=TEXT_SECONDARY),
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
                        on_click=AppState.fetch_tasks,
                        _hover={"border_color": ACCENT_BLUE},
                        transition="border-color 0.15s ease",
                    ),
                ),
                width="100%",
                align="start",
                margin_bottom="1.5rem",
            ),

            # Table
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell(
                                rx.text("Task ID", size="1", weight="bold", color=TEXT_MUTED, text_transform="uppercase", letter_spacing="0.06em"),
                            ),
                            rx.table.column_header_cell(
                                rx.text("Name", size="1", weight="bold", color=TEXT_MUTED, text_transform="uppercase", letter_spacing="0.06em"),
                            ),
                            rx.table.column_header_cell(
                                rx.text("State", size="1", weight="bold", color=TEXT_MUTED, text_transform="uppercase", letter_spacing="0.06em"),
                            ),
                            rx.table.column_header_cell(
                                rx.text("Worker", size="1", weight="bold", color=TEXT_MUTED, text_transform="uppercase", letter_spacing="0.06em"),
                            ),
                            rx.table.column_header_cell(
                                rx.text("Runtime (s)", size="1", weight="bold", color=TEXT_MUTED, text_transform="uppercase", letter_spacing="0.06em"),
                            ),
                            style={"border_bottom": f"1px solid {BORDER}"},
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(AppState.tasks, _task_row),
                    ),
                    width="100%",
                ),
                background=BG_CARD,
                border=f"1px solid {BORDER}",
                border_radius="10px",
                overflow="hidden",
                backdrop_filter="blur(10px)",
                width="100%",
            ),

            # Empty state
            rx.cond(
                AppState.tasks.length() == 0,
                _empty_state("📋", "No tasks yet", "Start a Celery worker with enable_monitoring() to begin capturing task data."),
                rx.box(),
            ),

            align_items="stretch",
            spacing="0",
            width="100%",
            max_width="1200px",
        )
    )
