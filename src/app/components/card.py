from dash import dcc
import dash_bootstrap_components as dbc


def chart_card(fig, class_name: str = "section-card"):
	return dbc.Card(
		dbc.CardBody(dcc.Graph(figure=fig, className="chart-graph")),
		className=class_name,
	)


def kpi_card(label: str, value: str, class_name: str = "kpi-card"):
	return dbc.Card(
		dbc.CardBody(
			[
				dbc.Label(label, className="kpi-label"),
				dbc.CardText(value, className="kpi-value"),
			]
		),
		className=class_name,
	)
