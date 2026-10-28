import pandas as pd

prices = pd.read_csv("data/prices.csv", index_col="Date", parse_dates=True)
returns = prices.pct_change().dropna()

# 1. Yearly return (CAGR): the steady yearly growth rate that matches the total growth
years = (prices.index[-1] - prices.index[0]).days / 365.25
annual_return = (prices.iloc[-1] / prices.iloc[0]) ** (1 / years) - 1

# 2. Volatility: how bumpy, scaled up to a full year
volatility = returns.std() * (252 ** 0.5)

# 3. Sharpe ratio: return per unit of risk (simple version, no risk-free rate)
sharpe = annual_return / volatility

# 4. Maximum drawdown: the worst fall from a previous peak
running_peak = prices.cummax()
drawdown = prices / running_peak - 1
max_drawdown = drawdown.min()

# Put everything in one summary table
summary = pd.DataFrame({
    "Annual Return %": annual_return * 100,
    "Volatility %": volatility * 100,
    "Sharpe": sharpe,
    "Max Drawdown %": max_drawdown * 100,
}).round(2)

print(summary)
summary.to_csv("data/summary.csv")