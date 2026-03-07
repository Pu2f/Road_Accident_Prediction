from pathlib import Path

import pandas as pd
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from src.model.predict import predict_injury


PROCESSED_DATA_PATH = Path("data/processed/cleaned_accidents.csv")


def _text_options(column_name: str, fallback_values: list[str]) -> list[dict]:
    if PROCESSED_DATA_PATH.exists():
        try:
            df = pd.read_csv(PROCESSED_DATA_PATH, usecols=[column_name], dtype={column_name: "string"})
            values = (
                df[column_name]
                .dropna()
                .astype("string")
                .str.strip()
                .replace("", pd.NA)
                .dropna()
            )
            unique_values = sorted(v for v in values.unique().tolist() if v != "Unknown")
            if unique_values:
                return [{"label": v, "value": v} for v in unique_values]
        except Exception:
            pass

    return [{"label": v, "value": v} for v in fallback_values]


def _move_option_to_end(options: list[dict], value_to_move: str) -> list[dict]:
    kept = [o for o in options if o["value"] != value_to_move]
    moved = [o for o in options if o["value"] == value_to_move]
    return kept + moved


PROVINCE_OPTIONS = _text_options("จังหวัด", ["กรุงเทพมหานคร"])
WEATHER_OPTIONS = _text_options("สภาพอากาศ", ["แจ่มใส"])
WEATHER_OPTIONS = _move_option_to_end(WEATHER_OPTIONS, "อื่นๆ")
HOUR_OPTIONS = [{"label": str(h), "value": h} for h in range(24)]
DOW_OPTIONS = [
    {"label": "จันทร์ (0)", "value": 0},
    {"label": "อังคาร (1)", "value": 1},
    {"label": "พุธ (2)", "value": 2},
    {"label": "พฤหัสบดี (3)", "value": 3},
    {"label": "ศุกร์ (4)", "value": 4},
    {"label": "เสาร์ (5)", "value": 5},
    {"label": "อาทิตย์ (6)", "value": 6},
]
MONTH_OPTIONS = [{"label": str(m), "value": m} for m in range(1, 13)]
PEAK_OPTIONS = [
    {"label": "ไม่ใช่ช่วงเร่งด่วน (0)", "value": 0},
    {"label": "ช่วงเร่งด่วน (1)", "value": 1},
]

DEFAULT_PROVINCE = "กรุงเทพมหานคร" if any(o["value"] == "กรุงเทพมหานคร" for o in PROVINCE_OPTIONS) else PROVINCE_OPTIONS[0]["value"]
DEFAULT_WEATHER = "แจ่มใส" if any(o["value"] == "แจ่มใส" for o in WEATHER_OPTIONS) else WEATHER_OPTIONS[0]["value"]

layout = dbc.Container(
    [
        html.H3("Forecast จำนวนผู้บาดเจ็บ"),
        html.P("กรอกพารามิเตอร์รอบข้างเพื่อคาดการณ์"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("จังหวัด"),
                        dcc.Dropdown(
                            id="province",
                            options=PROVINCE_OPTIONS,
                            value=DEFAULT_PROVINCE,
                            clearable=False,
                            searchable=True,
                        ),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        dbc.Label("สภาพอากาศ"),
                        dcc.Dropdown(
                            id="weather",
                            options=WEATHER_OPTIONS,
                            value=DEFAULT_WEATHER,
                            clearable=False,
                            searchable=True,
                        ),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        dbc.Label("ชั่วโมง (0-23)"),
                        dcc.Dropdown(id="hour", options=HOUR_OPTIONS, value=18, clearable=False),
                    ],
                    md=4,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("วันในสัปดาห์ (0=จันทร์)"),
                        dcc.Dropdown(id="dow", options=DOW_OPTIONS, value=4, clearable=False),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        dbc.Label("เดือน (1-12)"),
                        dcc.Dropdown(id="month", options=MONTH_OPTIONS, value=3, clearable=False),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        dbc.Label("ช่วงเร่งด่วน (0/1)"),
                        dcc.Dropdown(id="peak", options=PEAK_OPTIONS, value=1, clearable=False),
                    ],
                    md=4,
                ),
            ],
            className="mb-3",
        ),
        dbc.Button("ทำนาย", id="btn-predict", color="primary"),
        html.Hr(),
        html.Div(id="forecast-result", style={"fontSize": "22px", "fontWeight": "bold"}),
    ],
    fluid=True,
)


@callback(
    Output("forecast-result", "children"),
    Input("btn-predict", "n_clicks"),
    Input("province", "value"),
    Input("weather", "value"),
    Input("hour", "value"),
    Input("dow", "value"),
    Input("month", "value"),
    Input("peak", "value"),
    prevent_initial_call=True,
)
def do_predict(n_clicks, province, weather, hour, dow, month, peak):
    row = {
        "จังหวัด": province,
        "สภาพอากาศ": weather,
        "hour": hour,
        "day_of_week": dow,
        "month": month,
        "is_peak_hour": peak,
    }
    pred = predict_injury(row)
    return f"คาดการณ์ผู้บาดเจ็บรวม ≈ {pred:.2f} คน"