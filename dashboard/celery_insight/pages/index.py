import reflex as rx
from celery_insight.state import AppState
from celery_insight.template import page_shell, BG_PRIMARY, BG_CARD, BG_SECONDARY, BORDER, BORDER_SUBTLE, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED, ACCENT_AMBER, ACCENT_PURPLE

# ─── Metric card component ────────────────────────────────────────
_CARD_CONFIGS = {
    "blue":  (ACCENT_BLUE,  "rgba(88,166,255,0.1)",   "rgba(88,166,255,0.25)"),
    "red":   (ACCENT_RED,   "rgba(248,81,73,0.1)",    "rgba(248,81,73,0.25)"),
    "amber": (ACCENT_AMBER, "rgba(210,153,34,0.1)",   "rgba(210,153,34,0.25)"),
    "green": (ACCENT_GREEN, "rgba(63,185,80,0.1)",    "rgba(63,185,80,0.25)"),
}


def _metric_card(
    label: str,
    value: rx.Var,
    icon: str,
    color_key: str,
    trend: str,
) -> rx.Component:
    accent, bg, border_glow = _CARD_CONFIGS[color_key]
    return rx.box(
        # Top accent line
        rx.box(
            height="2px",
            background=f"linear-gradient(90deg, {accent}, transparent)",
            border_radius="8px 8px 0 0",
        ),
        rx.vstack(
            rx.hstack(
                rx.text(label, size="1", weight="medium", color=TEXT_SECONDARY, text_transform="uppercase", letter_spacing="0.05em"),
                rx.box(
                    rx.icon(icon, size=14, color=accent),
                    background=bg,
                    border=f"1px solid {border_glow}",
                    border_radius="6px",
                    padding="0.35rem",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                ),
                justify="between",
                width="100%",
                align="center",
            ),
            rx.text(
                value,
                size="8",
                weight="bold",
                color=TEXT_PRIMARY,
                font_variant_numeric="tabular-nums",
                line_height="1",
            ),
            rx.text(trend, size="1", color=TEXT_MUTED),
            spacing="2",
            padding="1rem 1.25rem 1.25rem",
            align_items="start",
        ),
        background=BG_CARD,
        border=f"1px solid {BORDER}",
        border_radius="10px",
        overflow="hidden",
        backdrop_filter="blur(10px)",
        _hover={"border_color": border_glow, "box_shadow": f"0 0 20px {bg}"},
        transition="border-color 0.2s ease, box-shadow 0.2s ease",
        width="100%",
    )


@rx.page(
    route="/",
    title="Dashboard — Celery Insight",
    on_load=[AppState.fetch_overview, AppState.auto_refresh],
)
def index() -> rx.Component:
    return page_shell(
        rx.vstack(
            # ─── Page header ───────────────────────────────────────
            rx.hstack(
                rx.vstack(
                    rx.text("Overview", size="6", weight="bold", color=TEXT_PRIMARY, letter_spacing="-0.02em"),
                    rx.text("Real-time Celery cluster observability", size="2", color=TEXT_SECONDARY),
                    spacing="1",
                    align_items="start",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.cond(AppState.is_loading, rx.spinner(size="1"), rx.box()),
                    rx.box(
                        rx.hstack(
                            rx.box(
                                width="6px",
                                height="6px",
                                border_radius="50%",
                                background=ACCENT_GREEN,
                                box_shadow=f"0 0 6px {ACCENT_GREEN}",
                                animation="pulse 2s infinite",
                            ),
                            rx.text("Live", size="1", color=TEXT_MUTED),
                            spacing="2",
                            align="center",
                        ),
                        background=BG_CARD,
                        border=f"1px solid {BORDER}",
                        border_radius="6px",
                        padding="0.375rem 0.75rem",
                    ),
                    spacing="3",
                    align="center",
                ),
                width="100%",
                align="start",
                margin_bottom="1.5rem",
            ),

            # ─── Metric grid ───────────────────────────────────────
            rx.grid(
                _metric_card("Active Workers", AppState.overview_data["active_workers"], "server",         "blue",  "Worker nodes online"),
                _metric_card("Failed Tasks",   AppState.overview_data["failed_tasks"],   "triangle-alert", "red",   "Requires attention"),
                _metric_card("Queue Backlog",  AppState.overview_data["queue_backlog"],  "layers",         "amber", "Pending + in progress"),
                _metric_card("Avg Runtime",    AppState.overview_data["avg_runtime"],    "timer",          "green", "Seconds per task"),
                columns="4",
                spacing="4",
                width="100%",
            ),

            rx.grid(
                # Throughput Chart (Span 2)
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.vstack(
                                rx.text("Task Throughput", size="3", weight="bold", color=TEXT_PRIMARY),
                                rx.text("Historical task ingestion metrics", size="1", color=TEXT_MUTED),
                                spacing="0",
                                align_items="start",
                            ),
                            rx.spacer(),
                            rx.tabs.root(
                                rx.tabs.list(
                                    rx.tabs.trigger("30m", value="30m"),
                                    rx.tabs.trigger("1h",  value="1h"),
                                    rx.tabs.trigger("24h", value="24h"),
                                    rx.tabs.trigger("7d",  value="7d"),
                                ),
                                value=AppState.period_range,
                                on_change=AppState.set_period_range,
                            ),
                            rx.badge("Real-time", color_scheme="blue", variant="soft"),
                            width="100%",
                            align="center",
                            padding_bottom="1rem",
                        ),
                        rx.box(
                            rx.recharts.area_chart(
                                rx.recharts.area(
                                    data_key="count",
                                    stroke=ACCENT_BLUE,
                                    fill=ACCENT_BLUE,
                                    fill_opacity=0.1,
                                    type_="monotone",
                                ),
                                rx.recharts.x_axis(data_key="time", hide=False, axis_line=False, tick_line=False, stroke=TEXT_MUTED, font_size=10),
                                rx.recharts.y_axis(hide=True),
                                rx.recharts.cartesian_grid(vertical=False, stroke_dasharray="3 3", stroke=BORDER),
                                rx.recharts.graphing_tooltip(
                                    content_style={"background-color": BG_SECONDARY, "border": f"1px solid {BORDER}", "border-radius": "6px"},
                                    item_style={"color": TEXT_PRIMARY, "font-size": "12px"},
                                    label_style={"color": TEXT_MUTED, "font-size": "10px"},
                                ),
                                data=AppState.throughput_data,
                                width="100%",
                                height=200,
                            ),
                            width="100%",
                        ),
                        spacing="0",
                        align_items="stretch",
                        padding="1.5rem",
                    ),
                    background=BG_CARD,
                    border=f"1px solid {BORDER}",
                    border_radius="10px",
                    width="100%",
                    grid_column="span 2",
                    overflow="hidden",
                ),
                # Worker Load Chart (Span 1)
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.vstack(
                                rx.text("Worker Load", size="3", weight="bold", color=TEXT_PRIMARY),
                                rx.text("Active tasks per node", size="1", color=TEXT_MUTED),
                                spacing="0",
                                align_items="start",
                            ),
                            rx.spacer(),
                            width="100%",
                            align="center",
                            padding_bottom="1rem",
                        ),
                        rx.box(
                            rx.recharts.bar_chart(
                                rx.recharts.bar(
                                    data_key="active_tasks",
                                    fill=ACCENT_PURPLE,
                                    radius=[4, 4, 0, 0],
                                ),
                                rx.recharts.x_axis(data_key="worker_id", hide=False, axis_line=False, tick_line=False, stroke=TEXT_MUTED, font_size=10),
                                rx.recharts.y_axis(hide=False, axis_line=False, tick_line=False, stroke=TEXT_MUTED, font_size=10),
                                rx.recharts.cartesian_grid(vertical=False, stroke_dasharray="3 3", stroke=BORDER),
                                rx.recharts.graphing_tooltip(
                                    content_style={"background-color": BG_SECONDARY, "border": f"1px solid {BORDER}", "border-radius": "6px"},
                                    item_style={"color": TEXT_PRIMARY, "font-size": "12px"},
                                    label_style={"color": TEXT_MUTED, "font-size": "10px"},
                                ),
                                data=AppState.workers,
                                width="100%",
                                height=200,
                            ),
                            width="100%",
                        ),
                        spacing="0",
                        align_items="stretch",
                        padding="1.5rem",
                    ),
                    background=BG_CARD,
                    border=f"1px solid {BORDER}",
                    border_radius="10px",
                    width="100%",
                    overflow="hidden",
                ),
                columns="3",
                spacing="4",
                width="100%",
                margin_top="1.5rem",
            ),

            # ─── Status / help card ────────────────────────────────
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon("shield-check", size=16, color=ACCENT_BLUE),
                        rx.text("Platform Health", size="3", weight="bold", color=TEXT_PRIMARY),
                        spacing="2",
                        align="center",
                    ),
                    rx.text(
                        "Celery Insight is actively monitoring your task infrastructure. "
                        "Connect a worker using the lightweight SDK to start seeing live data.",
                        size="2",
                        color=TEXT_SECONDARY,
                        line_height="1.6",
                    ),
                    rx.box(
                        rx.text(
                            "from sdk.celery_insight import enable_monitoring",
                            size="2",
                            color="#a371f7",
                            font_family="'JetBrains Mono', monospace",
                        ),
                        background="#0d1117",
                        border=f"1px solid {BORDER}",
                        border_radius="6px",
                        padding="0.75rem 1rem",
                        margin_top="0.5rem",
                    ),
                    align_items="start",
                    spacing="3",
                    padding="1.5rem",
                ),
                background=BG_CARD,
                border=f"1px solid {BORDER}",
                border_radius="10px",
                margin_top="1.5rem",
                width="100%",
            ),

            spacing="0",
            align_items="stretch",
            width="100%",
            max_width="1200px",
        )
    )
