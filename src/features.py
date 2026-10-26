# features.py - build the label and the features for each customer.
# Used by both train_evaluate.py and score_customers.py, so they always match.

import os

import pandas as pd
from sqlalchemy import create_engine

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SQLite by default. To use SQL Server instead, set DATABASE_URL, for example:
# mssql+pyodbc://localhost\SQLEXPRESS/MzansiRetail?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes
DEFAULT_URL = "sqlite:///" + os.path.join(BASE_DIR, "data", "mzansi_retail.db")
FEATURES = ["early_orders", "early_spend", "early_categories"]


def get_engine():
    return create_engine(os.environ.get("DATABASE_URL", DEFAULT_URL))


def load_model_data(engine):
    # One row per completed order line, with its date and customer
    lines = pd.read_sql("""
        SELECT o.customer_id, o.order_date,
               i.quantity * i.unit_price * (1 - i.discount_pct / 100.0) AS line_total,
               i.product_id
        FROM orders o
        JOIN order_items i ON o.order_id = i.order_id
        WHERE o.status = 'Completed'
    """, engine, parse_dates=["order_date"])

    # LABEL: is the customer's total spend in the top 25%?
    lifetime = lines.groupby("customer_id")["line_total"].sum()
    threshold = lifetime.quantile(0.75)
    high_value = (lifetime >= threshold).astype(int)

    # FEATURES: what the customer did in their first 180 days
    first_order = lines.groupby("customer_id")["order_date"].min().rename("first_dt")
    beh = lines.merge(first_order, on="customer_id")
    early = beh[beh["order_date"] <= beh["first_dt"] + pd.Timedelta(days=180)]
    features = early.groupby("customer_id").agg(
        early_orders=("line_total", "size"),        # number of items bought
        early_spend=("line_total", "sum"),          # money spent
        early_categories=("product_id", "nunique"),  # how many different products
    ).reset_index()

    model_data = features.merge(high_value.rename("high_value"),
                                left_on="customer_id", right_index=True)
    model_data = model_data.merge(lifetime.rename("lifetime_spend"),
                                  left_on="customer_id", right_index=True)
    return model_data, threshold
