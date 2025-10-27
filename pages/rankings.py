import pandas as pd
import os
import re
from dash import html, dcc, callback, Input, Output, register_page

register_page(__name__, path="/rankings", name="Industry Leaders")

# layout = html.Div([
#     html.H2("Industry Leaders Ranking"),
#     html.P("We can see the top performers in each category and year.")
# ])

# Load dataset once (not inside the callback)
CURRENT_DIR = os.path.dirname(__file__)                         # Get path of current file, without file name pages/
DATA_DIR = os.path.join(CURRENT_DIR, "..", "data")              # .. is go one up, to fuel_project and add data with join
df = pd.read_csv(os.path.join(DATA_DIR, "car_rankings.csv"))    # fuel_project/data/'file_name.csv'

# Get unique years for the dropdown
years = sorted(df["year"].unique(), reverse=True)

# --- Category Icons ---
CATEGORY_ICONS = {
    "Best SUV": "🚙",
    "Best Sedan": "🚗",
    "Best Truck": "🚚",
    "Best Electric Vehicle": "⚡",
    "Best Compact Car": "🏁",
}


# --- Helper: clean duplicate years from model names ---
def clean_model_name(model, year):
    model = str(model)
    year_str = str(year)
    # remove repeated year tokens like "2024 2024 Civic"
    return re.sub(rf"\b{year_str}\s+", "", model).strip()


# --- Layout ---
layout = html.Div(
    [
        html.H2(
            "🏆 Industry Leaders Ranking",
            style={
                "textAlign": "center",
                "fontWeight": "700",
                "fontSize": "2.2rem",
                "color": "#2c3e50",
                "marginBottom": "10px",
            },
        ),
        html.P(
            "Select a year to see the top 5 cars in each category.",
            style={
                "textAlign": "center",
                "fontSize": "1.1rem",
                "marginBottom": "30px",
                "color": "#555",
            },
        ),

        # Year selector
        html.Div(
            dcc.Dropdown(
                id="year-dropdown",
                options=[{"label": str(y), "value": y} for y in years],
                value=years[0],
                clearable=False,
                style={"width": "280px"},
            ),
            style={"display": "flex", "justifyContent": "center", "marginBottom": "40px"},
        ),

        html.Div(id="rankings-content", style={"maxWidth": "950px", "margin": "0 auto"}),
    ],
    style={
        "padding": "30px",
        "backgroundColor": "#ffffff",
        "fontFamily": "Inter, system-ui, sans-serif",
    },
)


# --- Callback ---
@callback(
    Output("rankings-content", "children"),
    Input("year-dropdown", "value")
)
def display_rankings(selected_year):
    filtered = df[df["year"] == selected_year]
    sections = []

    for i, (category, group) in enumerate(filtered.groupby("category")):
        bg_color = "#f9fafc" if i % 2 == 0 else "#ffffff"
        icon = CATEGORY_ICONS.get(category, "🚘")

        car_cards = []
        for _, row in group.iterrows():
            model_name = clean_model_name(row["model"], row["year"])

            card = html.Div(
                [
                    html.Div(
                        f"#{int(row['rank'])}",
                        style={
                            "fontWeight": "600",
                            "color": "#888",
                            "fontSize": "0.9rem",
                            "marginBottom": "6px",
                        },
                    ),
                    html.H4(
                        f"{model_name} — {row['manufacturer']}",
                        style={
                            "margin": "4px 0",
                            "fontWeight": "700",
                            "color": "#2c3e50",
                        },
                    ),
                    html.P(
                        f"Awarded by: {row['source']}" if pd.notna(row["source"]) else "",
                        style={
                            "color": "#444",
                            "fontSize": "0.9rem",
                            "margin": "4px 0 6px 0",
                            "fontStyle": "italic",
                        },
                    ),
                    html.P(
                        row["rationale"],
                        style={
                            "color": "#555",
                            "fontSize": "0.95rem",
                            "marginBottom": "0",
                        },
                    ),
                ],
                style={
                    "border": "1px solid #eaeaea",
                    "borderRadius": "12px",
                    "padding": "16px 20px",
                    "marginBottom": "14px",
                    "backgroundColor": "#fdfdfd",
                    "boxShadow": "0 2px 6px rgba(0,0,0,0.05)",
                    "transition": "transform 0.15s ease, box-shadow 0.15s ease",
                },
                className="car-card"
            )
            car_cards.append(card)

        section = html.Div(
            [
                html.H3(
                    f"{icon} {category}",
                    style={
                        "textAlign": "center",
                        "marginTop": "40px",
                        "marginBottom": "20px",
                        "fontWeight": "700",
                        "color": "#34495e",
                    },
                ),
                html.Div(car_cards, style={"marginBottom": "30px"}),
            ],
            style={
                "backgroundColor": bg_color,
                "padding": "25px 20px",
                "borderRadius": "10px",
                "marginBottom": "25px",
            },
        )
        sections.append(section)

    return sections


# --- Add card hover animation via CSS ---
from dash import Dash

Dash.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .car-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 4px 10px rgba(0,0,0,0.08);
                background-color: #ffffff;
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