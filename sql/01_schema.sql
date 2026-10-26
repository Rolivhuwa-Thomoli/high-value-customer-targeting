-- MzansiRetail tables (SQLite version).
-- The same tables work in SQL Server: change TEXT to NVARCHAR and REAL to DECIMAL(10,2).

CREATE TABLE stores (
    store_id     INTEGER PRIMARY KEY,
    store_name   TEXT NOT NULL,
    province     TEXT NOT NULL,
    city         TEXT NOT NULL,
    store_type   TEXT NOT NULL,      -- Flagship / Mall / High Street / Township
    opened_date  TEXT NOT NULL
);

CREATE TABLE customers (
    customer_id   INTEGER PRIMARY KEY,
    first_name    TEXT NOT NULL,
    last_name     TEXT NOT NULL,
    gender        TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    province      TEXT NOT NULL,
    city          TEXT NOT NULL,
    join_date     TEXT NOT NULL,
    loyalty_tier  TEXT NOT NULL      -- Bronze / Silver / Gold / Platinum
);

CREATE TABLE products (
    product_id   INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category     TEXT NOT NULL,
    subcategory  TEXT NOT NULL,
    unit_cost    REAL NOT NULL,
    unit_price   REAL NOT NULL,
    supplier     TEXT NOT NULL
);

CREATE TABLE orders (
    order_id    INTEGER PRIMARY KEY,
    order_date  TEXT NOT NULL,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    store_id    INTEGER NOT NULL REFERENCES stores(store_id),
    channel     TEXT NOT NULL,       -- In-Store / Online / Mobile App
    status      TEXT NOT NULL        -- Completed / Returned / Cancelled
);

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id      INTEGER NOT NULL REFERENCES orders(order_id),
    product_id    INTEGER NOT NULL REFERENCES products(product_id),
    quantity      INTEGER NOT NULL,
    unit_price    REAL NOT NULL,
    discount_pct  INTEGER NOT NULL   -- 0, 5, 10, 15 or 20
);
