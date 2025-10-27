from dash import html, dcc, register_page

register_page(__name__, path="/", name="Home")

layout = html.Div(
    [
        # --- Hero Section ---
        html.Div(
            [
                html.Img(
                    src="https://i.postimg.cc/3JFcThJf/pexels-ammy-k-106103999-9552683.jpg",
                    style={
                        "width": "100%",
                        "maxHeight": "380px",
                        "objectFit": "cover",
                        "borderRadius": "10px",
                        "marginBottom": "25px",
                        "boxShadow": "0 2px 8px rgba(0,0,0,0.15)",
                    },
                ),
                html.H2(
                    "Welcome to the Car Intelligence Hub",
                    style={
                        "textAlign": "center",
                        "marginTop": "10px",
                        "fontWeight": "700",
                        "color": "#2c3e50",
                    },
                ),
                html.P(
                    "Your one-stop automotive insight platform — explore the best cars, get personalized suggestions, and analyze industry trends.",
                    style={
                        "textAlign": "center",
                        "fontSize": "1.1rem",
                        "maxWidth": "750px",
                        "margin": "10px auto 30px auto",
                        "color": "#555",
                    },
                ),
            ]
        ),

        html.Hr(style={"width": "60%", "margin": "30px auto"}),

        # --- Features Section ---
        html.Div(
            [
                # 1️⃣ Car Search
                html.Div(
                    [
                        html.H3("🔍 Car Search"),
                        html.P(
                            "Explore and filter through a comprehensive list of vehicles by make, model, or year. "
                            "Perfect for researching cars and comparing specs side-by-side."
                        ),
                        html.P(
                            "👉 Tip: Use dropdown filters to narrow down to electric, hybrid, or conventional models."
                        ),
                    ],
                    style={"textAlign": "left", "maxWidth": "700px", "margin": "auto", "marginBottom": "30px"},
                ),

                # 2️⃣ Industry Leaders
                html.Div(
                    [
                        html.H3("🏆 Industry Leaders"),
                        html.P(
                            "See the top-ranked cars from 2020 to 2025, categorized by awards such as "
                            "‘Best SUV’, ‘Best Sedan’, or ‘Best Electric Vehicle’."
                        ),
                        html.P(
                            "👉 Tip: Choose a year from the dropdown to see that year's top 5 performers in each category."
                        ),
                    ],
                    style={"textAlign": "left", "maxWidth": "700px", "margin": "auto", "marginBottom": "30px"},
                ),

                # 3️⃣ Find Your Car (LLM assistant)
                html.Div(
                    [
                        html.H3("🤖 Find Your Car (AI Assistant)"),
                        html.P(
                            "Describe what you’re looking for — whether it’s a fast EV, a family SUV, or a budget-friendly compact car. "
                            "Our AI assistant will ask clarifying questions and recommend 5 ideal models."
                        ),
                        html.P(
                            "👉 Tip: Be descriptive! Mention your budget, preferred fuel type, and use case "
                            "(e.g., long-range, city driving, snowy region)."
                        ),
                    ],
                    style={"textAlign": "left", "maxWidth": "700px", "margin": "auto", "marginBottom": "30px"},
                ),
            ]
        ),

        html.Hr(style={"width": "60%", "margin": "30px auto"}),

        # --- Footer ---
        html.Div(
            [
                html.P(
                    "Start exploring the world of intelligent car insights today.",
                    style={"textAlign": "center", "fontWeight": "500", "color": "#444"},
                ),
                html.P(
                    "Use the navigation bar above to get started 🚗",
                    style={"textAlign": "center", "color": "#666", "marginBottom": "20px"},
                ),
            ]
        ),
    ],
    style={
        "padding": "30px",
        "backgroundColor": "#ffffff",
        "fontFamily": "Inter, system-ui, sans-serif",
    },
)
