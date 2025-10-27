"""
CarWise AI — Dash (Step 2.6: Minor UI Fixes + Better Reset Behavior)
"""

import os, json, re
import pandas as pd
from dash import Dash, html, dcc, Input, Output, State, no_update, callback
from dotenv import load_dotenv

# car_app/pages/car_search.py
from dash import register_page

register_page(__name__, path="/car-search", name="Car Search")

# ---------- Config ----------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

DATA_DIR = "data"
DEFAULT_ANNUAL_DISTANCE = 15000
DEFAULT_FUEL_PRICE = 1.80
DEFAULT_ELECTRICITY_PRICE = 0.14

# ---------- Load local datasets ----------
def load_vehicle_dataframe(vehicle_type: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, f"{vehicle_type}.csv")
    return pd.read_csv(path)

CACHED_DATA = {vt: load_vehicle_dataframe(vt) for vt in ["conventional", "phev", "bev"]}

# ---------- Timestamp ----------
LAST_UPDATED_PATH = os.path.join(DATA_DIR, "last_updated.txt")
if os.path.exists(LAST_UPDATED_PATH):
    with open(LAST_UPDATED_PATH, "r") as f:
        LAST_UPDATED = f.read().strip()
else:
    LAST_UPDATED = "Data Last updated: Unknown"

# ---------- OpenAI ----------
try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except Exception:
    openai_client = None

def get_vehicle_summary(make: str, model: str, year: str) -> str:
    if not openai_client:
        return f"The {year} {make} {model} is a popular model. (No API key configured)"
    prompt = (
        f"You are an automotive advisor for Canadian buyers. Act like a car nerd. "
        f"In 2–3 sentences, summarize the {year} {make} {model} focusing on the general public view, performance, reliability, "
        f"and everyday usability — what it's good for and what it's not ideal for. "
        f"Keep it neutral, concise, and friendly."
    )
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"(Summary unavailable: {e})"
    

def get_vehicle_price(make: str, model: str, year: str):
    """
    Uses GPT to estimate both:
      - Retail price (current or discontinued MSRP)
      - Second-hand price range (min–max CAD)
    Returns a dict:
      {
        "retail_text": "Retail Price (Discontinued): $42,000 CAD",
        "used_text": "Used Market: $18,000–$28,000 CAD"
      }
    """
    if not openai_client:
        return {"retail_text": "Price unavailable (no API key).", "used_text": ""}

    prompt = (
        f"You are an automotive market analyst. For the {year} {make} {model}, "
        f"give two brief price lines in Canadian dollars:\n"
        f"1. Retail Price: if still sold new, give 'Retail Price: $XX,XXX CAD'; "
        f"if discontinued, give 'Retail Price (Discontinued): $XX,XXX CAD'.\n"
        f"2. Used Market: give a reasonable used market range (e.g. '$15,000–$25,000 CAD'), "
        f"based on typical Canadian listings, condition, and mileage. "
        f"If too new or unavailable second-hand, write 'Used Market: unavailable'.\n"
        f"Be concise, formatted as plain text with exactly two lines."
    )
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        lines = [line.strip() for line in resp.choices[0].message.content.split("\n") if line.strip()]
        retail = lines[0] if len(lines) > 0 else "Retail Price: unavailable"
        used = lines[1] if len(lines) > 1 else "Used Market: unavailable"
        return {"retail_text": retail, "used_text": used}
    except Exception as e:
        return {"retail_text": f"(Price unavailable: {e})", "used_text": ""}



def get_vehicle_kpis(make: str, model: str, year: str, price_context: str):
    """
    Uses GPT to provide 1–10 scores for key KPIs: Performance, Value, Reliability, Eco-Friendliness.
    Accepts a full price context string (e.g., 'Retail Price: $40,000 | Used Market: $20,000–$25,000').
    """
    if not openai_client:
        return None

    prompt = (
        f"You are an automotive expert reviewing the {year} {make} {model}. "
        f"Rate it on a 1–10 scale for (can be float like 8.5, 9.5, 4.5):\n"
        f"- Performance (acceleration, handling, top speed)\n"
        f"- Value for Money (price vs quality, efficiency, features)\n"
        f"- Reliability (mechanical dependability, repair frequency, maintenance cost)\n"
        f"- Eco-Friendliness (fuel economy AND CO₂ emissions)\n\n"

        f"Interpretation guide:\n"
        f"7 = average for its class, 8–9 = excellent, 10 = exceptional or class-leading, "
        f"5–6 = below average, 1–4 = poor. Be realistic and fair — do not exaggerate.\n\n"

        f"Performance:\n"
        f"10 → supercar / hypercar (0–100 km/h under 3.0s, top speed >300 km/h)\n"
        f"8–9 → high-performance sports cars (0–100 km/h 3.5–4.0s)\n"
        f"7 → sporty or strong performance\n"
        f"5–6 → typical everyday vehicle\n"
        f"1–4 → slow or underpowered.\n\n"

        f"Reliability:\n"
        f"10 → extremely dependable (e.g., Toyota, Lexus, Volvo)\n"
        f"7–8 → good reliability with minor or infrequent issues (e.g., premium or exotic cars like Porsche, Lamborghini — "
        f"high build quality but costly parts)\n"
        f"5–6 → average reliability\n"
        f"1–4 → poor reliability or frequent major repairs.\n\n"

        f"Eco-Friendliness:\n"
        f"10 → zero tailpipe emissions (EV)\n"
        f"7–9 → hybrids and very efficient gas vehicles\n"
        f"5–6 → moderate fuel use (around 8–10 L/100 km)\n"
        f"1–4 → inefficient or high CO₂ vehicles (>12 L/100 km or >250 g/km CO₂).\n\n"

        f"Always include numeric details in explanations where possible: engine size (L), cylinder count, "
        f"horsepower, 0–100 km/h acceleration, top speed, fuel economy (L/100 km or mpg), and CO₂ emissions (g/km). "
        f"If exact data isn't available, estimate realistically based on vehicle type and class.\n\n"

        f"Keep explanations short (one sentence, two at most), factual, and neutral — no marketing tone.\n\n"

        f"Return only a valid JSON object. Example:\n"
        f'{{"performance": 10, "value": 6, "reliability": 7, "eco": 3, '
        f'"explanations": {{"performance": "5.2L V10, 0–100 km/h in 2.9s, top 310 km/h.", '
        f'"value": "Very expensive but extreme performance.", '
        f'"reliability": "High-quality engineering but costly servicing.", '
        f'"eco": "13.5 L/100 km, 320 g/km CO₂."}}}}'
    )
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return json.loads(resp.choices[0].message.content.strip())
    except Exception as e:
        return {"error": str(e)}
    

# ---------- Dash Layout ----------
# app = Dash(__name__)
# app.title = "CarWise AI — MVP"

vehicle_options = [
    {"label": "Conventional (Gas/Diesel)", "value": "conventional"},
    {"label": "Plug-in Hybrid (PHEV)", "value": "phev"},
    {"label": "Battery Electric (BEV)", "value": "bev"},
]

layout = html.Div(
    style={"maxWidth": 960, "margin": "40px auto", "fontFamily": "system-ui, sans-serif"},
    children=[
        html.H1("CarWise AI — MVP"),
        html.P("Vehicle summary + annual fuel or electricity cost estimator."),
        html.P(LAST_UPDATED, style={"color": "#666", "fontStyle": "italic"}),

        # ---------- Selection ----------
        html.Div([
            html.Label("Vehicle Type:"),
            dcc.Dropdown(id="vehicle-type", options=vehicle_options, value="conventional", clearable=False),
        ]),
        html.Br(),
        html.Div([
            html.Label("Model Year:"),
            dcc.Dropdown(id="year-dropdown", placeholder="Select a year"),
        ]),
        html.Br(),
        html.Div([
            html.Label("Make:"),
            dcc.Dropdown(id="make-dropdown", placeholder="Select a make"),
        ]),
        html.Br(),
        html.Div([
            html.Label("Vehicle Class:"),
            dcc.Dropdown(id="class-dropdown", placeholder="Select a vehicle class"),
        ]),
        html.Br(),
        html.Div([
            html.Label("Model:"),
            dcc.Dropdown(id="model-dropdown", placeholder="Select a model"),
        ]),
        html.Br(),
        html.Button("Get Summary", id="go", n_clicks=0),
        html.Hr(),

        html.Div(id="summary-block"),
        html.Div(id="price-block", style={"marginTop": "20px"}),
        html.Div(id="kpi-block", style={"marginTop": "20px"}),

        # ---------- Estimator ----------
        html.Div(
            id="fuel-section",
            style={"display": "none"},
            children=[
                html.H3("Annual Energy Cost Estimator"),
                html.Label("City driving ratio (%)"),
                dcc.Slider(
                    id="city-ratio",
                    min=0,
                    max=100,
                    step=5,
                    value=80,
                    marks=None,
                    tooltip={"placement": "bottom"},
                ),
                html.Br(),
                html.Label(id="price-label"),
                dcc.Input(
                    id="energy-price",
                    type="number",
                    value=DEFAULT_FUEL_PRICE,
                    step=0.01,
                    style={"width": "150px", "marginLeft": "8px"},
                ),
                html.P(
                    id="price-default-note",
                    style={"color": "#666", "fontSize": 13, "marginTop": "2px"},
                ),
                html.Br(),
                html.Label("Annual distance (km)"),
                dcc.Input(
                    id="annual-distance",
                    type="number",
                    value=DEFAULT_ANNUAL_DISTANCE,
                    step=500,
                    style={"width": "150px", "marginLeft": "8px"},
                ),
                html.P(
                    f"Default is {DEFAULT_ANNUAL_DISTANCE:,} km/year",
                    style={"color": "#666", "fontSize": 13, "marginTop": "2px"},
                ),
                html.Div(id="fuel-cost-output", style={"marginTop": "12px", "fontWeight": "600"}),
            ],
        ),

        dcc.Store(id="session-cache", storage_type="memory"),
    ],
)

# ---------- Callbacks ----------

# Reset all dropdowns when dataset changes
@callback(
    Output("year-dropdown", "value"),
    Output("make-dropdown", "value"),
    Output("class-dropdown", "value"),
    Output("model-dropdown", "value"),
    Input("vehicle-type", "value"),
)
def reset_dropdowns_on_dataset_change(vehicle_type):
    return None, None, None, None


@callback(
    Output("year-dropdown", "options"),
    Input("vehicle-type", "value"),
)
def update_years(vehicle_type):
    df = CACHED_DATA.get(vehicle_type, pd.DataFrame())
    if "model_year" in df.columns:
        years = sorted(df["model_year"].dropna().unique().tolist())
        return [{"label": str(y), "value": str(y)} for y in years]
    return []


@callback(
    Output("make-dropdown", "options"),
    Input("year-dropdown", "value"),
    State("vehicle-type", "value"),
)
def update_makes(year, vehicle_type):
    if not year:
        return []
    df = CACHED_DATA.get(vehicle_type, pd.DataFrame())
    df = df[df["model_year"].astype(str) == str(year)]
    makes = sorted(df["make"].dropna().unique().tolist()) if "make" in df.columns else []
    return [{"label": m, "value": m} for m in makes]

@callback(
    Output("class-dropdown", "options"),
    Input("make-dropdown", "value"),
    State("year-dropdown", "value"),
    State("vehicle-type", "value"),
)
def update_vehicle_classes(make, year, vehicle_type):
    """Populate available vehicle classes for the chosen year & make."""
    if not (make and year):
        return []
    df = CACHED_DATA.get(vehicle_type, pd.DataFrame())
    df = df[(df["model_year"].astype(str) == str(year)) & (df["make"] == make)]
    if "vehicle_class" in df.columns:
        classes = sorted(df["vehicle_class"].dropna().unique().tolist())
        return [{"label": c, "value": c} for c in classes]
    return []


@callback(
    Output("model-dropdown", "options"),
    Input("class-dropdown", "value"),
    State("make-dropdown", "value"),
    State("year-dropdown", "value"),
    State("vehicle-type", "value"),
)
def update_models(vehicle_class, make, year, vehicle_type):
    """Populate model dropdown filtered by year, make, and vehicle class."""
    if not (make and year):
        return []
    df = CACHED_DATA.get(vehicle_type, pd.DataFrame())
    df = df[(df["model_year"].astype(str) == str(year)) & (df["make"] == make)]
    if vehicle_class:
        df = df[df["vehicle_class"] == vehicle_class]
    models = sorted(df["model"].dropna().unique().tolist()) if "model" in df.columns else []
    return [{"label": m, "value": m} for m in models]


@callback(
    Output("summary-block", "children"),
    Output("price-block", "children"),
    Output("kpi-block", "children"),
    Output("fuel-section", "style"),
    Output("session-cache", "data"),
    Output("price-label", "children"),
    Output("energy-price", "value"),
    Output("price-default-note", "children"),
    Input("go", "n_clicks"),
    State("vehicle-type", "value"),
    State("year-dropdown", "value"),
    State("make-dropdown", "value"),
    State("model-dropdown", "value"),
    prevent_initial_call=True,
)
def handle_generate(n, vehicle_type, year, make, model):
    if not (year and make and model):
        return (
            html.P("Please select Year, Make, and Model."),
            "", "", {"display": "none"}, no_update, "", no_update, ""
        )

    # --- Summary
    summary_text = get_vehicle_summary(make, model, year)
    summary_children = [
        html.H3(f"{year} {make} {model}"),
        html.P(summary_text)
    ]

     # --- Price
    price_info = get_vehicle_price(make, model, year)

    price_block = html.Div([
        html.H4("Price Estimates"),
        html.P(price_info["retail_text"], style={"fontWeight": "600", "marginBottom": "4px"}),
        html.P(price_info["used_text"], style={"fontWeight": "600", "marginBottom": "4px", "color": "#333"}),
    ])

    # --- KPIs
    # Use price_info context for better "value" estimation
    price_context = f"{price_info['retail_text']} | {price_info['used_text']}"
    kpi_data = get_vehicle_kpis(make, model, year, price_context)

    def color_for_score(score: float) -> str:
        """Return color hex based on score range."""
        try:
            score = float(score)
        except Exception:
            return "#bdc3c7"  # neutral gray if no valid score
        if score <= 4:
            return "#e74c3c"  # red
        elif score <= 6:
            return "#f39c12"  # orange
        elif score <= 7:
            return "#f1c40f"  # yellow
        elif score <= 8:
            return "#2ecc71"  # light green
        else:
            return "#27ae60"  # dark green

    if not kpi_data or "error" in kpi_data:
        kpi_block = html.P("KPI data unavailable.")
    else:
        kpi_cards = []
        for key in ["performance", "value", "reliability", "eco"]:
            score = kpi_data.get(key, "–")
            exp = kpi_data.get("explanations", {}).get(key, "")
            label = key.capitalize() if key != "eco" else "Eco-Friendliness"
            color = color_for_score(score)

            kpi_cards.append(
                html.Div(
                    style={
                        "border": f"2px solid {color}",
                        "borderRadius": "10px",
                        "padding": "12px",
                        "margin": "8px",
                        "flex": "1 1 200px",
                        "boxShadow": "0 2px 6px rgba(0,0,0,0.1)",
                        "backgroundColor": "white",
                        "textAlign": "center",
                    },
                    children=[
                        html.H5(label, style={"marginBottom": "6px", "color": "#333"}),
                        html.H2(f"{score}/10", style={"margin": "0", "color": color}),
                        html.P(exp, style={
                            "fontSize": "0.9em",
                            "color": "#555",
                            "marginTop": "6px",
                            "lineHeight": "1.3em"
                        }),
                    ],
                )
            )

        kpi_block = html.Div([
            html.H4("Vehicle Scores", style={"marginBottom": "10px", "color": "#222"}),
            html.Div(
                kpi_cards,
                style={
                    "display": "flex",
                    "flexWrap": "wrap",
                    "justifyContent": "flex-start",
                    "alignItems": "stretch",
                    "gap": "10px"
                }
            )
        ])



    # --- Fuel section setup
    if vehicle_type == "bev":
        label = "Electricity price (CAD per kWh):"
        default_note = f"Default is {DEFAULT_ELECTRICITY_PRICE:.2f} CAD/kWh (national average)"
        price_value = DEFAULT_ELECTRICITY_PRICE
    else:
        label = "Fuel price (CAD per litre):"
        default_note = f"Default is {DEFAULT_FUEL_PRICE:.2f} CAD/L"
        price_value = DEFAULT_FUEL_PRICE

    cache_payload = {"vehicle_type": vehicle_type, "year": year, "make": make, "model": model}

    return (
        summary_children,
        price_block,
        kpi_block,
        {"display": "block"},
        cache_payload,
        label,
        price_value,
        default_note,
    )


@callback(
    Output("fuel-cost-output", "children"),
    Input("city-ratio", "value"),
    Input("energy-price", "value"),
    Input("annual-distance", "value"),
    State("session-cache", "data"),
)
def update_energy_cost(city_ratio, energy_price, annual_distance, cache):
    if not cache:
        return ""
    vt, year, make, model = cache["vehicle_type"], cache["year"], cache["make"], cache["model"]
    df = CACHED_DATA.get(vt, pd.DataFrame())
    df = df[(df["model_year"].astype(str) == str(year)) & (df["make"] == make) & (df["model"] == model)]
    if df.empty:
        return "Energy data unavailable."

    city_ratio = city_ratio / 100
    highway_ratio = 1 - city_ratio

    if vt == "bev":
        try:
            city_kwh = float(df["city_(kwh/100_km)"].iloc[0])
            highway_kwh = float(df["highway_(kwh/100_km)"].iloc[0])
        except Exception:
            return "Electricity data unavailable."

        annual_cost = (annual_distance / 100) * (
            city_ratio * city_kwh * energy_price + highway_ratio * highway_kwh * energy_price
        )
        return f"Estimated annual charging cost: ${annual_cost:,.0f} CAD (at {energy_price:.2f} CAD/kWh)"

    try:
        city_l = float(df["city_(l/100_km)"].iloc[0])
        highway_l = float(df["highway_(l/100_km)"].iloc[0])
    except Exception:
        return "Fuel data unavailable."

    annual_fuel_cost = (annual_distance / 100) * (
        city_ratio * city_l * energy_price + highway_ratio * highway_l * energy_price
    )
    return f"Estimated annual fuel cost: ${annual_fuel_cost:,.0f} CAD (at {energy_price:.2f} CAD/L)"


# if __name__ == "__main__":
#     app.run(debug=True)

"""
Would you like me to now extend this version with the KPI cards (Performance, Value, Reliability, Eco) next 
— using OpenAI + your dataset logic?
"""

"""
Use display_name where necessary. 
"""