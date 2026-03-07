import os
import pandas as pd
import plotly.express as px
from dash import html, dcc
import dash_bootstrap_components as dbc

DATA_PATH = "data/processed/cleaned_accidents.csv"
PRED_PATH = "artifacts/predictions_sample.csv"


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

cards = dbc.Row(
    [
        dbc.Col(
            dbc.Card(dbc.CardBody([html.H5("จำนวนแถวข้อมูล"), html.H3(f"{len(df):,}")]))
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("จำนวนจังหวัด"),
                        html.H3(
                            f"{df['จังหวัด'].nunique() if 'จังหวัด' in df.columns else 0:,}"
                        ),
                    ]
                )
            )
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("บาดเจ็บรวมเฉลี่ย"),
                        html.H3(
                            f"{pd.to_numeric(df['รวมจำนวนผู้บาดเจ็บ'], errors='coerce').mean():.2f}"
                            if "รวมจำนวนผู้บาดเจ็บ" in df.columns and len(df)
                            else "N/A"
                        ),
                    ]
                )
            )
        ),
    ],
    className="mb-3",
)

graphs = []

if len(df) and "จังหวัด" in df.columns:
    top_province = (
        df["จังหวัด"].fillna("ไม่ระบุ").astype(str).value_counts().head(10).reset_index()
    )
    top_province.columns = ["จังหวัด", "จำนวนเหตุ"]
    fig_province = px.bar(
        top_province,
        x="จังหวัด",
        y="จำนวนเหตุ",
        color="จังหวัด",
        color_discrete_sequence=px.colors.qualitative.Set3,
        title="Top 10 จังหวัดที่เกิดอุบัติเหตุสูง",
    )
    fig_province.update_layout(showlegend=False)
    graphs.append(dcc.Graph(figure=fig_province))

if len(df) and "hour" in df.columns:
    hour_series = pd.to_numeric(df["hour"], errors="coerce").dropna().astype(int)
    if len(hour_series):
        hour_count = hour_series.value_counts().sort_index().reset_index()
        hour_count.columns = ["hour", "จำนวนเหตุ"]
        fig_hour = px.line(
            hour_count,
            x="hour",
            y="จำนวนเหตุ",
            markers=True,
            title="จำนวนอุบัติเหตุตามชั่วโมง",
        )
        graphs.append(dcc.Graph(figure=fig_hour))

# ✅ pie chart ต้องอยู่ก่อนสร้าง layout
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

    fig_vehicle_pie = px.pie(
        vehicle_count,
        names="ประเภทรถ",
        values="จำนวนเหตุ",
        title="สัดส่วนประเภทรถที่เกิดอุบัติเหตุ",
        hole=0.35,
    )
    fig_vehicle_pie.update_traces(
        textinfo="none", hoverinfo="label+percent", sort=False
    )
    fig_vehicle_pie.update_layout(uniformtext_minsize=10, uniformtext_mode="hide")
    graphs.append(dcc.Graph(figure=fig_vehicle_pie))

if len(pred_df) and {"actual", "predicted"}.issubset(pred_df.columns):
    fig_ap = px.scatter(
        pred_df,
        x="actual",
        y="predicted",
        trendline="ols",
        title="Actual vs Predicted",
    )
    graphs.append(dcc.Graph(figure=fig_ap))

layout = dbc.Container(
    [
        html.H3("Overview Dashboard"),
        html.P("ภาพรวมข้อมูลอุบัติเหตุและผลโมเดล"),
        html.P(data_year_text, className="text-muted"),
        cards,
        *graphs,
    ],
    fluid=True,
)
