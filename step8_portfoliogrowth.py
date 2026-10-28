import pandas as pd
import plotly.graph_objects as go

prices = pd.read_csv("data/prices.csv", index_col="Date", parse_dates=True)
returns = prices.pct_change().dropna()

portfolios = {
    "All Banks": {"RY.TO": 0.5, "TD.TO": 0.5},
    "All Tech": {"AAPL": 0.5, "MSFT": 0.5},
    "Mixed": {"RY.TO": 0.25, "TD.TO": 0.25, "AAPL": 0.25, "MSFT": 0.25},
}

fig = go.Figure()
for name, weights in portfolios.items():
    w = pd.Series(weights)
    port_ret = (returns[w.index] * w).sum(axis=1)
    growth = (1 + port_ret).cumprod() * 100       # start at 100
    fig.add_trace(go.Scatter(x=growth.index, y=growth, name=name))

fig.update_layout(
    title="Growth of 100 invested in each portfolio",
    yaxis_title="Value of investment",
    hovermode="x unified",
)
fig.show()