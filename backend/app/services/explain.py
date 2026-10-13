"""Explains a fraud prediction with SHAP and turns it into plain English."""
import numpy as np
import shap

from app.services.fraud_model import FEATURES, build_frame, get_model

_explainer = None  # built once, then reused

# Several raw columns describe the same idea, so we add their SHAP values together.
GROUPS = {
    "Amount vs usual": ["amount", "avg_amount_30d", "amount_ratio"],
    "Time of day": ["hour"],
    "Distance from home": ["distance_from_home_km"],
    "Recent activity": ["txn_count_24h"],
    "Device": ["is_new_device"],
    "International": ["is_international"],
    "Account age": ["account_age_days"],
}


def get_explainer():
    global _explainer
    if _explainer is None:
        _explainer = shap.TreeExplainer(get_model())
    return _explainer


def describe(group: str, impact: float, data: dict) -> str:
    """Write one plain-English sentence for a factor."""
    raises_risk = impact > 0

    if group == "Amount vs usual":
        ratio = data["amount"] / data["avg_amount_30d"]
        if raises_risk:
            if ratio >= 1.5:
                return f"Amount is {ratio:.1f}x higher than usual spending"
            return f"Amount of ₹{data['amount']:,.0f} stands out for this account"
        return "Amount is in line with usual spending"

    if group == "Time of day":
        hour = f"{data['hour']:02d}:00"
        if raises_risk:
            return f"Transaction at an unusual hour ({hour})"
        return f"Transaction at a typical hour ({hour})"

    if group == "Distance from home":
        km = data["distance_from_home_km"]
        if raises_risk:
            return f"Transaction is {km:,.0f} km from home"
        return f"Transaction is close to home ({km:,.0f} km)"

    if group == "Recent activity":
        n = data["txn_count_24h"]
        noun = "transaction" if n == 1 else "transactions"
        if raises_risk:
            return f"{n} {noun} in the last 24 hours"
        return f"Only {n} {noun} in the last 24 hours"

    if group == "Device":
        if data["is_new_device"]:
            return "Transaction is from a new device"
        return "Transaction is from a known device"

    if group == "International":
        if data["is_international"]:
            return "International transaction"
        return "Domestic transaction"

    if group == "Account age":
        days = data["account_age_days"]
        if days < 200:
            return f"Account is only {days} days old"
        return f"Account is well established ({days} days old)"

    return group


def explain(data: dict, top_n: int = 5):
    """Return (reasons, contributions) for one transaction."""
    frame = build_frame(data)

    values = np.array(get_explainer().shap_values(frame))
    if values.ndim == 3:        # some versions return one set per class
        values = values[..., 1]
    per_feature = dict(zip(FEATURES, values[0]))

    # Add up the SHAP values inside each group
    contributions = []
    for group, features in GROUPS.items():
        impact = float(sum(per_feature[f] for f in features))
        contributions.append({"feature": group, "impact": round(impact, 3)})

    # Biggest influence first
    contributions.sort(key=lambda c: abs(c["impact"]), reverse=True)

    # Keep the strong ones (up to 5), but always show at least 3
    strong = [c for c in contributions if abs(c["impact"]) >= 0.1][:top_n]
    chosen = strong if len(strong) >= 3 else contributions[:3]

    reasons = [
        {
            "text": describe(c["feature"], c["impact"], data),
            "direction": "increases" if c["impact"] > 0 else "decreases",
        }
        for c in chosen
    ]
    return reasons, contributions