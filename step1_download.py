import yfinance as yf

# The stocks we want to study
tickers = ["RY.TO", "TD.TO", "AAPL", "MSFT"]

# Download 5 years of daily data and keep only the closing prices
#threads=false means download one stock at a time to avoid locking
prices = yf.download(tickers, period="5y", threads=False)["Close"]

# Look at the first 5 rows and the size of the table
print(prices.head())
print(prices.shape)