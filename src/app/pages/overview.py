import os
import pandas as pd
import plotly.express as px
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from src.app.components.card import chart_card

DATA_PATH = "data/processed/cleaned_accidents.csv"
PRED_PATH = "artifacts/predictions_sample.csv"
CHART_PALETTE = [
    "#0B6E4F",
    "#1A936F",
    "#2EC4B6",
    "#118AB2",
    "#3A86FF",
    "#5E60CE",
    "#7B2CBF",
    "#FFD166",
    "#FFB703",
    "#F4A261",
    "#E76F51",
    "#D62828",
    "#264653",
    "#6B705C",
]
TOP_PROVINCE_COLORS = [
    "#FF6B6B",
    "#4D96FF",
    "#FFC75F",
    "#845EC2",
    "#00C9A7",
    "#FF9671",
    "#0081CF",
    "#C34A36",
    "#4B4453",
    "#2C73D2",
]


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


def get_available_years(dataframe: pd.DataFrame) -> list[int]:
    year_col = "ปีที่เกิดเหตุ"
    if len(dataframe) == 0 or year_col not in dataframe.columns:
        return []

    return (
        pd.to_numeric(dataframe[year_col], errors="coerce")
        .dropna()
        .astype(int)
        .sort_values()
        .unique()
        .tolist()
    )


def get_year_range_label(dataframe: pd.DataFrame) -> str | None:
    years = get_available_years(dataframe)
    if not years:
        return None

    min_year, max_year = years[0], years[-1]
    if min_year == max_year:
        return str(min_year)
    return f"{min_year}-{max_year}"


df = load_data()
pred_df = load_pred()
data_year_text = get_data_year_text(df)
province_year_range = get_year_range_label(df)


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


def _polish_fig(fig, *, margin=None, showlegend=None):
    if fig is None:
        return fig

    fig.update_layout(
        title=dict(
            text=(fig.layout.title.text if fig.layout.title else None),
            x=0.5,
            xanchor="center",
            y=0.98,
            yanchor="top",
        ),
        font=dict(size=12),
        title_font=dict(size=18),
        margin=margin or dict(l=36, r=24, t=64, b=56),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    if showlegend is not None:
        fig.update_layout(showlegend=showlegend)

    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    return fig


def _add_gridlines(fig, *, x: bool = True, y: bool = True):
    if fig is None:
        return fig
    grid_color = "rgba(0,0,0,0.12)"
    if x:
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor=grid_color,
            zeroline=False,
        )
    if y:
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor=grid_color,
            zeroline=False,
        )
    return fig


if len(df) and "จังหวัด" in df.columns:
    top_province = (
        df["จังหวัด"].fillna("ไม่ระบุ").astype(str).value_counts().head(10).reset_index()
    )
    top_province.columns = ["จังหวัด", "จำนวนเหตุ"]
    province_title = (
        f"Top 10 จังหวัดที่เกิดอุบัติเหตุสูง (สะสมปี {province_year_range})"
        if province_year_range
        else "Top 10 จังหวัดที่เกิดอุบัติเหตุสูง"
    )
    _fig_province = px.bar(
        top_province,
        x="จังหวัด",
        y="จำนวนเหตุ",
        color="จังหวัด",
        color_discrete_sequence=TOP_PROVINCE_COLORS,
        title=province_title,
    )
    _fig_province.update_xaxes(
        title_text="จังหวัด",
        tickangle=-30,
    )
    _fig_province.update_yaxes(title_text="จำนวนเหตุ")
    _polish_fig(_fig_province, margin=dict(l=36, r=16, t=64, b=76), showlegend=False)
    _add_gridlines(_fig_province, x=False, y=True)

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
        _fig_hour.update_xaxes(
            title_text="ชั่วโมง (0–23)",
            tickmode="linear",
            dtick=1,
        )
        _fig_hour.update_yaxes(title_text="จำนวนเหตุ")
        _polish_fig(_fig_hour)
        _add_gridlines(_fig_hour, x=True, y=True)

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
        color_discrete_sequence=CHART_PALETTE,
    )
    _fig_vehicle.update_traces(textinfo="none", hoverinfo="label+percent", sort=False)
    _fig_vehicle.update_layout(
        uniformtext_minsize=10,
        uniformtext_mode="hide",
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            title_text="",
        ),
    )
    _polish_fig(_fig_vehicle, margin=dict(l=20, r=220, t=64, b=40), showlegend=True)

_actual_col = "actual" if "actual" in pred_df.columns else "รวมจำนวนผู้บาดเจ็บ"
_pred_col = "predicted" if "predicted" in pred_df.columns else "prediction_label"

if len(pred_df) and {_actual_col, _pred_col}.issubset(pred_df.columns):
    pred_df = pred_df.copy()
    pred_df[_actual_col] = pd.to_numeric(pred_df[_actual_col], errors="coerce")
    pred_df[_pred_col] = pd.to_numeric(pred_df[_pred_col], errors="coerce")
    pred_df = pred_df.dropna(subset=[_actual_col, _pred_col])
    pred_df["abs_error"] = (pred_df[_actual_col] - pred_df[_pred_col]).abs()

    _fig_ap = px.scatter(
        pred_df,
        x=_actual_col,
        y=_pred_col,
        color="abs_error",
        color_continuous_scale="Turbo",
        trendline="ols",
        title="Actual vs Predicted",
    )
    _fig_ap.update_xaxes(title_text="Actual")
    _fig_ap.update_yaxes(title_text="Predicted")
    _fig_ap.update_layout(
        coloraxis_colorbar=dict(
            title="abs_error",
            y=0.5,
            yanchor="middle",
            len=0.78,
        )
    )
    _polish_fig(_fig_ap, margin=dict(l=42, r=34, t=64, b=56))
    _add_gridlines(_fig_ap, x=True, y=True)


# -- Province summary table (full-width, bottom) -----------------------------
_province_table_data = []
_province_table_columns = [
    {"name": "ลำดับ", "id": "rank"},
    {"name": "จังหวัด", "id": "จังหวัด"},
    {"name": "จำนวนเหตุ", "id": "จำนวนเหตุ"},
    {"name": "ส่วนแบ่ง (%)", "id": "ส่วนแบ่ง (%)"},
    {"name": "จุดที่เกิดบ่อยที่สุด", "id": "จุดที่เกิดบ่อยที่สุด"},
]

if len(df) and "จังหวัด" in df.columns:
    prov_series = (
        df["จังหวัด"]
        .map(
            lambda x: (
                x.decode("utf-8", errors="ignore")
                if isinstance(x, (bytes, bytearray))
                else x
            )
        )
        .astype("string")
        .str.strip()
        .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "<NA>": pd.NA})
        .fillna("ไม่ระบุ")
    )

    prov_counts = prov_series.value_counts()
    total = int(prov_counts.sum()) if len(prov_counts) else 0

    spot_col_candidates = ["บริเวณที่เกิดเหตุ", "ลักษณะการเกิดเหตุ", "มูลเหตุสันนิษฐาน"]
    spot_col = next((c for c in spot_col_candidates if c in df.columns), None)
    spot_by_prov = None
    if spot_col is not None:
        spot_series = (
            df[spot_col]
            .map(
                lambda x: (
                    x.decode("utf-8", errors="ignore")
                    if isinstance(x, (bytes, bytearray))
                    else x
                )
            )
            .astype("string")
            .str.strip()
            .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "<NA>": pd.NA})
            .fillna("ไม่ระบุ")
        )

        tmp = pd.DataFrame({"จังหวัด": prov_series, "spot": spot_series})
        spot_by_prov = (
            tmp.groupby("จังหวัด")["spot"]
            .agg(lambda s: s.value_counts().index[0] if len(s) else "ไม่ระบุ")
            .to_dict()
        )

    rows = []
    for i, (prov, cnt) in enumerate(prov_counts.items(), start=1):
        share = (float(cnt) / float(total) * 100.0) if total else 0.0
        rows.append(
            {
                "rank": i,
                "จังหวัด": prov,
                "จำนวนเหตุ": int(cnt),
                "ส่วนแบ่ง (%)": f"{share:.1f}%",
                "จุดที่เกิดบ่อยที่สุด": (
                    spot_by_prov.get(prov, "ไม่ระบุ") if spot_by_prov else "ไม่ระบุ"
                ),
            }
        )

    _province_table_data = rows


# -- Build grid rows ---------------------------------------------------------
chart_rows = []

# Row 1: Top-10 province bar  +  vehicle pie  (side-by-side)
_row1_cols = []
if _fig_province:
    _row1_cols.append(dbc.Col(chart_card(_fig_province), md=6))
if _fig_vehicle:
    _row1_cols.append(dbc.Col(chart_card(_fig_vehicle), md=6))
if _row1_cols:
    chart_rows.append(dbc.Row(_row1_cols, className="g-3 mb-3"))

# Row 2: hourly line  +  actual-vs-predicted (stacked, full-width)
if _fig_hour:
    chart_rows.append(
        dbc.Row([dbc.Col(chart_card(_fig_hour), md=12)], className="g-3 mb-3")
    )
if _fig_ap:
    chart_rows.append(
        dbc.Row([dbc.Col(chart_card(_fig_ap), md=12)], className="g-3 mb-3")
    )

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
        # -- Province summary table (bottom, full-width) --
        html.Div(
            [
                html.H5("📋 สรุปอุบัติเหตุตามจังหวัด", className="ov-section-title"),
                html.Hr(className="ov-divider"),
            ],
            className="mt-2 mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dash_table.DataTable(
                                columns=_province_table_columns,
                                data=_province_table_data,
                                page_action="none",
                                fixed_rows={"headers": True},
                                style_table={
                                    "height": "520px",
                                    "overflowY": "auto",
                                    "overflowX": "auto",
                                },
                                style_cell={
                                    "padding": "6px",
                                    "textAlign": "left",
                                    "whiteSpace": "normal",
                                    "height": "auto",
                                    "lineHeight": "1.25",
                                },
                                style_header={
                                    "fontWeight": "bold",
                                    "textAlign": "left",
                                },
                                style_cell_conditional=[
                                    {
                                        "if": {"column_id": "rank"},
                                        "minWidth": "10%",
                                        "width": "10%",
                                        "maxWidth": "10%",
                                    },
                                    {
                                        "if": {"column_id": "จังหวัด"},
                                        "minWidth": "22.5%",
                                        "width": "22.5%",
                                        "maxWidth": "22.5%",
                                    },
                                    {
                                        "if": {"column_id": "จำนวนเหตุ"},
                                        "minWidth": "22.5%",
                                        "width": "22.5%",
                                        "maxWidth": "22.5%",
                                    },
                                    {
                                        "if": {
                                            "column_id": "ส่วนแบ่ง (%)",
                                        },
                                        "minWidth": "22.5%",
                                        "width": "22.5%",
                                        "maxWidth": "22.5%",
                                    },
                                    {
                                        "if": {
                                            "column_id": "จุดที่เกิดบ่อยที่สุด",
                                        },
                                        "minWidth": "22.5%",
                                        "width": "22.5%",
                                        "maxWidth": "22.5%",
                                    },
                                ],
                            )
                        ),
                        className="section-card",
                    ),
                    md=12,
                )
            ],
            className="g-3 mb-3",
        ),
    ],
    fluid=True,
    className="page-wrap pb-4",
)
