import yfinance as yf
import pandas as pd
import os


# The stocks we want to study
tickers = ["RY.TO", "TD.TO", "AAPL", "MSFT"]

# Download 5 years of daily data and keep only the closing prices
#threads=false means download one stock at a time to avoid locking
prices = yf.download(tickers, period="5y", threads=False)["Close"]

# 1. Check the missing values 
print("Missing values before cleaning:")
print(prices.isna().sum())

# 2. Fix: fill a gap with the previous day's price, then drop any leftovers
prices=prices.ffill().dropna()

# 3. Check again
print("Missing values after cleaning:")
print(prices.isna().sum())
print("Final shape:", prices.shape)

# 4. Save to a file so we can reuse it without downloading again
os.makedirs("data", exist_ok=True)
prices.to_csv("data/prices.csv")
print("\nSaved to data/prices.csv")