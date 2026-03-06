import os
import pandas as pd
import plotly.express as px
from dash import html, dcc
import dash_bootstrap_components as dbc

DATA_PATH = "data/processed/cleaned_accidents.csv"
PRED_PATH = "artifacts/predictions_sample.csv"  # จะสร้างจาก model branch

def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    return pd.DataFrame()

def load_pred():
    if os.path.exists(PRED_PATH):
        return pd.read_csv(PRED_PATH)
    return pd.DataFrame()

df = load_data()
pred_df = load_pred()

cards = dbc.Row(
    [
        dbc.Col(dbc.Card(dbc.CardBody([html.H5("จำนวนแถวข้อมูล"), html.H3(f"{len(df):,}")]))),
        dbc.Col(dbc.Card(dbc.CardBody([html.H5("จำนวนจังหวัด"), html.H3(f"{df['จังหวัด'].nunique() if 'จังหวัด' in df.columns else 0:,}")]))),
        dbc.Col(dbc.Card(dbc.CardBody([html.H5("บาดเจ็บรวมเฉลี่ย"), html.H3(f"{df['รวมจำนวนผู้บาดเจ็บ'].mean():.2f}" if 'รวมจำนวนผู้บาดเจ็บ' in df.columns and len(df) else "N/A")]))),
    ],
    className="mb-3"
)

graphs = []

if len(df) and "จังหวัด" in df.columns:
    top_province = df["จังหวัด"].value_counts().head(10).reset_index()
    top_province.columns = ["จังหวัด", "จำนวนเหตุ"]
    fig_province = px.bar(top_province, x="จังหวัด", y="จำนวนเหตุ", title="Top 10 จังหวัดที่เกิดอุบัติเหตุสูง")
    graphs.append(dcc.Graph(figure=fig_province))

if len(df) and "hour" in df.columns:
    hour_count = df["hour"].value_counts().sort_index().reset_index()
    hour_count.columns = ["hour", "จำนวนเหตุ"]
    fig_hour = px.line(hour_count, x="hour", y="จำนวนเหตุ", markers=True, title="จำนวนอุบัติเหตุตามชั่วโมง")
    graphs.append(dcc.Graph(figure=fig_hour))

if len(pred_df) and {"actual", "predicted"}.issubset(pred_df.columns):
    fig_ap = px.scatter(pred_df, x="actual", y="predicted", trendline="ols", title="Actual vs Predicted")
    graphs.append(dcc.Graph(figure=fig_ap))

layout = dbc.Container(
    [
        html.H3("Overview Dashboard"),
        html.P("ภาพรวมข้อมูลอุบัติเหตุและผลโมเดล"),
        cards,
        *graphs
    ],
    fluid=True
)