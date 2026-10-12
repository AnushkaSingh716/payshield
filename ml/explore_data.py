"""A quick look at the fraud data: size, missing values, class imbalance."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # save the chart as a file instead of opening a window
import matplotlib.pyplot as plt
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
df = pd.read_csv(DATA_DIR / "fraud_transactions.csv")

print("Rows, columns:", df.shape)
print("Missing values:", df.isna().sum().sum())
print()

# How imbalanced is it?
counts = df["is_fraud"].value_counts()
n_legit, n_fraud = counts[0], counts[1]
print(f"Legit: {n_legit:,}  Fraud: {n_fraud:,}  ({n_fraud / len(df):.2%} fraud)")
print()

# Do fraud rows really look different? Compare the averages.
print("Average of each feature (0 = legit, 1 = fraud):")
print(df.groupby("is_fraud").mean().round(2).T)
print()

# Handling imbalance: instead of copying fake fraud rows (SMOTE), we tell the
# model that one fraud row matters as much as ~49 legit rows (class weights).
print(f"scale_pos_weight for XGBoost = {n_legit / n_fraud:.1f}")

# Save a simple chart
counts.rename({0: "Legit", 1: "Fraud"}).plot(kind="bar", color=["green", "red"])
plt.title("Legit vs Fraud transactions")
plt.ylabel("Count")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(DATA_DIR / "class_balance.png")
print("Chart saved to", DATA_DIR / "class_balance.png")