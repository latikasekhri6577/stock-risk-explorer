import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

prices = pd.read_csv("data/prices.csv", index_col="Date", parse_dates=True)
returns = prices.pct_change().dropna()

# Correlation between every pair of stocks
corr = returns.corr()
print(corr.round(2))

# Draw the heatmap
sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1, fmt=".2f")
plt.title("How closely do these stocks move together?")

# Save the picture, then show it
plt.savefig("data/correlation.png", dpi=150, bbox_inches="tight")
plt.show()