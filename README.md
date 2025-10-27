CAR-INTELLIGENCE-HUB/      ← main project folder
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore             
├── .env                   ← (NOT pushed)
│
├── data/
│   ├── bev.csv
│   ├── car_rankings.csv
│   ├── conventional.csv
│   ├── phev.csv
│   └── last_updated.txt
│
└── pages/
    ├── home.py
    ├── car_search.py
    ├── myCar.py
    └── rankings.py


# 🚗 Car Intelligence Hub

An interactive Dash app that uses AI to analyze, rank, and recommend cars between 2020–2025.  
Built with Dash, OpenAI API, and pandas — offering real-time rankings, category insights, and personalized car suggestions.

## 🌟 Features
- AI-powered car recommendations
- Year & category-based top 5 rankings
- Interactive design with Dash Bootstrap Components
- Integrated OpenAI LLM analysis

## 🧰 Tech Stack
- Python 3.11+
- Dash
- Plotly
- OpenAI API
- Bootstrap (Flatly theme)

## 🚀 Run Locally
```bash
pip install -r requirements.txt
python app.py
