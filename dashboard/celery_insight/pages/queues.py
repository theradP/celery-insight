import reflex as rx
from celery_insight.state import AppState
from celery_insight.template import page_shell, BG_CARD, BORDER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED, ACCENT_AMBER


def _queue_card(queue: rx.Var[dict[str, str]]) -> rx.Component:
    """A card representing a single queue's health metrics."""
    return rx.box(
        rx.vstack(
            # Queue name header
            rx.hstack(
                rx.icon("layers", size=16, color=ACCENT_BLUE),
                rx.text(
                    queue["queue_name"],
                    size="3",
                    weight="bold",
                    color=TEXT_PRIMARY,
                    font_family="'JetBrains Mono', monospace",
                ),
                spacing="2",
                align="center",
            ),

            rx.separator(color=BORDER, margin_y="0.75rem"),

            # Stats grid
            rx.grid(
                # Pending
                rx.vstack(
                    rx.text(queue["pending_tasks"], size="5", weight="bold", color=ACCENT_AMBER),
                    rx.text("Pending", size="1", color=TEXT_MUTED, text_transform="uppercase", letter_spacing="0.06em"),
                    spacing="1",
                    align="center",
                ),
                # Completed
                rx.vstack(
                    rx.text(queue["completed_tasks"], size="5", weight="bold", color=ACCENT_GREEN),
                    rx.text("Completed", size="1", color=TEXT_MUTED, text_transform="uppercase", letter_spacing="0.06em"),
                    spacing="1",
                    align="center",
                ),
                # Failed
                rx.vstack(
                    rx.text(queue["failed_tasks"], size="5", weight="bold", color=ACCENT_RED),
                    rx.text("Failed", size="1", color=TEXT_MUTED, text_transform="uppercase", letter_spacing="0.06em"),
                    spacing="1",
                    align="center",
                ),
                # Total
                rx.vstack(
                    rx.text(queue["total_tasks"], size="5", weight="bold", color=TEXT_PRIMARY),
                    rx.text("Total", size="1", color=TEXT_MUTED, text_transform="uppercase", letter_spacing="0.06em"),
                    spacing="1",
                    align="center",
                ),
                columns="4",
                spacing="4",
                width="100%",
            ),

            rx.separator(color=BORDER, margin_y="0.75rem"),

            # Avg runtime footer
            rx.hstack(
                rx.text("Avg Runtime", size="1", color=TEXT_MUTED),
                rx.spacer(),
                rx.text(
                    queue["avg_runtime"],
                    size="2",
                    weight="bold",
                    color=ACCENT_BLUE,
                    font_family="'JetBrains Mono', monospace",
                ),
                rx.text("s", size="1", color=TEXT_MUTED),
                width="100%",
                align="center",
            ),

            spacing="2",
            align_items="stretch",
            width="100%",
        ),
        background=BG_CARD,
        border=f"1px solid {BORDER}",
        border_radius="10px",
        padding="1.5rem",
        width="100%",
        _hover={"border_color": "rgba(88,166,255,0.3)"},
        transition="border-color 0.2s ease",
    )


@rx.page(route="/queues", title="Queue Health — Celery Insight", on_load=AppState.fetch_queues)
def queues() -> rx.Component:
    return page_shell(
        rx.vstack(
            # Header
            rx.hstack(
                rx.vstack(
                    rx.text("Queue Health", size="6", weight="bold", color=TEXT_PRIMARY, letter_spacing="-0.02em"),
                    rx.text("Per-queue task distribution, backlog, and throughput", size="2", color=TEXT_SECONDARY),
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
                        on_click=AppState.fetch_queues,
                        _hover={"border_color": ACCENT_BLUE},
                        transition="border-color 0.15s ease",
                    ),
                ),
                width="100%",
                align="start",
                margin_bottom="1.5rem",
            ),

            # Queue cards grid
            rx.cond(
                AppState.queues.length() > 0,
                rx.grid(
                    rx.foreach(AppState.queues, _queue_card),
                    columns="2",
                    spacing="6",
                    width="100%",
                ),
                # Empty state
                rx.box(
                    rx.vstack(
                        rx.text("📦", size="7"),
                        rx.text("No queues detected", size="3", weight="bold", color=TEXT_SECONDARY),
                        rx.text(
                            "Queue data appears once tasks are processed. Start a Celery worker with enable_monitoring() to begin.",
                            size="2",
                            color=TEXT_MUTED,
                            text_align="center",
                            max_width="420px",
                        ),
                        spacing="3",
                        align="center",
                    ),
                    padding="4rem",
                    text_align="center",
                    width="100%",
                ),
            ),

            align_items="stretch",
            spacing="0",
            width="100%",
            max_width="1200px",
        )
    )
