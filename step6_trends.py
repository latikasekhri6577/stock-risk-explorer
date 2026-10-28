import pandas as pd
import plotly.graph_objects as go

prices = pd.read_csv("data/prices.csv", index_col="Date", parse_dates=True)

ticker = "RY.TO"          # change this to any of the 4 stocks later
price = prices[ticker]

# Moving averages
ma50 = price.rolling(50).mean()
ma200 = price.rolling(200).mean()

# Find crossovers: 1 means 50-day is above 200-day, 0 means below
above = (ma50 > ma200).astype(int)
change = above.diff()                       # +1 = just crossed up, -1 = just crossed down
has_history = ma200.shift(1).notna()        # ignore the first days before the 200-day exists
golden = price[(change == 1) & has_history]
death = price[(change == -1) & has_history]

# Draw the chart
fig = go.Figure()
fig.add_trace(go.Scatter(x=price.index, y=price, name="Price"))
fig.add_trace(go.Scatter(x=ma50.index, y=ma50, name="50-day average"))
fig.add_trace(go.Scatter(x=ma200.index, y=ma200, name="200-day average"))
fig.add_trace(go.Scatter(x=golden.index, y=golden, mode="markers",
                         name="Golden cross", marker=dict(size=12, symbol="triangle-up", color="green")))
fig.add_trace(go.Scatter(x=death.index, y=death, mode="markers",
                         name="Death cross", marker=dict(size=12, symbol="triangle-down", color="red")))
fig.update_layout(title=f"{ticker}: price and moving averages")
fig.show()