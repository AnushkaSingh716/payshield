"""Creates a fake (synthetic) transaction dataset for PayShield.

Fraud rows are made to look different from normal rows: bigger amounts,
night-time, far from home, new device, and so on. Some fraud rows look
normal on purpose, so the model has to work for its score.
"""
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)  # fixed seed = same data every run

N_ROWS = 50_000
FRAUD_RATE = 0.02  # 2% fraud, like the real world (very imbalanced)

n_fraud = int(N_ROWS * FRAUD_RATE)
n_legit = N_ROWS - n_fraud


def make_rows(n, is_fraud):
    """Make n transactions, either legit or fraud."""
    # The customer's usual spending (average over the last 30 days, in rupees)
    avg_amount = rng.lognormal(mean=np.log(1500), sigma=0.6, size=n)

    if not is_fraud:
        amount = avg_amount * rng.lognormal(0, 0.5, n)
        hour = np.round(rng.normal(15, 4, n)).astype(int) % 24  # mostly daytime
        distance = rng.exponential(8, n)                        # close to home
        txn_count = rng.poisson(2, n)                           # few txns today
        new_device = rng.random(n) < 0.05
        international = rng.random(n) < 0.03
        account_age = rng.integers(30, 3000, n)
    else:
        # 80% of frauds have a much bigger amount than usual, 20% look normal
        big = rng.random(n) < 0.8
        factor = np.where(big, rng.lognormal(np.log(5), 0.7, n),
                          rng.lognormal(0, 0.5, n))
        amount = avg_amount * factor
        night = rng.random(n) < 0.5                             # half at night
        hour = np.where(night, rng.integers(0, 6, n), rng.integers(0, 24, n))
        far = rng.random(n) < 0.7                               # mostly far away
        distance = np.where(far, rng.exponential(150, n),
                            rng.exponential(8, n))
        txn_count = rng.poisson(6, n)                           # many txns today
        new_device = rng.random(n) < 0.6
        international = rng.random(n) < 0.35
        new_account = rng.random(n) < 0.4
        account_age = np.where(new_account, rng.integers(1, 200, n),
                               rng.integers(30, 3000, n))

    return pd.DataFrame({
        "amount": amount.round(2),
        "avg_amount_30d": avg_amount.round(2),
        "amount_ratio": (amount / avg_amount).round(2),  # how unusual the amount is
        "hour": hour,
        "distance_from_home_km": distance.round(1),
        "txn_count_24h": txn_count,
        "is_new_device": new_device.astype(int),
        "is_international": international.astype(int),
        "account_age_days": account_age,
        "is_fraud": int(is_fraud),
    })


df = pd.concat([make_rows(n_legit, False), make_rows(n_fraud, True)])
df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle rows

out_path = Path(__file__).parent / "data" / "fraud_transactions.csv"
df.to_csv(out_path, index=False)

print(f"Saved {len(df):,} rows to {out_path}")
print(f"Fraud rows: {df['is_fraud'].sum():,}")