import os
import numpy as np
import pandas as pd
import plotly.express as px
from dash import html, dcc, dash_table
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


freq_tbl, risk_tbl = _top_locations(df)

if len(df) > 18000:
    df_plot = df.sample(18000, random_state=42)
else:
    df_plot = df.copy()

content = []

if df_plot.empty:
    content.append(dbc.Alert("ไม่พบข้อมูลพิกัดสำหรับสร้าง Risk Map", color="warning"))
else:
    # 1) Summary cards for most frequent / most dangerous locations
    if not freq_tbl.empty and not risk_tbl.empty:
        summary_card = dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5(
                                    "จุดที่เกิดเหตุมากที่สุด (Top 3)", className="card-title"
                                ),
                                dash_table.DataTable(
                                    columns=[
                                        {"name": "ลำดับ", "id": "rank"},
                                        {"name": "Latitude", "id": "lat"},
                                        {"name": "Longitude", "id": "lon"},
                                        {"name": "จำนวนเหตุ", "id": "count"},
                                    ],
                                    data=[
                                        {
                                            "rank": i + 1,
                                            "lat": f"{row['lat_bin']:.4f}",
                                            "lon": f"{row['lon_bin']:.4f}",
                                            "count": int(row["count"]),
                                        }
                                        for i, row in freq_tbl.reset_index(
                                            drop=True
                                        ).iterrows()
                                    ],
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
                                    columns=[
                                        {"name": "ลำดับ", "id": "rank"},
                                        {"name": "Latitude", "id": "lat"},
                                        {"name": "Longitude", "id": "lon"},
                                        {"name": "คะแนนความเสี่ยงเฉลี่ย", "id": "avg_risk"},
                                    ],
                                    data=[
                                        {
                                            "rank": i + 1,
                                            "lat": f"{row['lat_bin']:.4f}",
                                            "lon": f"{row['lon_bin']:.4f}",
                                            "avg_risk": f"{row['avg_risk']:.1f}",
                                        }
                                        for i, row in risk_tbl.reset_index(
                                            drop=True
                                        ).iterrows()
                                    ],
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
        )
        content.append(summary_card)

    # 2) Discrete level map (อธิบายง่ายเวลา present)
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
        hover_data={"risk_score": ":.2f", "LATITUDE": ":.4f", "LONGITUDE": ":.4f"},
        zoom=4.8,
        height=720,
        mapbox_style="carto-positron",
        title="Risk Level Map (Low / Medium / High)",
        opacity=0.6,
    )
    fig_level.update_traces(marker={"size": 6})
    fig_level.update_layout(
        margin=dict(l=0, r=0, t=50, b=0), legend_title_text="Risk Level"
    )

    content.append(
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(
                                figure=fig_level,
                                className="chart-graph risk-map-graph",
                            )
                        ),
                        className="section-card",
                    ),
                    md=12,
                )
            ],
            className="mb-3",
        )
    )

layout = dbc.Container(
    [
        html.H3("Risk Map Module"),
        html.P(
            "Risk Score (0-100) คำนวณจากการผสาน 3 ปัจจัยหลัก ได้แก่ ความรุนแรงของเหตุการณ์ "
            "(จำนวนผู้บาดเจ็บ + น้ำหนักผู้เสียชีวิต), ความถี่การเกิดซ้ำในพื้นที่ใกล้เคียง (area frequency), "
            "และการเกิดเหตุในช่วงเวลาเร่งด่วน (is_peak_hour)",
            className="section-subtitle",
        ),
        *content,
    ],
    fluid=True,
    className="page-wrap pb-4",
)
