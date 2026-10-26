# score_customers.py - train on all customers, score everyone, write scores to the database.
# Power BI (or Excel) then reads the customer_scores table like any other table.
# Run: python src/score_customers.py

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from features import BASE_DIR, FEATURES, get_engine, load_model_data

engine = get_engine()
model_data, _ = load_model_data(engine)

# Production run: use every customer we have
X = model_data[FEATURES]
scaler = StandardScaler()
model = LogisticRegression(max_iter=1000)
model.fit(scaler.fit_transform(X), model_data["high_value"])

model_data["score"] = model.predict_proba(scaler.transform(X))[:, 1].round(4)
out = model_data[["customer_id", "score"]].sort_values("score", ascending=False)
out.to_sql("customer_scores", engine, if_exists="replace", index=False)

flagged = int((out["score"] > 0.5).sum())
print(f"Wrote {len(out):,} scores; top score {out['score'].max():.4f}; "
      f"{flagged} customers above 0.5")

# How good is the weekly call list (top 100)?
ranked = model_data.sort_values("score", ascending=False)
top100 = ranked.head(100)
print(f"Top 100: {top100['high_value'].mean():.0%} high-value "
      f"(random pick: {model_data['high_value'].mean():.0%}), "
      f"average lifetime spend R{top100['lifetime_spend'].mean():,.2f}")

# The targeting list: top 100 names, joined to customer details
customers = pd.read_sql("SELECT customer_id, first_name, last_name, province, loyalty_tier "
                        "FROM customers", engine)
target = top100[["customer_id", "score"]].merge(customers, on="customer_id")
os.makedirs(os.path.join(BASE_DIR, "results"), exist_ok=True)
target.to_csv(os.path.join(BASE_DIR, "results", "top100_call_list.csv"), index=False)

# Picture of the targeting page: score histogram + top 15 of the call list
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [1, 1.2]})
ax1.hist(out["score"], bins=20, color="#2b6cb0", edgecolor="white")
ax1.axvline(0.5, color="#c53030", linestyle="--", label=f"0.5 flag line ({flagged} flagged)")
ax1.set_title("Scores for all customers")
ax1.set_xlabel("Chance of being high-value")
ax1.set_ylabel("Number of customers")
ax1.legend()

top15 = target.head(15).iloc[::-1]
labels = [f"{r.first_name} {r.last_name} ({r.province}, {r.loyalty_tier})"
          for r in top15.itertuples()]
ax2.barh(labels, top15["score"], color="#2f855a")
ax2.set_xlim(0, 1)
ax2.set_title("This week's call list: top 15 of 100")
ax2.set_xlabel("Score")
fig.suptitle("Targeting page (made-up customers)", fontsize=13)
fig.tight_layout()
fig.savefig(os.path.join(BASE_DIR, "images", "targeting_page.png"), dpi=120)
