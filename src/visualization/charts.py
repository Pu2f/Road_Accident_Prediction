import plotly.express as px

def province_chart(df):

    fig = px.bar(
        df,
        x="province",
        title="Accidents by Province"
    )

    return fig


def vehicle_chart(df):

    fig = px.pie(
        df,
        names="vehicle_type",
        title="Vehicle Type Distribution"
    )

    return fig


def time_chart(df):

    fig = px.histogram(
        df,
        x="hour",
        title="Accidents by Hour"
    )

    return fig


def map_chart(df):

    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        zoom=5
    )

    fig.update_layout(mapbox_style="open-street-map")

    return fig