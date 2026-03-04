from dash import Input, Output
import pandas as pd
from ..visualization.charts import (
    province_chart,
    vehicle_chart,
    time_chart,
    map_chart
)

def register_callbacks(app):

    df = pd.read_csv("data/processed/accident_cleaned.csv")

    @app.callback(
        Output("province-chart", "figure"),
        Input("province-filter", "value")
    )
    def update_province_chart(province):

        data = df

        if province:
            data = df[df["province"] == province]

        return province_chart(data)


    @app.callback(
        Output("vehicle-chart", "figure"),
        Input("vehicle-filter", "value")
    )
    def update_vehicle_chart(vehicle):

        data = df

        if vehicle:
            data = df[df["vehicle_type"] == vehicle]

        return vehicle_chart(data)


    @app.callback(
        Output("time-chart", "figure"),
        Input("province-filter", "value")
    )
    def update_time_chart(province):

        data = df

        if province:
            data = df[df["province"] == province]

        return time_chart(data)


    @app.callback(
        Output("map-chart", "figure"),
        Input("province-filter", "value")
    )
    def update_map_chart(province):

        data = df

        if province:
            data = df[df["province"] == province]

        return map_chart(data)