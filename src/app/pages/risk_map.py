from dash import html
import dash_bootstrap_components as dbc

layout = dbc.Container(
    [
        html.H3("Risk Map Module"),
        html.P("โมดูลเสริม: แผนที่จุดเสี่ยง (จะเติม heatmap/cluster ในขั้นถัดไป)"),
    ],
    fluid=True
)