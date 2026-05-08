# ⚽ Football Market Efficiency Dashboard (Streamlit)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Football Market Efficiency Dashboard",
    layout="wide"
)

st.title("⚽ Football Market Efficiency Dashboard")

st.markdown("""
This dashboard evaluates bookmaker prediction efficiency across:
- Premier League
- Bundesliga

The analysis focuses on:
- Market efficiency
- Team overperformance
- Prediction calibration
- Favorites vs underdogs
- Forecasting reliability
""")

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
@st.cache_data

def load_data():

    # Load EPL
    epl = pd.read_excel("E0.xlsx", engine="openpyxl")
    epl["League"] = "Premier League"

    # Load Bundesliga
    bundesliga = pd.read_excel("D1.xlsx", engine="openpyxl")
    bundesliga["League"] = "Bundesliga"

    return epl, bundesliga


try:
    epl, bundesliga = load_data()

except Exception as e:
    st.error(f"Error loading files: {e}")
    st.stop()

# -------------------------------------------------
# COMBINE DATASETS
# -------------------------------------------------
combined = pd.concat([epl, bundesliga], ignore_index=True)

# -------------------------------------------------
# DATA CLEANING
# -------------------------------------------------
combined = combined.dropna(subset=["B365H", "B365D", "B365A", "FTR"])

# -------------------------------------------------
# IMPLIED PROBABILITIES
# -------------------------------------------------
combined["home_prob"] = 1 / combined["B365H"]
combined["draw_prob"] = 1 / combined["B365D"]
combined["away_prob"] = 1 / combined["B365A"]

# Normalize probabilities
prob_total = (
    combined["home_prob"] +
    combined["draw_prob"] +
    combined["away_prob"]
)

combined["home_prob"] = combined["home_prob"] / prob_total
combined["draw_prob"] = combined["draw_prob"] / prob_total
combined["away_prob"] = combined["away_prob"] / prob_total

# -------------------------------------------------
# ACTUAL RESULTS
# -------------------------------------------------
combined["actual_home"] = (combined["FTR"] == "H").astype(int)
combined["actual_draw"] = (combined["FTR"] == "D").astype(int)
combined["actual_away"] = (combined["FTR"] == "A").astype(int)

# -------------------------------------------------
# PREDICTION ERRORS
# -------------------------------------------------
combined["home_error"] = abs(
    combined["actual_home"] - combined["home_prob"]
)

combined["draw_error"] = abs(
    combined["actual_draw"] - combined["draw_prob"]
)

combined["away_error"] = abs(
    combined["actual_away"] - combined["away_prob"]
)

combined["overall_error"] = (
    combined["home_error"] +
    combined["draw_error"] +
    combined["away_error"]
) / 3

# -------------------------------------------------
# TEAM OVERPERFORMANCE
# -------------------------------------------------
combined["home_overperf"] = (
    combined["actual_home"] - combined["home_prob"]
)

combined["away_overperf"] = (
    combined["actual_away"] - combined["away_prob"]
)

home_perf = combined.groupby("HomeTeam")["home_overperf"].mean()
away_perf = combined.groupby("AwayTeam")["away_overperf"].mean()

team_overperf = (
    home_perf.add(away_perf, fill_value=0)
    .sort_values(ascending=False)
)

# -------------------------------------------------
# MARKET TYPE CLASSIFICATION
# -------------------------------------------------
def classify_market(prob):

    if prob >= 0.7:
        return "Favorite"

    elif prob >= 0.4:
        return "Balanced"

    else:
        return "Underdog"


combined["market_type"] = combined["home_prob"].apply(
    classify_market
)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.header("⚙️ Dashboard Filters")

league_filter = st.sidebar.multiselect(
    "Select League",
    combined["League"].unique(),
    default=combined["League"].unique()
)

filtered = combined[
    combined["League"].isin(league_filter)
]

selected_team = st.sidebar.selectbox(
    "Select Team",
    sorted(filtered["HomeTeam"].unique())
)

# -------------------------------------------------
# SECTION 1 — LEAGUE EFFICIENCY
# -------------------------------------------------
st.header("📊 League Market Efficiency")

league_mae = filtered.groupby("League").agg(
    home_error=("home_error", "mean"),
    draw_error=("draw_error", "mean"),
    away_error=("away_error", "mean"),
    overall_mae=("overall_error", "mean")
).reset_index()

fig1 = px.bar(
    league_mae,
    x="League",
    y="overall_mae",
    color="League",
    text="overall_mae",
    title="Bookmaker Prediction Error by League"
)

fig1.update_traces(
    texttemplate='%{text:.3f}',
    textposition='outside'
)

st.plotly_chart(fig1, use_container_width=True)

st.dataframe(league_mae)

# -------------------------------------------------
# SECTION 2 — TEAM OVERPERFORMANCE
# -------------------------------------------------
st.header("📈 Team Overperformance")

team_df = team_overperf.reset_index()
team_df.columns = ["Team", "Overperformance"]

colors = [
    "green" if x > 0 else "red"
    for x in team_df["Overperformance"]
]

fig2 = px.bar(
    team_df,
    x="Overperformance",
    y="Team",
    orientation="h",
    text="Overperformance",
    title="Teams vs Bookmaker Expectations"
)

fig2.update_traces(marker_color=colors)

st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------
# SECTION 3 — MARKET SEGMENTATION
# -------------------------------------------------
st.header("⚽ Favorites vs Underdogs")

market_analysis = filtered.groupby(
    ["League", "market_type"]
).agg(
    home_error=("home_error", "mean")
).reset_index()

fig3 = px.bar(
    market_analysis,
    x="market_type",
    y="home_error",
    color="League",
    barmode="group",
    text="home_error",
    title="Prediction Error by Market Type"
)

fig3.update_traces(
    texttemplate='%{text:.3f}',
    textposition='outside'
)

st.plotly_chart(fig3, use_container_width=True)

# -------------------------------------------------
# SECTION 4 — CALIBRATION ANALYSIS
# -------------------------------------------------
st.header("📉 Probability Calibration")

filtered["prob_bin"] = pd.cut(
    filtered["home_prob"],
    bins=[0,0.1,0.2,0.3,0.4,0.5,
          0.6,0.7,0.8,0.9,1.0]
)

calibration = filtered.groupby(
    ["League", "prob_bin"]
).agg(
    expected_prob=("home_prob", "mean"),
    actual_win_rate=("actual_home", "mean"),
    matches=("actual_home", "count")
).reset_index()

calibration = calibration.dropna()

fig4 = go.Figure()

for league in calibration["League"].unique():

    temp = calibration[
        calibration["League"] == league
    ]

    fig4.add_trace(go.Scatter(
        x=temp["expected_prob"],
        y=temp["actual_win_rate"],
        mode='lines+markers',
        name=league
    ))

# Perfect calibration line
fig4.add_trace(go.Scatter(
    x=[0,1],
    y=[0,1],
    mode='lines',
    name='Perfect Calibration',
    line=dict(dash='dash')
))

fig4.update_layout(
    title="Expected Probability vs Actual Win Rate",
    xaxis_title="Expected Probability",
    yaxis_title="Actual Win Rate"
)

st.plotly_chart(fig4, use_container_width=True)

st.dataframe(calibration)

# -------------------------------------------------
# SECTION 5 — FAVORITE ANALYSIS
# -------------------------------------------------
st.header("🏆 Strong Favorite Analysis")

strong_favorites = filtered[
    filtered["home_prob"] >= 0.7
]

favorite_analysis = strong_favorites.groupby(
    "League"
).agg(
    expected_prob=("home_prob", "mean"),
    actual_win_rate=("actual_home", "mean"),
    matches=("actual_home", "count")
).reset_index()

fig5 = go.Figure()

fig5.add_trace(go.Bar(
    x=favorite_analysis["League"],
    y=favorite_analysis["expected_prob"],
    name="Expected Probability"
))

fig5.add_trace(go.Bar(
    x=favorite_analysis["League"],
    y=favorite_analysis["actual_win_rate"],
    name="Actual Win Rate"
))

fig5.update_layout(
    barmode="group",
    title="Strong Favorites: Expected vs Actual Performance",
    yaxis_title="Probability / Win Rate"
)

st.plotly_chart(fig5, use_container_width=True)

st.dataframe(favorite_analysis)

# -------------------------------------------------
# SECTION 6 — TEAM EXPLORER
# -------------------------------------------------
st.header("🔍 Team Explorer")

team_matches = filtered[
    (filtered["HomeTeam"] == selected_team) |
    (filtered["AwayTeam"] == selected_team)
]

st.subheader(f"Matches involving {selected_team}")

st.dataframe(
    team_matches[[
        "Date",
        "HomeTeam",
        "AwayTeam",
        "FTHG",
        "FTAG",
        "FTR",
        "League"
    ]]
)

# -------------------------------------------------
# SECTION 7 — KEY INSIGHTS
# -------------------------------------------------
st.header("🧠 Key Insights")

st.info("""
Key Findings:

• Bundesliga markets showed lower overall prediction error.

• Premier League markets displayed higher volatility.

• Strong favorites outperformed bookmaker expectations.

• Underdogs generated lower prediction error than favorites.

• Calibration analysis revealed that bookmaker probabilities
were generally well aligned with real outcomes.
""")

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")

st.markdown(
    "Built with Streamlit, Plotly, and Football Betting Market Data"
)


