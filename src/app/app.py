from pathlib import Path

from dash import Dash, html, dcc, Input, Output, ctx
import dash_bootstrap_components as dbc

from src.app.pages.overview import layout as overview_layout
from src.app.pages.forecast import layout as forecast_layout
from src.app.pages.risk_map import layout as risk_map_layout

ASSETS_DIR = Path(__file__).resolve().parent / "assets"

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    assets_folder=str(ASSETS_DIR),
    suppress_callback_exceptions=True,
)

app.layout = dbc.Container(
    [
        html.Div(
            [
                html.H2("Road Accident Forecast Dashboard", className="app-title"),
                html.P(
                    "ข้อมูลอุบัติเหตุบนโครงข่ายถนนของกระทรวงคมนาคม ประกอบด้วย อุบัติเหตุที่เกิดขึ้นบนถนนทางหลวง ทางหลวงชนบท และทางด่วน",
                    className="app-subtitle",
                ),
            ],
            className="app-hero",
        ),
        dcc.Tabs(
            id="tabs",
            value="overview",
            className="app-tabs",
            children=[
                dcc.Tab(label="Overview", value="overview"),
                dcc.Tab(label="Forecast", value="forecast"),
                dcc.Tab(label="Risk Map", value="risk_map"),
            ],
            className="app-header my-3",
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.H5("เมนู", className="sidebar-heading"),
                            dbc.Button(
                                [
                                    html.Span("OV", className="side-nav-icon"),
                                    html.Span("Overview", className="side-nav-label"),
                                ],
                                id="btn-overview",
                                n_clicks=0,
                                className="side-nav-btn active",
                            ),
                            dbc.Button(
                                [
                                    html.Span("FC", className="side-nav-icon"),
                                    html.Span("Forecast", className="side-nav-label"),
                                ],
                                id="btn-forecast",
                                n_clicks=0,
                                className="side-nav-btn",
                            ),
                            dbc.Button(
                                [
                                    html.Span("RM", className="side-nav-icon"),
                                    html.Span("Risk Map", className="side-nav-label"),
                                ],
                                id="btn-risk-map",
                                n_clicks=0,
                                className="side-nav-btn",
                            ),
                        ],
                        className="sidebar-panel",
                    ),
                    xs=12,
                    md=3,
                    lg=2,
                    className="mb-3 mb-md-0",
                ),
                dbc.Col(
                    html.Div(id="tab-content", className="page-content-wrap"),
                    xs=12,
                    md=9,
                    lg=10,
                ),
            ],
            className="g-3",
        ),
    ],
    fluid=True,
    className="app-shell py-3 py-md-4",
)


@app.callback(
    Output("tab-content", "children"),
    Output("tab-content", "className"),
    Output("btn-overview", "className"),
    Output("btn-forecast", "className"),
    Output("btn-risk-map", "className"),
    Input("btn-overview", "n_clicks"),
    Input("btn-forecast", "n_clicks"),
    Input("btn-risk-map", "n_clicks"),
)
def render_tab(overview_clicks, forecast_clicks, risk_map_clicks):
    triggered_id = ctx.triggered_id
    page = "overview"

    if triggered_id == "btn-forecast":
        page = "forecast"
    elif triggered_id == "btn-risk-map":
        page = "risk_map"
    elif triggered_id == "btn-overview":
        page = "overview"

    overview_btn = "side-nav-btn active" if page == "overview" else "side-nav-btn"
    forecast_btn = "side-nav-btn active" if page == "forecast" else "side-nav-btn"
    risk_map_btn = "side-nav-btn active" if page == "risk_map" else "side-nav-btn"
    content_class = f"page-content-wrap page-{page}"

    if page == "overview":
        return overview_layout, content_class, overview_btn, forecast_btn, risk_map_btn
    if page == "forecast":
        return forecast_layout, content_class, overview_btn, forecast_btn, risk_map_btn
    return risk_map_layout, content_class, overview_btn, forecast_btn, risk_map_btn


if __name__ == "__main__":
    app.run(debug=True)
