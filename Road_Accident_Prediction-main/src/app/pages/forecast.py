from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from src.model.predict import predict_injury

layout = dbc.Container(
    [
        html.H3("Forecast จำนวนผู้บาดเจ็บ"),
        html.P("กรอกพารามิเตอร์รอบข้างเพื่อคาดการณ์"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("จังหวัด"),
                        dcc.Input(id="province", type="text", value="กรุงเทพมหานคร", className="form-control"),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        dbc.Label("สภาพอากาศ"),
                        dcc.Input(id="weather", type="text", value="แจ่มใส", className="form-control"),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        dbc.Label("ชั่วโมง (0-23)"),
                        dcc.Input(id="hour", type="number", value=18, className="form-control"),
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
                        dcc.Input(id="dow", type="number", value=4, className="form-control"),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        dbc.Label("เดือน (1-12)"),
                        dcc.Input(id="month", type="number", value=3, className="form-control"),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        dbc.Label("ช่วงเร่งด่วน (0/1)"),
                        dcc.Input(id="peak", type="number", value=1, className="form-control"),
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