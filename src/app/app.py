from dash import Dash, html
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    [
        html.H2("Road Accident Forecast Dashboard"),
        html.P("เริ่มต้นระบบสำเร็จ ✅"),
    ],
    fluid=True
)

if __name__ == "__main__":
    app.run(debug=True)