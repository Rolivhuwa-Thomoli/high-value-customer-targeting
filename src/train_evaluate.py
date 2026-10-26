# train_evaluate.py - train the model on 75% of customers and test it on the other 25%.
# The test customers are never seen during training, so the result is honest.
# Run: python src/train_evaluate.py

import os

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from features import BASE_DIR, FEATURES, get_engine, load_model_data

model_data, threshold = load_model_data(get_engine())
X = model_data[FEATURES]
y = model_data["high_value"]
print(f"Customers: {len(model_data):,} | top-25% spend line: R{threshold:,.2f}")

# Keep 25% of customers aside as a test set
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25,
                                          random_state=42, stratify=y)

# Put the features on the same scale so the coefficients can be compared
scaler = StandardScaler()
model = LogisticRegression(max_iter=1000)
model.fit(scaler.fit_transform(X_tr), y_tr)

proba = model.predict_proba(scaler.transform(X_te))[:, 1]
auc = roc_auc_score(y_te, proba)
cm = confusion_matrix(y_te, (proba > 0.5).astype(int))

# Business view: if we call the top 25 test customers, how many are high-value?
test = pd.DataFrame({"high_value": y_te.to_numpy(), "score": proba})
top_n = 25  # 100 out of 1,800 is about 5.5%; 25 out of 450 is the same share
top_rate = test.sort_values("score", ascending=False).head(top_n)["high_value"].mean()
base_rate = test["high_value"].mean()

lines = [
    f"AUC on test customers: {auc:.3f}",
    "Coefficients (scaled features):",
    *[f"  {name}: {coef:+.2f}" for name, coef in zip(FEATURES, model.coef_[0])],
    "Confusion matrix at 0.5 (rows = actual 0/1, columns = predicted 0/1):",
    f"  {cm.tolist()}",
    f"Top {top_n} test customers by score: {top_rate:.0%} are high-value",
    f"Random pick: {base_rate:.0%} are high-value",
    f"Lift: {top_rate / base_rate:.1f}x",
]
print("\n".join(lines))

os.makedirs(os.path.join(BASE_DIR, "results"), exist_ok=True)
with open(os.path.join(BASE_DIR, "results", "evaluation.txt"), "w") as f:
    f.write("\n".join(lines) + "\n")
