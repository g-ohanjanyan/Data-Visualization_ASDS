from dash import Dash, html, page_container
import dash_bootstrap_components as dbc

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.CYBORG]
)

server = app.server
app.title = "Non-Cash Dashboard"

app.layout = dbc.Container([
    dbc.NavbarSimple(
        brand="Non-Cash Dashboard",
        color="dark",
        dark=True,
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.NavItem(dbc.NavLink("Overview", href="/overview"))
        ]
    ),
    html.Br(),
    page_container
], fluid=True)

if __name__ == "__main__":
    app.run(debug=True)
