# ⚽ Football Market Efficiency Dashboard

A sports analytics dashboard built with Python and Streamlit that evaluates bookmaker prediction efficiency across:

- Premier League
- Bundesliga

The project explores:

- Market efficiency
- Team overperformance
- Probability calibration
- Favorites vs underdogs
- Forecasting reliability

---

# 📊 Project Objective

This project investigates whether bookmaker probabilities accurately reflect real football outcomes.

Using betting market odds from Bet365, the dashboard analyzes:

- Which leagues are harder to predict
- Which teams outperform bookmaker expectations
- Whether favorites are overpriced or underpriced
- How well bookmaker probabilities are calibrated

---

# 🧠 Key Business Questions

- Are bookmaker markets efficient?
- Which teams consistently outperform expectations?
- Are strong favorites accurately priced?
- Which league is more predictable?
- Do bookmakers systematically misprice certain market segments?

---

# 📈 Key Insights

### ✅ Bundesliga markets showed lower prediction error
The Bundesliga demonstrated slightly lower mean absolute error (MAE), suggesting higher market predictability compared to the Premier League.

### ✅ Premier League markets displayed higher volatility
The EPL exhibited greater forecasting uncertainty and more unpredictable outcomes.

### ✅ Strong favorites outperformed expectations
Across both leagues, teams with very high implied probabilities won more often than bookmakers predicted.

### ✅ Underdogs produced lower prediction error
Bookmakers were highly effective at identifying weak teams and low-probability outcomes.

### ✅ Calibration analysis revealed generally efficient pricing
Bookmaker probabilities aligned reasonably well with actual match outcomes across most probability ranges.

---

# ⚙️ Features

- Interactive Streamlit dashboard
- League comparison analysis
- Team overperformance rankings
- Favorites vs underdogs analysis
- Probability calibration curves
- Strong favorite analysis
- Team match explorer
- Market efficiency visualizations

---

# 📂 Dataset

The datasets contain:

- Match results
- Goals scored
- Betting odds
- Match statistics
- Referee data
- Over/Under odds
- Asian handicap markets

Leagues analyzed:

- Premier League (`E0.xlsx`)
- Bundesliga (`D1.xlsx`)

---

# 🛠️ Technologies Used

- Python
- Pandas
- Plotly
- Streamlit
- NumPy
- OpenPyXL

---

# 🚀 Installation

Clone the repository:

```bash
git clone <your-github-repo-link>
