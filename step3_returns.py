import pandas as pd

# Load the cleaned data we saved earlier
prices = pd.read_csv("data/prices.csv", index_col="Date", parse_dates=True)

# 1. Daily returns: the % change from the previous day
returns = prices.pct_change().dropna()

print("First 5 daily returns:")
print((returns.head() * 100).round(2))

# 2. Best and worst day for each stock
print("\nBest day (%):")
print((returns.max() * 100).round(2))
print("\nWorst day (%):")
print((returns.min() * 100).round(2))

# 3. Growth of 100 invested on the first day
growth = prices / prices.iloc[0] * 100

print("\nWhat 100 invested 5 years ago is worth now:")
print(growth.iloc[-1].round(1))