import pandas as pd

prices = pd.read_csv("data/prices.csv", index_col="Date", parse_dates=True)
returns = prices.pct_change().dropna()

# How much of each stock goes into each portfolio (weights add up to 1)
portfolios = {
    "All Banks": {"RY.TO": 0.5, "TD.TO": 0.5},
    "All Tech": {"AAPL": 0.5, "MSFT": 0.5},
    "Mixed": {"RY.TO": 0.25, "TD.TO": 0.25, "AAPL": 0.25, "MSFT": 0.25},
}

results = {}
for name, weights in portfolios.items():
    w = pd.Series(weights)

    # Portfolio's daily return = weighted sum of its stocks' daily returns
    port_ret = (returns[w.index] * w).sum(axis=1)

    # Growth of 1 invested, and the same measures as Step 13
    growth = (1 + port_ret).cumprod()
    years = (growth.index[-1] - growth.index[0]).days / 365.25
    annual_return = growth.iloc[-1] ** (1 / years) - 1
    volatility = port_ret.std() * (252 ** 0.5)
    sharpe = annual_return / volatility
    max_drawdown = (growth / growth.cummax() - 1).min()

    results[name] = {
        "Annual Return %": annual_return * 100,
        "Volatility %": volatility * 100,
        "Sharpe": sharpe,
        "Max Drawdown %": max_drawdown * 100,
    }

summary = pd.DataFrame(results).T.round(2)
print(summary)
summary.to_csv("data/portfolios.csv")