# from dash import html, register_page

# register_page(__name__, path="/myCar", name="myCar")

# layout = html.Div([
#     html.H2("Find Your Car"),
#     html.P("Explain to me what are you looking for in your next car and pick from the options!")
# ])

# myCar.py
import os
import json
import re
from typing import List, Dict, Any, Optional

from dash import no_update
from dash import html, dcc, Input, Output, State, callback, register_page
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
register_page(__name__, path="/myCar", name="Find My Car")

# --------------------------
# Enhanced System Prompt
# --------------------------
SYSTEM_PROMPT = """
You are CarAdvisor — a specialized automotive consultant who helps users choose, compare, and inspect cars for purchase in a natural multi-turn chat.

You must:
1. Extract and remember user preferences (seats, performance, use case, price, fuel type, brand, drive type, transmission, range, maintenance, cargo space, climate).
2. If any information is missing, ask the most relevant 1–2 clarifying questions.
3. When ready, provide EXACTLY 5 recommendations in this JSON format:

{
  "recommendations": [
    {
      "rank": 1,
      "model": "Toyota RAV4 Hybrid",
      "manufacturer": "Toyota",
      "year": 2025,
      "category": "SUV",
      "fuel_type": "Hybrid Gasoline",
      "price_range": "Used: $25,000–$35,000 | New: $38,000–$45,000",
      "seats": 5,
      "transmission": "Automatic",
      "engine": "2.5L I4 Hybrid",
      "max_speed": "180 km/h",
      "fuel_consumption": "5.8 L/100 km",
      "region_availability": ["North America", "Europe", "Asia"],
      "rationale": "Reliable, efficient family SUV ideal for city and long-range travel."
    },
    ...
  ]
}

Guidelines:
- Always include `price_range`, `seats`, `transmission`, `engine`, `max_speed`, and `fuel_consumption` (or electric consumption if EV).
- Be realistic and concise. You may estimate reasonable ranges if unknown.
- If comparing multiple cars, use short comparison summaries.
- If unclear about user intent, ask follow-up questions before listing.

Tone: friendly, expert, and professional.
"""

# --------------------------
# Helper Functions
# --------------------------
def call_llm(messages: List[Dict[str, str]]) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.7,
        messages=messages
    )
    return resp.choices[0].message.content.strip()

def extract_json_recommendations(text: str) -> Optional[List[Dict[str, Any]]]:
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
        return data.get("recommendations", [])
    except Exception:
        return None

def render_chat(history: List[Dict[str, str]]) -> List[Any]:
    bubbles = []
    for msg in history:
        if msg["role"] == "system":
            continue
        align = "right" if msg["role"] == "user" else "left"
        color = "#e8f0fe" if msg["role"] == "user" else "#ffffff"
        bubbles.append(
            html.Div(
                msg["content"],
                style={
                    "textAlign": align,
                    "backgroundColor": color,
                    "padding": "10px 14px",
                    "borderRadius": "12px",
                    "margin": "8px 0",
                    "border": "1px solid #ddd",
                    "maxWidth": "75%",
                    "alignSelf": "flex-end" if align == "right" else "flex-start",
                    "whiteSpace": "pre-wrap",
                },
            )
        )
    return bubbles

def render_recommendation_cards(recs: List[Dict[str, Any]]) -> List[Any]:
    cards = []
    for r in recs[:5]:
        region_str = ", ".join(r.get("region_availability", [])) if isinstance(r.get("region_availability"), list) else r.get("region_availability", "N/A")

        cards.append(
            html.Div(
                [
                    html.Div(f"#{r.get('rank','-')}", style={"fontWeight": 600, "opacity": 0.6}),
                    html.H4(f"{r.get('year', '')} {r.get('model', 'Unknown')} ({r.get('manufacturer','')})",
                            style={"margin": "6px 0"}),

                    html.Div(
                        f"Category: {r.get('category','N/A')} • Price Range: {r.get('price_range','N/A')}",
                        style={"color": "#555"}
                    ),

                    html.Div(
                        f"Fuel Type: {r.get('fuel_type','-')} • Seats: {r.get('seats','-')} • Transmission: {r.get('transmission','-')} • "
                        f"Engine: {r.get('engine','-')} • Max Speed: {r.get('max_speed','-')} • Consumption: {r.get('fuel_consumption','-')}",
                        style={"color": "#666", "fontSize": "0.9em", "marginTop": "4px"}
                    ),

                    html.Div(
                        f"Available Regions: {region_str}",
                        style={"color": "#777", "fontSize": "0.85em", "marginTop": "2px", "marginBottom": "6px"}
                    ),

                    html.Div(r.get("rationale", ""), style={"color": "#666"})
                ],
                style={
                    "border": "1px solid #e5e5e5",
                    "borderRadius": "12px",
                    "padding": "14px",
                    "backgroundColor": "#fff",
                    "boxShadow": "0 1px 3px rgba(0,0,0,0.06)",
                    "marginBottom": "14px",
                }
            )
        )
    return cards


# --------------------------
# Layout
# --------------------------
INITIAL_ASSISTANT = (
    "Hi there! Tell me what kind of car you’re looking for — "
    "for example, a fast sedan, family SUV, or eco-friendly commuter. "
    "I’ll ask follow-ups if needed and then show you my top 5 picks."
)

layout = html.Div(
    [
        html.H2("Find Your Perfect Car", style={"textAlign": "center"}),
        html.P(
            "Describe what you want in plain English (budget, seats, fuel type, performance, etc).",
            style={"textAlign": "center", "maxWidth": "800px", "margin": "auto", "color": "#555"},
        ),

        # Chat Area
        html.Div(
            id="chat-container",
            children=[
                html.Div(
                    id="chat-history",
                    style={
                        "maxWidth": "800px",
                        "width": "100%",
                        "margin": "20px auto",
                        "padding": "16px",
                        "border": "1px solid #ddd",
                        "borderRadius": "12px",
                        "backgroundColor": "#fafafa",
                        "minHeight": "250px",
                        "display": "flex",
                        "flexDirection": "column",
                        "justifyContent": "flex-start",
                    },
                ),
                # Input directly under chat
                html.Div(
                    [
                        dcc.Textarea(
                            id="user-input",
                            placeholder="e.g., I want a 5-seater automatic SUV good for long trips under $40k.",
                            style={"width": "80%", "height": "90px", "marginRight": "10px", "borderRadius": "10px"},
                        ),
                        html.Button("Send", id="send-btn", n_clicks=0, style={"height": "44px"}),
                    ],
                    style={"display": "flex", "justifyContent": "center", "alignItems": "center", "marginTop": "12px"},
                ),
            ],
        ),

        html.H4("Recommendations", style={"textAlign": "center", "marginTop": "40px"}),
        html.Div(id="recs-container", style={"maxWidth": "800px", "margin": "0 auto"}),

        dcc.Store(
            id="conv-store",
            data=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "assistant", "content": INITIAL_ASSISTANT},
            ],
        ),
    ],
    style={
        "display": "flex",
        "flexDirection": "column",
        "alignItems": "center",
        "padding": "36px",
    },
)

# --------------------------
# Callbacks
# --------------------------
@callback(
    Output("chat-history", "children"),
    Output("recs-container", "children"),
    Output("conv-store", "data"),
    Output("user-input", "value"),
    Input("send-btn", "n_clicks"),
    State("user-input", "value"),
    State("conv-store", "data"),
    prevent_initial_call=True,
)
def chat_logic(n_clicks, user_msg, conv):
    if not user_msg:
        return html.Div(render_chat(conv)), no_update, conv, ""

    conv.append({"role": "user", "content": user_msg})
    llm_text = call_llm(conv)
    recs = extract_json_recommendations(llm_text)

    if recs:
        conv.append({"role": "assistant", "content": "Here are my top 5 suggestions for you!"})
        chat_content = render_chat(conv)
        rec_cards = render_recommendation_cards(recs)
        return chat_content, rec_cards, conv, ""
    else:
        conv.append({"role": "assistant", "content": llm_text})
        return render_chat(conv), no_update, conv, ""

