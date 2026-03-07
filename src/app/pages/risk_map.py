import os
import pandas as pd
import plotly.express as px
from dash import html, dcc
import dash_bootstrap_components as dbc

DATA_PATH = "data/processed/cleaned_accidents.csv"

def load_data():
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()
    df = pd.read_csv(DATA_PATH)

    # กันคอลัมน์ไม่สะอาด
    for c in ["LATITUDE", "LONGITUDE", "รวมจำนวนผู้บาดเจ็บ", "จังหวัด"]:
        if c not in df.columns:
            df[c] = None

    df["LATITUDE"] = pd.to_numeric(df["LATITUDE"], errors="coerce")
    df["LONGITUDE"] = pd.to_numeric(df["LONGITUDE"], errors="coerce")
    df["รวมจำนวนผู้บาดเจ็บ"] = pd.to_numeric(df["รวมจำนวนผู้บาดเจ็บ"], errors="coerce").fillna(0)

    # กรองพิกัดไทยโดยประมาณ
    df = df[df["LATITUDE"].between(5, 21, inclusive="both")]
    df = df[df["LONGITUDE"].between(97, 106, inclusive="both")]

    return df.reset_index(drop=True)

df = load_data()

if len(df) > 15000:
    df_plot = df.sample(15000, random_state=42)  # กันหน้าเว็บหนัก
else:
    df_plot = df.copy()

content = []

if len(df_plot) == 0:
    content.append(dbc.Alert("ไม่พบข้อมูลพิกัดสำหรับทำแผนที่", color="warning"))
else:
    fig_scatter = px.scatter_mapbox(
        df_plot,
        lat="LATITUDE",
        lon="LONGITUDE",
        color="รวมจำนวนผู้บาดเจ็บ",
        size="รวมจำนวนผู้บาดเจ็บ",
        hover_name="จังหวัด",
        hover_data={"LATITUDE": True, "LONGITUDE": True, "รวมจำนวนผู้บาดเจ็บ": True},
        zoom=4.6,
        height=550,
        title="Risk Scatter Map (ขนาด/สีตามจำนวนผู้บาดเจ็บ)",
        color_continuous_scale="Turbo",
        size_max=22,
    )
    fig_scatter.update_layout(mapbox_style="carto-positron", margin=dict(l=0, r=0, t=45, b=0))

    fig_density = px.density_mapbox(
        df_plot,
        lat="LATITUDE",
        lon="LONGITUDE",
        z="รวมจำนวนผู้บาดเจ็บ",
        radius=12,
        zoom=4.6,
        height=550,
        title="Risk Density Heatmap",
        mapbox_style="carto-positron",
        color_continuous_scale="YlOrRd",
    )
    fig_density.update_layout(margin=dict(l=0, r=0, t=45, b=0))

    top_prov = (
        df.groupby("จังหวัด", dropna=False)["รวมจำนวนผู้บาดเจ็บ"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig_top = px.bar(
        top_prov,
        x="จังหวัด",
        y="รวมจำนวนผู้บาดเจ็บ",
        title="Top 10 จังหวัดเสี่ยง (จากผลรวมผู้บาดเจ็บ)",
    )

    content.extend([
        dbc.Row([dbc.Col(dcc.Graph(figure=fig_scatter), md=12)], className="mb-3"),
        dbc.Row([dbc.Col(dcc.Graph(figure=fig_density), md=12)], className="mb-3"),
        dbc.Row([dbc.Col(dcc.Graph(figure=fig_top), md=12)], className="mb-3"),
    ])

layout = dbc.Container(
    [
        html.H3("Risk Map Module"),
        html.P("แผนที่จุดเสี่ยงอุบัติเหตุจากพิกัดจริง + ความหนาแน่น"),
        *content
    ],
    fluid=True
)