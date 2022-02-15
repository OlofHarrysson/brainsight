import dash
import dash_bootstrap_components as dbc
import dash_labs as dl
from brainsight.dashboard.pages import home, secret
from dash_extensions import WebSocket

from stream_data import stream_data


def main():
    app = dash.Dash(
        __name__,
        plugins=[dl.plugins.pages],
        external_stylesheets=[dbc.themes.BOOTSTRAP],
    )

    dash.register_page("home", path="/", layout=home.layout())
    dash.register_page("secret", path="/secret", layout=secret.layout())

    navbar = dbc.NavbarSimple(
        dbc.Nav(
            [
                dbc.NavLink(page["name"], href=page["path"])
                for page in dash.page_registry.values()
                if page.get("top_nav")
            ],
        ),
        brand="Multi Page App Demo",
        color="primary",
        dark=True,
        className="mb-2",
    )

    app.layout = dbc.Container(
        [
            navbar,
            dl.plugins.page_container,
            WebSocket(url="wss://echo.websocket.org", id="ws"),
        ],
        fluid=True,
    )

    # print("Connecting to EEG device...")
    # stream_data()
    app.run_server(debug=True)


if __name__ == "__main__":
    main()
