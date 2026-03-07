from pathlib import Path

from dash import Dash, html, dcc, Input, Output
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
                    "Accident analytics, forecasting, and risk insights",
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
        ),
        html.Div(id="tab-content", className="app-content mt-3"),
    ],
    fluid=True,
    className="app-shell py-3 py-md-4",
)


@app.callback(Output("tab-content", "children"), Input("tabs", "value"))
def render_tab(tab):
    if tab == "overview":
        return overview_layout
    if tab == "forecast":
        return forecast_layout
    return risk_map_layout


if __name__ == "__main__":
    app.run(debug=True)
