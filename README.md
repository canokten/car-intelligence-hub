# 🚗 Car Intelligence Hub

Car Intelligence Hub is an interactive analytics platform built with Dash that helps users explore, compare, and discover vehicles using verified government data and AI insights.

It combines real-world efficiency datasets from Natural Resources Canada with OpenAI’s GPT models to generate meaningful vehicle summaries, cost estimates, and smart rankings.

## Features

🔍 Car Search – View detailed specs, performance data, and annual fuel or electricity cost estimates for any car.

🏆 Rankings – Explore the top 5 vehicles of each year and category, scored across four metrics: Performance, Value, Reliability, and Eco-efficiency.

🤖 AI Car Finder – Describe what you’re looking for (e.g., “family SUV with great mileage”) and get AI-powered recommendations tailored to your needs.

## Methodology

All vehicle data is sourced from Natural Resources Canada’s Fuel Consumption Ratings dataset under the Open Government Licence – Canada.

This dataset provides model-specific fuel consumption ratings and estimated CO₂ emissions for new light-duty vehicles sold in Canada between 1995–2025.

It includes:
- Conventional vehicles (2015–2025)
- Plug-in Hybrid Electric Vehicles (2012–2025)
- Battery Electric Vehicles (2012–2025)

## Metric Calculation

Each car is scored across four key dimensions:

- Performance   - Derived from powertrain type, fuel economy, and drivetrain characteristics.
- Value         - Considers energy cost per year and comparative efficiency within its class.
- Reliability	- Estimated based on brand reliability averages and historical trend data.
- Eco	        - Based on CO₂ emissions per km and powertrain classification (EV, hybrid, gas).

Fuel and electricity costs are computed from dataset consumption values using current Canadian averages:

- Gasoline: 1.80 CAD/L
- Electricity: 0.18 CAD/kWh
- Annual driving distance: 15,000 km/year (default assumption)

All three of these metrics can be adjusted in the UI depending on region or personal preferences, and the calculation will adjust accordingly. 

## AI Integration

The app uses OpenAI’s GPT models:
- gpt-4o-mini – for fast, efficient summaries and explanations
- gpt-4o – for detailed comparisons and contextual reasoning

## Tech Stack
- Python 3.11.3
- Dash
- pandas
- OpenAI API (gpt-4o-mini, gpt-4o)
- Bootstrap (Flatly theme)
- Render (Web Service Deployement)

## Run Locally
```bash
pip install -r requirements.txt
python app.py
