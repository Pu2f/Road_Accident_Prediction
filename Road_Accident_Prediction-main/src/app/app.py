from dash import Dash
import dash_bootstrap_components as dbc
from src.app.pages.forecast import layout as forecast_layout

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = forecast_layout

if __name__ == "__main__":
    app.run(debug=True)