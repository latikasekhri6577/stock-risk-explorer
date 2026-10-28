import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Stock Risk Explorer", layout="wide")

@st.cache_data
def load_prices():
    return pd.read_csv("data/prices.csv", index_col="Date", parse_dates=True)


prices = load_prices()

# Page title
st.title("Stock Risk and Return Explorer")
st.caption("Analysis of past prices only. No predictions.")

with st.expander("New to stocks? Read this first"):
    st.markdown("""
- **Return:** how much the stock earned per year.
- **Volatility:** how bumpy the ride was (this is the risk).
- **Sharpe ratio:** return per unit of risk. Higher is better. Below 1 is weak, above 2 is excellent.
- **Max drawdown:** the worst fall from a previous peak.
- **Correlation:** do two stocks move together? Near +1 means yes, near 0 means independently.
- **Moving average:** the average price of the last 50 or 200 days. It smooths out the noise to show the trend.
- **Golden / death cross:** the 50-day average crossing above / below the 200-day average.
    """)

# Sidebar controls
st.sidebar.header("Choose what to compare")
chosen = st.sidebar.multiselect(
    "Stocks", list(prices.columns), default=list(prices.columns)
)

min_d = prices.index.min().date()
max_d = prices.index.max().date()
dates = st.sidebar.date_input(
    "Date range", value=(min_d, max_d), min_value=min_d, max_value=max_d
)

# Safety checks, so the app doesn't crash while the user is still choosing
if not chosen:
    st.warning("Pick at least one stock.")
    st.stop()
if len(dates) != 2:
    st.info("Please pick both a start date and an end date.")
    st.stop()

start, end = dates
data = prices.loc[str(start):str(end), chosen]
if data.empty:
    st.warning("No data in this date range.")
    st.stop()

# Growth of 100 invested
growth = data / data.iloc[0] * 100
fig = px.line(growth, title="Growth of 100 invested")
fig.update_layout(yaxis_title="Value", hovermode="x unified", legend_title="Stock")
st.plotly_chart(fig)

# ---------- Key measure cards ----------
returns = data.pct_change().dropna()

if len(returns) < 20:
    st.warning("Pick a longer date range (at least a month) to calculate the measures.")
    st.stop()

years = (data.index[-1] - data.index[0]).days / 365.25
annual_return = (data.iloc[-1] / data.iloc[0]) ** (1 / years) - 1
volatility = returns.std() * (252 ** 0.5)
sharpe = annual_return / volatility
max_drawdown = (data / data.cummax() - 1).min()

st.subheader("Key measures for the chosen period")
cols = st.columns(len(chosen))

for col, stock in zip(cols, chosen):
    with col:
        st.markdown(f"### {stock}")
        st.metric("Annual return", f"{annual_return[stock] * 100:.1f}%")
        st.metric("Volatility", f"{volatility[stock] * 100:.1f}%")
        st.metric("Sharpe ratio", f"{sharpe[stock]:.2f}")
        st.metric("Max drawdown", f"{max_drawdown[stock] * 100:.1f}%")

# ---------- Risk charts ----------
st.subheader("Risk charts")
left, right = st.columns(2)

# Left: risk vs return scatter plot
with left:
    risk_df = pd.DataFrame({
        "Stock": chosen,
        "Volatility %": volatility[chosen].values * 100,
        "Annual return %": annual_return[chosen].values * 100,
    })
    scatter = px.scatter(
        risk_df, x="Volatility %", y="Annual return %",
        text="Stock", color="Stock",
        title="Risk vs return (top-left is best)",
    )
    scatter.update_traces(marker=dict(size=14), textposition="top center")
    scatter.update_layout(showlegend=False)
    st.plotly_chart(scatter)

# Right: drawdown chart
with right:
    drawdown = (data / data.cummax() - 1) * 100
    dd_fig = px.line(drawdown, title="Drawdown: how far below the previous peak")
    dd_fig.update_layout(
        yaxis_title="% below peak", hovermode="x unified", legend_title="Stock"
    )
    st.plotly_chart(dd_fig)


# ---------- Correlation heatmap ----------
st.subheader("Do these stocks move together?")

if len(chosen) < 2:
    st.info("Pick at least two stocks to see how they move together.")
else:
    corr = returns.corr()
    heat = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        title="Correlation of daily returns",
    )
    st.plotly_chart(heat)
    st.caption("Closer to +1: move together. Closer to 0: move independently. "
               "Lower numbers between stocks mean better diversification.")


# ---------- Portfolio builder ----------
st.subheader("Build your own portfolio")
st.write("Set how much goes into each stock. The app rescales your numbers so they add up to 100%.")

raw = {}
slider_cols = st.columns(len(chosen))
for col, stock in zip(slider_cols, chosen):
    with col:
        raw[stock] = st.slider(stock, 0, 100, 100 // len(chosen), key=f"w_{stock}")

total = sum(raw.values())
if total == 0:
    st.warning("Give at least one stock a weight above 0.")
    st.stop()

weights = pd.Series(raw) / total
st.write("Your mix: " + ", ".join(f"{s} {w * 100:.0f}%" for s, w in weights.items()))

# Portfolio's daily return = weighted sum of the stocks' daily returns
port_ret = (returns[chosen] * weights).sum(axis=1)
port_growth = (1 + port_ret).cumprod()

p_return = port_growth.iloc[-1] ** (1 / years) - 1
p_vol = port_ret.std() * (252 ** 0.5)
p_sharpe = p_return / p_vol
p_dd = (port_growth / port_growth.cummax() - 1).min()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Annual return", f"{p_return * 100:.1f}%")
c2.metric("Volatility", f"{p_vol * 100:.1f}%")
c3.metric("Sharpe ratio", f"{p_sharpe:.2f}")
c4.metric("Max drawdown", f"{p_dd * 100:.1f}%")

# Chart: your portfolio vs the individual stocks
compare = growth.copy()
compare["Your portfolio"] = port_growth * 100
port_fig = px.line(compare, title="Your portfolio vs the individual stocks (100 invested)")
port_fig.data[-1].update(line=dict(width=4))
port_fig.update_layout(yaxis_title="Value", hovermode="x unified", legend_title="")
st.plotly_chart(port_fig)
st.caption("Simplified: the mix is reset to your percentages every day. "
           "Currency differences, trading costs and taxes are ignored.")


# ---------- Insights and download ----------
import numpy as np

st.subheader("Plain-language insights")

best_return = annual_return[chosen].idxmax()
lowest_risk = volatility[chosen].idxmin()
best_sharpe = sharpe[chosen].idxmax()
worst_fall = max_drawdown[chosen].idxmin()

st.markdown(f"- **Highest return:** {best_return} ({annual_return[best_return] * 100:.1f}% per year)")
st.markdown(f"- **Lowest risk:** {lowest_risk} (volatility {volatility[lowest_risk] * 100:.1f}%)")
st.markdown(f"- **Best return for the risk:** {best_sharpe} (Sharpe {sharpe[best_sharpe]:.2f})")
st.markdown(f"- **Deepest fall:** {worst_fall} ({max_drawdown[worst_fall] * 100:.1f}% below its peak)")

if len(chosen) >= 2:
    pair_corr = returns[chosen].corr()
    upper = pair_corr.where(np.triu(np.ones(pair_corr.shape, dtype=bool), k=1))
    pairs = upper.stack()
    a, b = pairs.idxmin()
    st.markdown(f"- **Best diversifying pair:** {a} and {b} (correlation {pairs.min():.2f})")

st.caption("These insights describe the chosen period only. Past performance does not guarantee future results.")

# Download the measures as a CSV file
summary_df = pd.DataFrame({
    "Annual return %": annual_return[chosen] * 100,
    "Volatility %": volatility[chosen] * 100,
    "Sharpe": sharpe[chosen],
    "Max drawdown %": max_drawdown[chosen] * 100,
}).round(2)

st.download_button(
    "Download these results (CSV)",
    data=summary_df.to_csv().encode("utf-8"),
    file_name="stock_summary.csv",
    mime="text/csv",
)

# ---------- Trend chart with moving averages ----------
import plotly.graph_objects as go

st.subheader("Trend chart with moving averages")
trend_stock = st.selectbox("Choose a stock", chosen)

# Calculate on the FULL history, so the 200-day line is ready when the chosen range starts
full_price = prices[trend_stock]
ma50 = full_price.rolling(50).mean()
ma200 = full_price.rolling(200).mean()

# Find the crossovers
above = (ma50 > ma200).astype(int)
change = above.diff()
has_history = ma200.shift(1).notna()
golden = full_price[(change == 1) & has_history]
death = full_price[(change == -1) & has_history]

# Show only the dates chosen in the sidebar
def in_range(series):
    return series.loc[str(start):str(end)]

trend_fig = go.Figure()
trend_fig.add_trace(go.Scatter(x=in_range(full_price).index, y=in_range(full_price), name="Price"))
trend_fig.add_trace(go.Scatter(x=in_range(ma50).index, y=in_range(ma50), name="50-day average"))
trend_fig.add_trace(go.Scatter(x=in_range(ma200).index, y=in_range(ma200), name="200-day average"))
trend_fig.add_trace(go.Scatter(x=in_range(golden).index, y=in_range(golden), mode="markers",
                               name="Golden cross",
                               marker=dict(size=12, symbol="triangle-up", color="green")))
trend_fig.add_trace(go.Scatter(x=in_range(death).index, y=in_range(death), mode="markers",
                               name="Death cross",
                               marker=dict(size=12, symbol="triangle-down", color="red")))
trend_fig.update_layout(title=f"{trend_stock}: price and moving averages", hovermode="x unified")
st.plotly_chart(trend_fig)
st.caption("Describes past trends only. A cross is not a prediction.")