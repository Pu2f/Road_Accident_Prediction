import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc, dash_table, Input, Output, State, callback
import dash_bootstrap_components as dbc

DATA_PATH = "data/processed/cleaned_accidents.csv"


def minmax(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce").fillna(0.0)
    mn, mx = s.min(), s.max()
    if mx == mn:
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - mn) / (mx - mn)


def load_and_score() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()

    df = pd.read_csv(DATA_PATH, low_memory=False)

    required = [
        "LATITUDE",
        "LONGITUDE",
        "รวมจำนวนผู้บาดเจ็บ",
        "จำนวนผู้เสียชีวิต",
        "is_peak_hour",
        "จังหวัด",
    ]
    for c in required:
        if c not in df.columns:
            df[c] = 0 if c != "จังหวัด" else "Unknown"

    # numeric cleanup
    for c in [
        "LATITUDE",
        "LONGITUDE",
        "รวมจำนวนผู้บาดเจ็บ",
        "จำนวนผู้เสียชีวิต",
        "is_peak_hour",
    ]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df["รวมจำนวนผู้บาดเจ็บ"] = df["รวมจำนวนผู้บาดเจ็บ"].fillna(0).clip(lower=0)
    df["จำนวนผู้เสียชีวิต"] = df["จำนวนผู้เสียชีวิต"].fillna(0).clip(lower=0)
    df["is_peak_hour"] = df["is_peak_hour"].fillna(0).clip(lower=0, upper=1)

    # Thailand bounding box
    df = df[
        df["LATITUDE"].between(5, 21, inclusive="both")
        & df["LONGITUDE"].between(97, 106, inclusive="both")
    ].copy()

    if df.empty:
        return df

    # grid frequency
    df["lat_bin"] = (df["LATITUDE"] * 20).round() / 20  # ~0.05 deg
    df["lon_bin"] = (df["LONGITUDE"] * 20).round() / 20
    area_freq = (
        df.groupby(["lat_bin", "lon_bin"]).size().rename("area_freq").reset_index()
    )
    df = df.merge(area_freq, on=["lat_bin", "lon_bin"], how="left")

    # robust severity (clip outliers by p95)
    severity_raw = df["รวมจำนวนผู้บาดเจ็บ"] + 3 * df["จำนวนผู้เสียชีวิต"]
    p95 = severity_raw.quantile(0.95)
    severity_clip = severity_raw.clip(upper=p95)

    severity_score = minmax(severity_clip)
    freq_score = minmax(df["area_freq"])
    time_score = df["is_peak_hour"]  # 0/1

    # weighted risk score 0-100
    df["risk_score"] = (
        0.5 * severity_score + 0.3 * freq_score + 0.2 * time_score
    ) * 100
    df["risk_score"] = df["risk_score"].clip(0, 100)

    df["risk_level"] = pd.cut(
        df["risk_score"],
        bins=[-0.1, 33.33, 66.66, 100],
        labels=["Low", "Medium", "High"],
    )

    return df.reset_index(drop=True)


df = load_and_score()


def _clean_text_series(s: pd.Series) -> pd.Series:
    return (
        s.astype("string")
        .str.strip()
        .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "<NA>": pd.NA})
        .fillna("Unknown")
    )


if "จังหวัด" in df.columns:
    df["จังหวัด"] = _clean_text_series(df["จังหวัด"])


# Summaries for “most frequent” and “most dangerous” locations
def _top_locations(df: pd.DataFrame, top_n: int = 3):
    """Return top locations by frequency and by average risk score."""

    if df.empty or not {"lat_bin", "lon_bin"}.issubset(df.columns):
        return pd.DataFrame(), pd.DataFrame()

    grp = (
        df.groupby(["lat_bin", "lon_bin"])
        .agg(
            count=("risk_score", "size"),
            avg_risk=("risk_score", "mean"),
        )
        .reset_index()
    )

    top_freq = grp.sort_values("count", ascending=False).head(top_n)
    top_risk = grp.sort_values("avg_risk", ascending=False).head(top_n)

    return top_freq, top_risk


def _make_empty_map(message: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        template="plotly_white",
        height=720,
        margin=dict(l=0, r=0, t=50, b=0),
        annotations=[
            dict(
                text=message,
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=16, color="#4b5d79"),
            )
        ],
    )
    return fig


def _map_view_for_df(source_df: pd.DataFrame, focused: bool) -> tuple[dict, float]:
    """Return map center/zoom from data; use tighter zoom when search is focused."""
    if source_df.empty:
        return {"lat": 13.7, "lon": 100.5}, 4.8

    lat = pd.to_numeric(source_df["LATITUDE"], errors="coerce")
    lon = pd.to_numeric(source_df["LONGITUDE"], errors="coerce")
    lat = lat.dropna()
    lon = lon.dropna()

    if lat.empty or lon.empty:
        return {"lat": 13.7, "lon": 100.5}, 4.8

    center = {"lat": float(lat.median()), "lon": float(lon.median())}

    if not focused:
        return center, 4.8

    # Use spread to choose a practical zoom level for searched areas.
    lat_span = float(lat.quantile(0.95) - lat.quantile(0.05))
    lon_span = float(lon.quantile(0.95) - lon.quantile(0.05))
    span = max(lat_span, lon_span)
    if span <= 0.08:
        zoom = 10.5
    elif span <= 0.2:
        zoom = 9.5
    elif span <= 0.45:
        zoom = 8.8
    elif span <= 0.9:
        zoom = 7.8
    else:
        zoom = 6.8

    return center, zoom


def _make_map_figure(source_df: pd.DataFrame, title_suffix: str = "", focused: bool = False) -> go.Figure:
    if source_df.empty:
        return _make_empty_map("ไม่พบข้อมูลตามเงื่อนไขที่ค้นหา")

    if len(source_df) > 18000:
        df_plot = source_df.sample(18000, random_state=42)
    else:
        df_plot = source_df.copy()

    title = "Risk Level Map (Low / Medium / High)"
    if title_suffix:
        title = f"{title} - {title_suffix}"

    hover_payload = {
        "risk_score": ":.2f",
        "LATITUDE": ":.4f",
        "LONGITUDE": ":.4f",
    }

    map_center, map_zoom = _map_view_for_df(source_df, focused=focused)

    fig_level = px.scatter_mapbox(
        df_plot,
        lat="LATITUDE",
        lon="LONGITUDE",
        color="risk_level",
        color_discrete_map={
            "Low": "#2ecc71",
            "Medium": "#f39c12",
            "High": "#e74c3c",
        },
        hover_name="จังหวัด",
        hover_data=hover_payload,
        zoom=map_zoom,
        center=map_center,
        height=720,
        mapbox_style="carto-positron",
        title=title,
        opacity=0.6,
    )
    fig_level.update_traces(marker={"size": 6})
    fig_level.update_layout(
        margin=dict(l=0, r=0, t=50, b=0), legend_title_text="Risk Level"
    )
    return fig_level


def _to_table_rows(freq_tbl: pd.DataFrame, risk_tbl: pd.DataFrame):
    freq_rows = [
        {
            "rank": i + 1,
            "lat": f"{row['lat_bin']:.4f}",
            "lon": f"{row['lon_bin']:.4f}",
            "count": int(row["count"]),
        }
        for i, row in freq_tbl.reset_index(drop=True).iterrows()
    ]
    risk_rows = [
        {
            "rank": i + 1,
            "lat": f"{row['lat_bin']:.4f}",
            "lon": f"{row['lon_bin']:.4f}",
            "avg_risk": f"{row['avg_risk']:.1f}",
        }
        for i, row in risk_tbl.reset_index(drop=True).iterrows()
    ]
    return freq_rows, risk_rows


def _filter_df(source_df: pd.DataFrame, province_value: str):
    out = source_df.copy()
    if province_value and province_value != "ALL":
        out = out[out["จังหวัด"] == province_value]
    return out


province_options = [{"label": "ทั้งหมด", "value": "ALL"}]
if not df.empty and "จังหวัด" in df.columns:
    province_values = sorted(
        [
            p
            for p in df["จังหวัด"].dropna().astype("string").unique().tolist()
            if p != "Unknown"
        ]
    )
    province_options += [{"label": p, "value": p} for p in province_values]

initial_filtered = _filter_df(df, "ALL") if not df.empty else pd.DataFrame()
initial_freq_tbl, initial_risk_tbl = _top_locations(initial_filtered)
initial_freq_rows, initial_risk_rows = _to_table_rows(initial_freq_tbl, initial_risk_tbl)
initial_fig = _make_map_figure(initial_filtered, focused=False)
initial_summary = f"พบข้อมูล {len(initial_filtered):,} แถว"

layout = dbc.Container(
    [
        html.H3("Risk Map Module"),
        html.P(
            "Risk Score (0-100) คำนวณจากการผสาน 3 ปัจจัยหลัก ได้แก่ ความรุนแรงของเหตุการณ์ "
            "(จำนวนผู้บาดเจ็บ + น้ำหนักผู้เสียชีวิต), ความถี่การเกิดซ้ำในพื้นที่ใกล้เคียง (area frequency), "
            "และการเกิดเหตุในช่วงเวลาเร่งด่วน (is_peak_hour)",
            className="section-subtitle",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("จุดที่เกิดเหตุมากที่สุด (Top 3)", className="card-title"),
                                dash_table.DataTable(
                                    id="risk-map-freq-table",
                                    columns=[
                                        {"name": "ลำดับ", "id": "rank"},
                                        {"name": "Latitude", "id": "lat"},
                                        {"name": "Longitude", "id": "lon"},
                                        {"name": "จำนวนเหตุ", "id": "count"},
                                    ],
                                    data=initial_freq_rows,
                                    style_cell={"padding": "4px", "textAlign": "left"},
                                    style_header={"fontWeight": "bold"},
                                    style_table={"overflowX": "auto"},
                                    page_action="none",
                                ),
                            ]
                        ),
                        className="section-card",
                    ),
                    md=6,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("จุดที่อันตรายที่สุด (Top 3)", className="card-title"),
                                dash_table.DataTable(
                                    id="risk-map-risk-table",
                                    columns=[
                                        {"name": "ลำดับ", "id": "rank"},
                                        {"name": "Latitude", "id": "lat"},
                                        {"name": "Longitude", "id": "lon"},
                                        {"name": "คะแนนความเสี่ยงเฉลี่ย", "id": "avg_risk"},
                                    ],
                                    data=initial_risk_rows,
                                    style_cell={"padding": "4px", "textAlign": "left"},
                                    style_header={"fontWeight": "bold"},
                                    style_table={"overflowX": "auto"},
                                    page_action="none",
                                ),
                            ]
                        ),
                        className="section-card",
                    ),
                    md=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Label("ค้นหาจังหวัด", className="forecast-label"),
                                    dcc.Dropdown(
                                        id="risk-map-province",
                                        options=province_options,
                                        value="ALL",
                                        clearable=False,
                                        placeholder="เลือกจังหวัด",
                                    ),
                                ],
                                md=9,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Search",
                                    id="risk-map-search-btn",
                                    color="primary",
                                    className="forecast-btn w-100",
                                    n_clicks=0,
                                ),
                                md=3,
                                className="d-flex align-items-end",
                            ),
                        ],
                        className="g-3",
                    ),
                    html.Div(
                        id="risk-map-summary",
                        className="mt-3 text-muted",
                        children=initial_summary,
                    ),
                ]
            ),
            className="section-card mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(
                                id="risk-map-graph",
                                figure=initial_fig,
                                className="chart-graph risk-map-graph",
                            )
                        ),
                        className="section-card",
                    ),
                    md=12,
                )
            ],
            className="mb-3",
        ),
    ],
    fluid=True,
    className="page-wrap pb-4",
)


@callback(
    Output("risk-map-graph", "figure"),
    Output("risk-map-freq-table", "data"),
    Output("risk-map-risk-table", "data"),
    Output("risk-map-summary", "children"),
    Input("risk-map-search-btn", "n_clicks"),
    State("risk-map-province", "value"),
)
def apply_risk_map_search(_, province_value):
    if df.empty:
        return _make_empty_map("ไม่พบข้อมูลพิกัดสำหรับสร้าง Risk Map"), [], [], "ไม่พบข้อมูล"

    province_value = province_value or "ALL"

    filtered = _filter_df(df, province_value)
    freq_tbl, risk_tbl = _top_locations(filtered)
    freq_rows, risk_rows = _to_table_rows(freq_tbl, risk_tbl)

    suffix_parts = []
    if province_value != "ALL":
        suffix_parts.append(f"จังหวัด: {province_value}")
    title_suffix = " | ".join(suffix_parts)

    summary = f"พบข้อมูล {len(filtered):,} แถว"
    if suffix_parts:
        summary = f"{summary} ({', '.join(suffix_parts)})"

    focused = province_value != "ALL"
    return _make_map_figure(filtered, title_suffix, focused=focused), freq_rows, risk_rows, summary
