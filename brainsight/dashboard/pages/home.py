import dash_bootstrap_components as dbc
import dash_labs as dl
import numpy as np
import pandas as pd
import plotly.express as px
from dash import dcc, html


def read_data():
    data_path = "output/meta.csv"
    data = pd.read_csv(data_path)
    print(data)
    return data


def layout():
    data = read_data()
    fig = px.line(data, x="timestamp", y="AF7", markers=True)
    graph = dcc.Graph(figure=fig)

    return html.Div(["Welcome home!", graph])
