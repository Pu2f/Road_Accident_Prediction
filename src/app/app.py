from src.app.pages.risk_map import layout as risk_map_layout
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

from src.app.pages.overview import layout as overview_layout
from src.app.pages.forecast import layout as forecast_layout
from src.app.pages.risk_map import layout as risk_map_layout

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    [
        html.H2("Road Accident Forecast Dashboard", className="my-3"),
        dcc.Tabs(
            id="tabs",
            value="overview",
            children=[
                dcc.Tab(label="Overview", value="overview"),
                dcc.Tab(label="Forecast", value="forecast"),
                dcc.Tab(label="Risk Map", value="risk_map"),
            ],
        ),
        html.Div(id="tab-content", className="mt-3"),
    ],
    fluid=True,
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