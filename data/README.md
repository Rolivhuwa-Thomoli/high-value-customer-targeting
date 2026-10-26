# Data

There is no data file in this folder on GitHub. Run `python src/generate_data.py` to make it.

The script makes a made-up South African shop called **Mzansi Retail**:
12 stores, 2,000 loyalty members, 120 products, 25,000 orders (2023 to 2025) and about 86,000 order lines.
It saves the tables as CSV files and loads them into `mzansi_retail.db` (SQLite).
The seed is fixed (42), so you get the same data every time.

No real people are in this data. The names are picked at random from a list.
