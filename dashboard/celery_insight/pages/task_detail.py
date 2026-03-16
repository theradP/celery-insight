import reflex as rx
from celery_insight.state import AppState
from celery_insight.template import page_shell, BG_CARD, BORDER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED, ACCENT_AMBER
from celery_insight.pages.tasks import _task_state_badge


def _detail_row(label: str, value: rx.Var) -> rx.Component:
    """A single metadata row: label on the left, value on the right."""
    return rx.hstack(
        rx.text(label, size="2", weight="bold", color=TEXT_SECONDARY, min_width="110px", flex_shrink="0"),
        rx.text(value, size="2", color=TEXT_PRIMARY, font_family="'JetBrains Mono', monospace", word_break="break-all"),
        spacing="4",
        align="start",
        padding_y="0.5rem",
        border_bottom=f"1px solid {BORDER}",
        width="100%",
    )


def _timeline_dot(event_type: rx.Var) -> rx.Component:
    """Colored dot for the timeline, based on event type."""
    return rx.box(
        width="11px",
        height="11px",
        border_radius="50%",
        background=rx.match(
            event_type,
            ("task-failed",    ACCENT_RED),
            ("task-succeeded", ACCENT_GREEN),
            ("task-retried",   ACCENT_AMBER),
            ACCENT_BLUE,
        ),
        margin_top="0.25rem",
        box_shadow="0 0 0 4px rgba(255,255,255,0.05)",
        flex_shrink="0",
    )


def _timeline_event(event: rx.Var[dict[str, str]]) -> rx.Component:
    """One node in the vertical event timeline."""
    return rx.box(
        rx.hstack(
            _timeline_dot(event["event_type"]),
            rx.vstack(
                rx.text(
                    event["event_type"],
                    size="2",
                    weight="bold",
                    color=TEXT_PRIMARY,
                    text_transform="uppercase",
                    letter_spacing="0.05em",
                ),
                rx.text(
                    event["timestamp"],
                    size="1",
                    color=TEXT_MUTED,
                    font_family="'JetBrains Mono', monospace",
                ),
                spacing="1",
                align_items="start",
                width="100%",
            ),
            spacing="4",
            align_items="start",
            width="100%",
        ),
        position="relative",
        padding_left="0",
        padding_bottom="1.5rem",
    )


@rx.page(
    route="/tasks/[task_id]",
    title="Task Details — Celery Insight",
    on_load=AppState.fetch_task_detail,
)
def task_detail() -> rx.Component:
    task = AppState.current_task_details["task"].to(dict[str, str])
    timeline = AppState.current_task_details["timeline"].to(list[dict[str, str]])

    return page_shell(
        rx.vstack(
            # ── Back Link ───────────────────────────────────────────
            rx.link(
                rx.hstack(
                    rx.icon("arrow-left", size=14, color=TEXT_MUTED),
                    rx.text("Back to Tasks", size="2", color=TEXT_MUTED),
                    spacing="2",
                    align="center",
                ),
                href="/tasks",
                text_decoration="none",
                _hover={"opacity": "0.8"},
            ),

            # ── Page Header ────────────────────────────────────────
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "Task Details",
                        size="6",
                        weight="bold",
                        color=TEXT_PRIMARY,
                        letter_spacing="-0.02em",
                    ),
                    rx.hstack(
                        rx.text(
                            task["task_id"],
                            size="2",
                            color=TEXT_SECONDARY,
                            font_family="'JetBrains Mono', monospace",
                        ),
                        _task_state_badge(task["state"]),
                        spacing="3",
                        align="center",
                    ),
                    spacing="2",
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
                        on_click=AppState.fetch_task_detail,
                        _hover={"border_color": "rgba(255,255,255,0.2)"},
                        transition="border-color 0.15s ease",
                    ),
                ),
                width="100%",
                align="start",
            ),

            # ── Two-Column Layout ──────────────────────────────────
            rx.grid(
                # Left: Metadata Card
                rx.box(
                    rx.text("Metadata", size="3", weight="bold", color=TEXT_PRIMARY, margin_bottom="1rem"),
                    rx.vstack(
                        _detail_row("Task Name", task["task_name"]),
                        _detail_row("State",     task["state"]),
                        _detail_row("Worker",    task["worker_id"]),
                        _detail_row("Runtime",   task["runtime"]),
                        _detail_row("Exception", task["exception"]),
                        spacing="0",
                        align_items="stretch",
                        width="100%",
                    ),
                    background=BG_CARD,
                    border=f"1px solid {BORDER}",
                    border_radius="10px",
                    padding="1.5rem",
                    width="100%",
                    height="fit-content",
                ),

                # Right: Event Timeline Card
                rx.box(
                    rx.text("Event Timeline", size="3", weight="bold", color=TEXT_PRIMARY, margin_bottom="1.5rem"),
                    rx.cond(
                        timeline.length() > 0,
                        rx.vstack(
                            rx.foreach(timeline, _timeline_event),
                            spacing="0",
                            align_items="stretch",
                            width="100%",
                        ),
                        rx.box(
                            rx.text(
                                "No events recorded for this task.",
                                size="2",
                                color=TEXT_MUTED,
                                text_align="center",
                            ),
                            padding="3rem",
                            border=f"1px dashed {BORDER}",
                            border_radius="8px",
                        ),
                    ),
                    background=BG_CARD,
                    border=f"1px solid {BORDER}",
                    border_radius="10px",
                    padding="1.5rem",
                    width="100%",
                ),
                columns="2",
                spacing="6",
                width="100%",
            ),

            spacing="5",
            align_items="stretch",
            width="100%",
            max_width="1200px",
        )
    )
