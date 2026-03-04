from dash import html, dcc
import dash_bootstrap_components as dbc

def create_layout():

    sidebar = html.Div(
        className="sidebar",
        children=[
            html.H3("Dashboard"),
            html.Hr(),

            dcc.Dropdown(
                id="province-filter",
                placeholder="Select Province"
            ),

            dcc.Dropdown(
                id="vehicle-filter",
                placeholder="Vehicle Type"
            ),

            html.Br(),

            dbc.Button(
                "Predict Risk",
                id="predict-button",
                color="primary"
            ),

            html.Div(id="prediction-result")
        ]
    )

    main = html.Div(
        className="main",
        children=[
            html.H2("Road Accident Dashboard"),

            dbc.Row([
                dbc.Col(dcc.Graph(id="province-chart")),
                dbc.Col(dcc.Graph(id="vehicle-chart"))
            ]),

            dbc.Row([
                dbc.Col(dcc.Graph(id="time-chart")),
                dbc.Col(dcc.Graph(id="map-chart"))
            ])
        ]
    )

    return html.Div([
        dbc.Row([
            dbc.Col(sidebar, width=3),
            dbc.Col(main, width=9)
        ])
    ])