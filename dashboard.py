import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

STATE_COLORS = {
    "focused": "#22c55e",
    "distracted": "#f97316",
    "away": "#ef4444"
}

app = dash.Dash(__name__)

app.layout = html.Div(style={"fontFamily": "sans-serif", "padding": "2rem", "maxWidth": "1000px", "margin": "0 auto"}, children=[
    html.H1("Productivity Tracker", style={"marginBottom": "0.25rem"}),
    html.P("Live session data from your webcam tracker.", style={"color": "#6b7280", "marginBottom": "2rem"}),

    dcc.Interval(id="refresh", interval=5000, n_intervals=0),  # refresh every 5s

    html.Div(style={"display": "flex", "gap": "1rem", "marginBottom": "2rem"}, children=[
        html.Div(id="card-focused", style={"flex": 1, "padding": "1.5rem", "borderRadius": "12px", "background": "#f0fdf4", "border": "1px solid #bbf7d0"}),
        html.Div(id="card-distracted", style={"flex": 1, "padding": "1.5rem", "borderRadius": "12px", "background": "#fff7ed", "border": "1px solid #fed7aa"}),
        html.Div(id="card-away", style={"flex": 1, "padding": "1.5rem", "borderRadius": "12px", "background": "#fef2f2", "border": "1px solid #fecaca"}),
    ]),

    html.H2("Overall breakdown", style={"marginBottom": "0.5rem"}),
    dcc.Graph(id="pie-chart", style={"marginBottom": "2rem"}),

    html.H2("Daily breakdown", style={"marginBottom": "0.5rem"}),
    dcc.Graph(id="bar-chart"),
])


def fmt_time(seconds):
    if seconds is None:
        return "0m"
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m}m {s}s" if m else f"{s}s"


@app.callback(
    Output("card-focused", "children"),
    Output("card-distracted", "children"),
    Output("card-away", "children"),
    Output("pie-chart", "figure"),
    Output("bar-chart", "figure"),
    Input("refresh", "n_intervals")
)
def update(n):
    try:
        summary = requests.get(f"{API_URL}/summary").json()
        daily = requests.get(f"{API_URL}/summary/daily").json()
    except Exception:
        empty = go.Figure()
        no_data = html.P("Could not reach API.", style={"color": "red"})
        return no_data, no_data, no_data, empty, empty

    focused = summary.get("focused", 0)
    distracted = summary.get("distracted", 0)
    away = summary.get("away", 0)

    def stat_card(label, seconds, color):
        return [
            html.P(label.capitalize(), style={"margin": 0, "color": color, "fontWeight": 500}),
            html.H2(fmt_time(seconds), style={"margin": "0.25rem 0 0"}),
        ]

    card_focused = stat_card("focused", focused, "#16a34a")
    card_distracted = stat_card("distracted", distracted, "#ea580c")
    card_away = stat_card("away", away, "#dc2626")

    # pie chart
    pie = go.Figure(go.Pie(
        labels=list(summary.keys()),
        values=list(summary.values()),
        marker_colors=[STATE_COLORS.get(k, "#ccc") for k in summary.keys()],
        hole=0.4,
        textinfo="label+percent"
    ))
    pie.update_layout(margin=dict(t=20, b=20), showlegend=False)

    # bar chart
    df = pd.DataFrame(daily)
    if df.empty:
        bar = go.Figure()
    else:
        df["minutes"] = (df["total_seconds"] / 60).round(1)
        bar = px.bar(
            df,
            x="date",
            y="minutes",
            color="state",
            color_discrete_map=STATE_COLORS,
            barmode="stack",
            labels={"minutes": "Minutes", "date": "Date", "state": "State"},
        )
        bar.update_layout(margin=dict(t=20, b=20), legend_title_text="")

    return card_focused, card_distracted, card_away, pie, bar


if __name__ == "__main__":
    app.run(debug=True, port=8050)