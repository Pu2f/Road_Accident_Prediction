import os
import pandas as pd
import plotly.express as px
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc

DATA_PATH = "data/processed/cleaned_accidents.csv"
PRED_PATH = "artifacts/predictions_sample.csv"


# ---- Plotly chart theme (aligned with src/app/assets/style.css) ------------
# NOTE: Dash/Plotly can't directly read CSS variables server-side, so we keep
# these values in sync with :root tokens used by the app.
_PLOT_TEXT_COLOR = "#1f2a37"  # --foreground
_PLOT_MUTED_TEXT = "#64748b"  # --muted-foreground
_PLOT_GRID_COLOR = "#dce4ef"  # --border


def _apply_plot_style(fig, *, x_grid: bool = True, y_grid: bool = True):
    """Apply a light-theme Plotly style so gridlines are visible on white cards."""

    if fig is None:
        return None

    fig.update_layout(
        template="plotly_white",
        font=dict(color=_PLOT_TEXT_COLOR),
        title=dict(font=dict(color=_PLOT_TEXT_COLOR)),
        legend=dict(font=dict(color=_PLOT_MUTED_TEXT)),
    )

    # Keep the chart background transparent so the card background shows.
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")

    # Axes + grid (explicitly set for readability on light theme)
    fig.update_xaxes(
        showgrid=x_grid,
        gridcolor=_PLOT_GRID_COLOR,
        gridwidth=1,
        zeroline=False,
        tickfont=dict(color=_PLOT_MUTED_TEXT),
        title=dict(font=dict(color=_PLOT_MUTED_TEXT)),
    )
    fig.update_yaxes(
        showgrid=y_grid,
        gridcolor=_PLOT_GRID_COLOR,
        gridwidth=1,
        zeroline=False,
        tickfont=dict(color=_PLOT_MUTED_TEXT),
        title=dict(font=dict(color=_PLOT_MUTED_TEXT)),
    )

    return fig


def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH, low_memory=False)
    return pd.DataFrame()


def load_pred():
    if os.path.exists(PRED_PATH):
        return pd.read_csv(PRED_PATH)
    return pd.DataFrame()


def get_data_year_text(dataframe: pd.DataFrame) -> str:
    if len(dataframe) == 0:
        return "ปีข้อมูลที่ใช้: ไม่พบข้อมูล"

    year_col = "ปีที่เกิดเหตุ"
    if year_col in dataframe.columns:
        years = (
            pd.to_numeric(dataframe[year_col], errors="coerce")
            .dropna()
            .astype(int)
            .sort_values()
            .unique()
            .tolist()
        )
        if years:
            min_year, max_year = years[0], years[-1]
            if min_year == max_year:
                return f"ปีข้อมูลที่ใช้: {min_year}"
            return f"ปีข้อมูลที่ใช้: {min_year}–{max_year}"

    return "ปีข้อมูลที่ใช้: ไม่สามารถระบุปีจากข้อมูลได้"


df = load_data()
pred_df = load_pred()
data_year_text = get_data_year_text(df)


def _kpi(icon, label, value, accent):
    """Build a single KPI card with icon and accent colour."""
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.Span(
                            icon, className="kpi-icon", style={"background": accent}
                        ),
                        html.Div(
                            [
                                html.P(label, className="kpi-label mb-0"),
                                html.H3(value, className="kpi-value mb-0"),
                            ]
                        ),
                    ],
                    className="d-flex align-items-center gap-3",
                ),
            ]
        ),
        className="kpi-card",
    )


_injury_avg = (
    f"{pd.to_numeric(df['รวมจำนวนผู้บาดเจ็บ'], errors='coerce').mean():.2f}"
    if "รวมจำนวนผู้บาดเจ็บ" in df.columns and len(df)
    else "N/A"
)

cards = dbc.Card(
    dbc.CardBody(
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.Span(
                                "📊",
                                className="kpi-icon",
                                style={"background": "#e8f0fe"},
                            ),
                            html.Div(
                                [
                                    html.P("จำนวนแถวข้อมูล", className="kpi-label mb-0"),
                                    html.H4(f"{len(df):,}", className="kpi-value mb-0"),
                                ]
                            ),
                        ],
                        className="d-flex align-items-center gap-3",
                    ),
                    className="kpi-cell",
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.Span(
                                "🗺️",
                                className="kpi-icon",
                                style={"background": "#fef3e2"},
                            ),
                            html.Div(
                                [
                                    html.P("จำนวนจังหวัด", className="kpi-label mb-0"),
                                    html.H4(
                                        f"{df['จังหวัด'].nunique() if 'จังหวัด' in df.columns else 0:,}",
                                        className="kpi-value mb-0",
                                    ),
                                ]
                            ),
                        ],
                        className="d-flex align-items-center gap-3",
                    ),
                    className="kpi-cell",
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.Span(
                                "🏥",
                                className="kpi-icon",
                                style={"background": "#e6f9f0"},
                            ),
                            html.Div(
                                [
                                    html.P("บาดเจ็บรวมเฉลี่ย", className="kpi-label mb-0"),
                                    html.H4(_injury_avg, className="kpi-value mb-0"),
                                ]
                            ),
                        ],
                        className="d-flex align-items-center gap-3",
                    ),
                    className="kpi-cell",
                ),
            ],
            className="g-0 align-items-center",
        )
    ),
    className="kpi-strip mb-4",
)

# -- Collect chart figures into named slots for grid placement ----------------
_fig_province = None
_fig_hour = None
_fig_vehicle = None
_fig_ap = None

if len(df) and "จังหวัด" in df.columns:
    top_province = (
        df["จังหวัด"].fillna("ไม่ระบุ").astype(str).value_counts().head(10).reset_index()
    )
    top_province.columns = ["จังหวัด", "จำนวนเหตุ"]
    _fig_province = px.bar(
        top_province,
        x="จังหวัด",
        y="จำนวนเหตุ",
        color="จังหวัด",
        color_discrete_sequence=px.colors.qualitative.Set3,
        title="Top 10 จังหวัดที่เกิดอุบัติเหตุสูง",
    )
    _fig_province.update_layout(
        showlegend=False,
        margin=dict(l=30, r=20, t=50, b=40),
    )
    _apply_plot_style(_fig_province, x_grid=False, y_grid=True)

if len(df) and "hour" in df.columns:
    hour_series = pd.to_numeric(df["hour"], errors="coerce").dropna().astype(int)
    if len(hour_series):
        hour_count = hour_series.value_counts().sort_index().reset_index()
        hour_count.columns = ["hour", "จำนวนเหตุ"]
        _fig_hour = px.line(
            hour_count,
            x="hour",
            y="จำนวนเหตุ",
            markers=True,
            title="จำนวนอุบัติเหตุตามชั่วโมง",
        )
        _fig_hour.update_layout(margin=dict(l=30, r=20, t=50, b=40))
        _apply_plot_style(_fig_hour, x_grid=True, y_grid=True)

# ✅ pie chart
vehicle_col_candidates = [
    "ประเภทรถ",
    "ประเภทรถที่เกิดเหตุ",
    "ประเภทยานพาหนะ",
    "รถคันที่1",
]
vehicle_col = next((c for c in vehicle_col_candidates if c in df.columns), None)

if vehicle_col is None and len(df):
    object_cols = df.select_dtypes(
        include=["object", "string", "category"]
    ).columns.tolist()
    fallback_col = [
        c
        for c in object_cols
        if "รถ" in str(c) and c not in {"รถที่เกิดเหตุ", "รถและคนที่เกิดเหตุ"}
    ]
    if fallback_col:
        vehicle_col = fallback_col[0]

if vehicle_col and len(df):
    vehicle_count = (
        df[vehicle_col]
        .fillna("ไม่ระบุ")
        .astype(str)
        .str.strip()
        .replace({"": "ไม่ระบุ", "nan": "ไม่ระบุ", "None": "ไม่ระบุ", "<NA>": "ไม่ระบุ"})
        .value_counts()
        .head(8)
        .reset_index()
    )
    vehicle_count.columns = ["ประเภทรถ", "จำนวนเหตุ"]

    other_labels = {"อื่นๆ", "อื่น ๆ", "อื่น"}
    other_mask = vehicle_count["ประเภทรถ"].astype(str).str.strip().isin(other_labels)
    if other_mask.any():
        vehicle_count = pd.concat(
            [vehicle_count.loc[~other_mask], vehicle_count.loc[other_mask]],
            ignore_index=True,
        )

    _fig_vehicle = px.pie(
        vehicle_count,
        names="ประเภทรถ",
        values="จำนวนเหตุ",
        title="สัดส่วนประเภทรถที่เกิดอุบัติเหตุ",
        hole=0.35,
    )
    _fig_vehicle.update_traces(textinfo="none", hoverinfo="label+percent", sort=False)
    _fig_vehicle.update_layout(
        uniformtext_minsize=10,
        uniformtext_mode="hide",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    _apply_plot_style(_fig_vehicle, x_grid=False, y_grid=False)

if len(pred_df) and {"actual", "predicted"}.issubset(pred_df.columns):
    _fig_ap = px.scatter(
        pred_df,
        x="actual",
        y="predicted",
        trendline="ols",
        title="Actual vs Predicted",
    )
    _fig_ap.update_layout(margin=dict(l=30, r=20, t=50, b=40))
    _apply_plot_style(_fig_ap, x_grid=True, y_grid=True)


def _chart_card(fig):
    """Wrap a Plotly figure in a styled section card."""
    return dbc.Card(
        dbc.CardBody(dcc.Graph(figure=fig, className="chart-graph")),
        className="section-card",
    )


def _make_province_summary(df: pd.DataFrame, top_n: int | None = 10) -> pd.DataFrame:
    """Build a summary table of accident counts by province.

    Includes:
    - จำนวนเหตุ (count)
    - ส่วนแบ่ง (%) ที่เกิดขึ้นในแต่ละจังหวัด
    - จุดที่เกิดอุบัติเหตุบ่อยที่สุด (ถ้ามีคอลัมน์ข้อมูล)

    If ``top_n`` is None, returns all provinces.
    """

    if df.empty or "จังหวัด" not in df.columns:
        return pd.DataFrame()

    total = len(df)
    prov_series = df["จังหวัด"].fillna("ไม่ระบุ").astype(str)
    counts = prov_series.value_counts().reset_index()
    counts.columns = ["จังหวัด", "จำนวนเหตุ"]
    counts.insert(0, "ลำดับ", range(1, len(counts) + 1))
    counts["ส่วนแบ่ง (%)"] = (counts["จำนวนเหตุ"] / total * 100).map("{:.1f}%".format)

    if top_n is not None:
        counts = counts.head(top_n)

    if "บริเวณที่เกิดเหตุ" in df.columns:
        loc_series = df["บริเวณที่เกิดเหตุ"].fillna("ไม่ระบุ").astype(str)
        top_locations = []
        for prov in counts["จังหวัด"]:
            mask = prov_series == prov
            loc_counts = loc_series[mask].value_counts()
            top_locations.append(loc_counts.idxmax() if len(loc_counts) else "ไม่ระบุ")
        counts["จุดที่เกิดบ่อยที่สุด"] = top_locations

    return counts


def _data_table(df: pd.DataFrame, max_rows: int | None = 10, max_cols: int = 10):
    """Show a small sample of the dataframe as a scrollable Dash data table."""

    if df.empty:
        return html.Div("ไม่พบข้อมูลสำหรับแสดงในตาราง", className="text-muted")

    cols = df.columns.tolist()[:max_cols]
    sample = df[cols] if max_rows is None else df[cols].head(max_rows)

    return dash_table.DataTable(
        columns=[{"name": c, "id": c} for c in sample.columns],
        data=sample.to_dict("records"),
        page_action="none",
        style_table={"maxHeight": "520px", "overflowY": "auto", "overflowX": "auto"},
        fixed_rows={"headers": True},
        style_cell={
            "textAlign": "left",
            "padding": "6px",
            "whiteSpace": "normal",
            "minWidth": "120px",
        },
        style_cell_conditional=[
            {"if": {"column_id": "ลำดับ"}, "width": "60px", "maxWidth": "60px"},
        ],
        style_header={"fontWeight": "bold"},
    )


# -- Build grid rows ---------------------------------------------------------
chart_rows = []

# Row 1: Top-10 province bar  +  vehicle pie  (side-by-side)
_row1_cols = []
if _fig_province:
    _row1_cols.append(dbc.Col(_chart_card(_fig_province), md=6))
if _fig_vehicle:
    _row1_cols.append(dbc.Col(_chart_card(_fig_vehicle), md=6))
if _row1_cols:
    chart_rows.append(dbc.Row(_row1_cols, className="g-3 mb-3"))

# Row 2: hourly line  +  actual-vs-predicted  (side-by-side, or full-width if alone)
_row2_cols = []
if _fig_hour:
    _hour_width = 6 if _fig_ap else 12
    _row2_cols.append(dbc.Col(_chart_card(_fig_hour), md=_hour_width))
if _fig_ap:
    _ap_width = 6 if _fig_hour else 12
    _row2_cols.append(dbc.Col(_chart_card(_fig_ap), md=_ap_width))
if _row2_cols:
    chart_rows.append(dbc.Row(_row2_cols, className="g-3 mb-3"))

layout = dbc.Container(
    [
        # -- Page header --
        html.Div(
            [
                html.H3("Overview Dashboard", className="ov-heading"),
                html.P(
                    "ภาพรวมข้อมูลอุบัติเหตุและผลโมเดล",
                    className="section-subtitle mb-0",
                ),
                html.Small(data_year_text, className="text-muted"),
            ],
            className="ov-page-header mb-4",
        ),
        # -- KPI cards --
        cards,
        # -- Section divider --
        html.Div(
            [
                html.H5("📈 กราฟวิเคราะห์", className="ov-section-title"),
                html.Hr(className="ov-divider"),
            ],
            className="mt-2 mb-3",
        ),
        # -- Charts grid --
        *chart_rows,
        # -- Data table summary --
        html.Div(
            [
                html.H5("📋 สรุปอุบัติเหตุตามจังหวัด", className="ov-section-title"),
                html.Hr(className="ov-divider"),
                dbc.Card(
                    dbc.CardBody(
                        _data_table(
                            _make_province_summary(df, top_n=None),
                            max_rows=None,
                            max_cols=5,
                        )
                    ),
                    className="section-card",
                ),
            ],
            className="mt-3 mb-4",
        ),
    ],
    fluid=True,
    className="page-wrap pb-4",
)
