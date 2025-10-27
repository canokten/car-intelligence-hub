from dash import Dash, html, dcc, page_container
import dash_bootstrap_components as dbc

# Initialize app
app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True
)
app.title = "Car Intelligence Hub"

# ---------------------------
# NAVIGATION BAR
# ---------------------------
navbar = html.Div(
    [
        html.H1(
            "Car Intelligence Hub",
            style={
                "textAlign": "center",
                "fontWeight": "700",
                "fontSize": "2.2rem",
                "marginBottom": "10px",
                "color": "#2c3e50",
            },
        ),
        html.Div(
            [
                dcc.Link("Home", href="/", className="nav-link"),
                dcc.Link("Car Search", href="/car-search", className="nav-link"),
                dcc.Link("Industry Leaders", href="/rankings", className="nav-link"),
                # dcc.Link("Market Analysis", href="/market-analysis", className="nav-link"),
                dcc.Link("Find Your Car", href="/myCar", className="nav-link"),
            ],
            style={
                "display": "flex",
                "justifyContent": "center",
                "gap": "25px",
                "flexWrap": "wrap",
                "marginBottom": "20px",
            },
        ),
        html.Hr(
            style={
                "width": "60%",
                "margin": "10px auto 20px auto",
                "borderColor": "#ccc",
            }
        ),
    ],
    style={
        "backgroundColor": "#f8f9fa",
        "padding": "20px",
        "borderBottom": "1px solid #ddd",
        "boxShadow": "0px 2px 6px rgba(0,0,0,0.05)",
    },
)

# ---------------------------
# MAIN LAYOUT
# ---------------------------
app.layout = html.Div(
    [
        navbar,
        html.Div(
            page_container,
            style={
                "maxWidth": "1000px",
                "margin": "0 auto",
                "padding": "30px 20px",
                "textAlign": "center",
                "fontFamily": "Inter, system-ui, sans-serif",
            },
        ),
    ],
    style={
        "backgroundColor": "#ffffff",
        "minHeight": "100vh",
    },
)

# ---------------------------
# CUSTOM CSS STYLES
# ---------------------------
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .nav-link {
                text-decoration: none;
                font-weight: 600;
                color: #007BFF;
                transition: color 0.2s ease, border-bottom 0.2s ease;
            }
            .nav-link:hover {
                color: #0056b3;
                border-bottom: 2px solid #007BFF;
            }
            .nav-link.active {
                color: #2c3e50;
                border-bottom: 3px solid #2c3e50;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

# ---------------------------
# RUN
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)

