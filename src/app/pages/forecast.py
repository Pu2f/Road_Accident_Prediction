from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from src.model.predict import predict_injury

layout = dbc.Container([
    html.H3("Forecast จำนวนผู้บาดเจ็บ"),
    dbc.Row([
        dbc.Col([
            dbc.Label("จังหวัด"),
            dcc.Input(id="province", type="text", value="กรุงเทพมหานคร", className="form-control"),
        ], md=4),
        dbc.Col([
            dbc.Label("สภาพอากาศ"),
            dcc.Input(id="weather", type="text", value="แจ่มใส", className="form-control"),
        ], md=4),
        dbc.Col([
            dbc.Label("ชั่วโมง"),
            dcc.Input(id="hour", type="number", value=18, className="form-control"),
        ], md=4),
    ], className="mb-3"),

    dbc.Row([
        dbc.Col([
            dbc.Label("วันในสัปดาห์ (0=จันทร์)"),
            dcc.Input(id="dow", type="number", value=4, className="form-control"),
        ], md=4),
        dbc.Col([
            dbc.Label("เดือน"),
            dcc.Input(id="month", type="number", value=3, className="form-control"),
        ], md=4),
        dbc.Col([
            dbc.Label("ช่วงเร่งด่วน (0/1)"),
            dcc.Input(id="peak", type="number", value=1, className="form-control"),
        ], md=4),
    ], className="mb-3"),

    dbc.Button("ทำนาย", id="btn-predict", color="primary"),
    html.Hr(),
    html.Div(id="forecast-result", style={"fontSize": "20px", "fontWeight": "bold"})
], fluid=True)

@callback(
    Output("forecast-result", "children"),
    Input("btn-predict", "n_clicks"),
    Input("province", "value"),
    Input("weather", "value"),
    Input("hour", "value"),
    Input("dow", "value"),
    Input("month", "value"),
    Input("peak", "value"),
    prevent_initial_call=True
)
def do_predict(n, province, weather, hour, dow, month, peak):
    row = {
        "จังหวัด": province or "Unknown",
        "สภาพอากาศ": weather or "Unknown",
        "ลักษณะการเกิดเหตุ": "อื่นๆ",
        "มูลเหตุสันนิษฐาน": "ไม่ทราบ",
        "บริเวณที่เกิดเหตุ": "อื่นๆ",
        "hour": hour if hour is not None else 12,
        "day_of_week": dow if dow is not None else 0,
        "month": month if month is not None else 1,
        "is_peak_hour": peak if peak is not None else 0,
        "LATITUDE": 13.7563,
        "LONGITUDE": 100.5018
    }

    y = predict_injury(row)
    return f"คาดการณ์ผู้บาดเจ็บรวม ≈ {y:.2f} คน"