# generate_data.py
# ============================================================
# Mzansi Retail (Pty) Ltd - training database generator
# Run once: python src/generate_data.py
# Creates the CSV files in data/ and loads them into data/mzansi_retail.db
# The data is made up (synthetic). No real people or shops.
# ============================================================

import os
import sqlite3
from datetime import date, timedelta

import numpy as np
import pandas as pd

# Fixed seed so the same data comes out every time
rng = np.random.default_rng(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ------------------------------------------------------------
# TABLE 1: stores - 12 shops across South Africa
# ------------------------------------------------------------
stores = [
    (1, "Sandton City", "Gauteng", "Johannesburg", "Flagship", "2010-04-15"),
    (2, "Mall of Africa", "Gauteng", "Midrand", "Mall", "2016-04-28"),
    (3, "Menlyn Park", "Gauteng", "Pretoria", "Mall", "2012-09-01"),
    (4, "Soweto Plaza", "Gauteng", "Soweto", "Township", "2014-06-16"),
    (5, "V&A Waterfront", "Western Cape", "Cape Town", "Flagship", "2009-11-20"),
    (6, "Canal Walk", "Western Cape", "Cape Town", "Mall", "2011-03-05"),
    (7, "Gateway Theatre", "KwaZulu-Natal", "Durban", "Mall", "2013-07-25"),
    (8, "Pavilion", "KwaZulu-Natal", "Westville", "Mall", "2015-10-10"),
    (9, "Mall of the North", "Limpopo", "Polokwane", "Mall", "2017-05-18"),
    (10, "Riverside Mall", "Mpumalanga", "Mbombela", "High Street", "2018-02-02"),
    (11, "Loch Logan", "Free State", "Bloemfontein", "High Street", "2019-08-30"),
    (12, "Boardwalk", "Eastern Cape", "Gqeberha", "High Street", "2020-12-01"),
]
df_stores = pd.DataFrame(stores, columns=[
    "store_id", "store_name", "province", "city", "store_type", "opened_date"])

# ------------------------------------------------------------
# TABLE 2: customers - 2,000 loyalty members
# ------------------------------------------------------------
first_names = ["Sipho", "Thandi", "Lerato", "Bongani", "Naledi", "Karabo", "Pieter", "Johan",
               "Anika", "Fatima", "Ayesha", "Sifiso", "Mpho", "Tshilidzi", "Rinae", "Rolivhuwa",
               "Nomsa", "Andile", "Zanele", "Kagiso", "Maryke", "Sanjay", "Priya", "Vusi",
               "Dikeledi", "Hennie", "Elna", "Tebogo", "Refilwe", "Lunga"]
last_names = ["Nkosi", "Dlamini", "Van der Merwe", "Botha", "Patel", "Mokoena", "Khumalo",
              "Pretorius", "Naidoo", "Mabaso", "Tshabalala", "Coetzee", "Govender", "Sithole",
              "Petersen", "Ndlovu", "Fourie", "Mthembu", "Jacobs", "Moodley", "Mahlangu",
              "Erasmus", "Zulu", "Meyer", "Baloyi", "Ngcobo", "Venter", "Kekana", "Pillay", "Radebe"]

# Customers live near the shops, so they share the 7 store provinces.
# Gauteng is the biggest, like in real life.
provinces = ["Gauteng", "Western Cape", "KwaZulu-Natal", "Limpopo",
             "Mpumalanga", "Free State", "Eastern Cape"]
province_weights = [0.40, 0.20, 0.16, 0.08, 0.06, 0.05, 0.05]
province_city = {s[2]: s[3] for s in stores}

N_CUSTOMERS = 2000
cust_province = rng.choice(provinces, size=N_CUSTOMERS, p=province_weights)
tiers = rng.choice(["Bronze", "Silver", "Gold", "Platinum"], size=N_CUSTOMERS,
                   p=[0.45, 0.30, 0.17, 0.08])
df_customers = pd.DataFrame({
    "customer_id": np.arange(1, N_CUSTOMERS + 1),
    "first_name": rng.choice(first_names, size=N_CUSTOMERS),
    "last_name": rng.choice(last_names, size=N_CUSTOMERS),
    "gender": rng.choice(["Female", "Male"], size=N_CUSTOMERS),
    "date_of_birth": [str(date(1960, 1, 1) + timedelta(days=int(d)))
                      for d in rng.integers(0, 365 * 45, size=N_CUSTOMERS)],
    "province": cust_province,
    "city": [province_city[p] for p in cust_province],
    "join_date": [str(date(2018, 1, 1) + timedelta(days=int(d)))
                  for d in rng.integers(0, 365 * 5, size=N_CUSTOMERS)],
    "loyalty_tier": tiers,
})

# ------------------------------------------------------------
# TABLE 3: products - 120 products in 7 categories
# ------------------------------------------------------------
categories = {
    "Groceries": (20, 150), "Beverages": (15, 120), "Household": (30, 250),
    "Personal Care": (25, 220), "Electronics": (300, 4500),
    "Clothing": (120, 900), "Home & Garden": (80, 1500),
}
suppliers = ["Tiger Brands", "Pioneer Foods", "Unilever SA", "Clicks Supply",
             "Defy", "Mr Price Sourcing", "Builders Direct"]
product_rows = []
pid = 1
for cat_i, (cat, (low, high)) in enumerate(categories.items()):
    for k in range(120 // len(categories) + (1 if cat_i < 120 % len(categories) else 0)):
        price = round(float(rng.uniform(low, high)), 2)
        cost = round(price * float(rng.uniform(0.55, 0.8)), 2)
        product_rows.append((pid, f"{cat} item {k + 1:02d}", cat, f"{cat} line {k % 3 + 1}",
                             cost, price, suppliers[cat_i]))
        pid += 1
df_products = pd.DataFrame(product_rows, columns=[
    "product_id", "product_name", "category", "subcategory",
    "unit_cost", "unit_price", "supplier"])

# ------------------------------------------------------------
# TABLE 4: orders - 25,000 shopping trips, 2023 to 2025
# ------------------------------------------------------------
# 200 members joined but never shopped, so 1,800 customers have orders.
# Each shopper has a hidden "appetite": some shop often and buy more.
shoppers = rng.choice(df_customers["customer_id"], size=1800, replace=False)
appetite = rng.lognormal(mean=0.0, sigma=0.6, size=len(shoppers))
basket_size = rng.lognormal(mean=0.0, sigma=0.35, size=len(shoppers))  # spend per trip
first_day = rng.integers(0, 365 * 2, size=len(shoppers))  # when each shopper starts

N_ORDERS = 25000
start = date(2023, 1, 1)
end = date(2025, 12, 31)
total_days = (end - start).days

order_cust_idx = rng.choice(len(shoppers), size=N_ORDERS, p=appetite / appetite.sum())
# Make sure every shopper has at least one order
order_cust_idx[:len(shoppers)] = np.arange(len(shoppers))
rng.shuffle(order_cust_idx)

order_days = []
for idx in order_cust_idx:
    d0 = first_day[idx]
    order_days.append(int(rng.integers(d0, total_days + 1)))
order_dates = [start + timedelta(days=d) for d in order_days]

# Shoppers mostly use a shop in their own province
store_by_province = df_stores.groupby("province")["store_id"].apply(list).to_dict()
cust_prov_lookup = df_customers.set_index("customer_id")["province"]
order_store = [int(rng.choice(store_by_province[cust_prov_lookup[shoppers[i]]]))
               for i in order_cust_idx]

df_orders = pd.DataFrame({
    "order_id": np.arange(1, N_ORDERS + 1),
    "order_date": [str(d) for d in order_dates],
    "customer_id": shoppers[order_cust_idx],
    "store_id": order_store,
    "channel": rng.choice(["In-Store", "Online", "Mobile App"], size=N_ORDERS,
                          p=[0.70, 0.20, 0.10]),
    "status": rng.choice(["Completed", "Returned", "Cancelled"], size=N_ORDERS,
                         p=[0.92, 0.05, 0.03]),
}).sort_values(["order_date", "order_id"]).reset_index(drop=True)
df_orders["order_id"] = np.arange(1, N_ORDERS + 1)

# ------------------------------------------------------------
# TABLE 5: order_items - the products inside each order
# ------------------------------------------------------------
cust_to_idx = {c: i for i, c in enumerate(shoppers)}
cat_of_product = df_products["category"].to_numpy()
price_of_product = df_products["unit_price"].to_numpy()
# Cheaper everyday items are bought more often than electronics
product_weights = 1 / np.sqrt(price_of_product)
product_weights = product_weights / product_weights.sum()

item_rows = []
item_id = 1
for order_id, cust in zip(df_orders["order_id"], df_orders["customer_id"]):
    n_lines = 1 + rng.poisson(2.3 * basket_size[cust_to_idx[cust]])
    prods = rng.choice(len(df_products), size=n_lines, p=product_weights)
    for p in prods:
        item_rows.append((item_id, int(order_id), int(p + 1),
                          int(1 + rng.poisson(0.6)), float(price_of_product[p]),
                          int(rng.choice([0, 5, 10, 15, 20], p=[0.6, 0.15, 0.12, 0.08, 0.05]))))
        item_id += 1
df_items = pd.DataFrame(item_rows, columns=[
    "order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount_pct"])

# ------------------------------------------------------------
# Save CSVs and load them into a SQLite database
# ------------------------------------------------------------
tables = {"stores": df_stores, "customers": df_customers, "products": df_products,
          "orders": df_orders, "order_items": df_items}
for name, df in tables.items():
    df.to_csv(os.path.join(DATA_DIR, f"{name}.csv"), index=False)

db_path = os.path.join(DATA_DIR, "mzansi_retail.db")
if os.path.exists(db_path):
    os.remove(db_path)
with sqlite3.connect(db_path) as con:
    with open(os.path.join(BASE_DIR, "sql", "01_schema.sql")) as f:
        con.executescript(f.read())
    for name, df in tables.items():
        df.to_sql(name, con, if_exists="append", index=False)

print(f"Dataset created in: {DATA_DIR}")
for name, df in tables.items():
    print(f"  {name}.csv: {len(df):,} rows")
print("Done.")
