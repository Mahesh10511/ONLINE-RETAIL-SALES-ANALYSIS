import argparse
import random
from datetime import datetime, timedelta
import csv
import os

PRODUCTS = [
    ("P001","T-Shirt","Apparel"),
    ("P002","Running Shoes","Footwear"),
    ("P003","Coffee Mug","Home"),
    ("P004","Wireless Mouse","Electronics"),
    ("P005","Notebook","Stationery"),
    ("P006","Sunglasses","Accessories"),
    ("P007","Backpack","Bags"),
    ("P008","Headphones","Electronics"),
    ("P009","Water Bottle","Home"),
    ("P010","Hoodie","Apparel"),
]

COUNTRIES = ["United Kingdom","United States","Germany","France","Spain","India","Australia"]

def random_date(start, end):
    delta = end - start
    seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=seconds)

def generate_rows(n=1000, start_date=None, end_date=None):
    if start_date is None:
        start_date = datetime.now() - timedelta(days=365)
    if end_date is None:
        end_date = datetime.now()
    rows = []
    invoice = 100000
    for i in range(n):
        invoice += 1 if random.random() < 0.6 else 0  # sometimes multiple rows per invoice
        invoice_no = f"INV{invoice}"
        date = random_date(start_date, end_date)
        customer_id = random.randint(1000, 1100)
        country = random.choice(COUNTRIES)
        prod = random.choice(PRODUCTS)
        qty = random.choices([1,1,1,2,3,4], weights=[40,40,10,5,3,2])[0]
        unit_price = round(random.uniform(5,120) * (1.0 if prod[2]!="Electronics" else 4.0), 2)
        rows.append({
            "InvoiceNo": invoice_no,
            "InvoiceDate": date.strftime("%Y-%m-%d %H:%M:%S"),
            "CustomerID": customer_id,
            "Country": country,
            "StockCode": prod[0],
            "Description": prod[1],
            "Quantity": qty,
            "UnitPrice": unit_price
        })
    return rows

def write_csv(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fieldnames = ["InvoiceNo","InvoiceDate","CustomerID","Country","StockCode","Description","Quantity","UnitPrice"]
    with open(path, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="../data/sample_retail_data.csv", help="output csv path")
    parser.add_argument("--n", type=int, default=5000, help="number of transaction rows")
    args = parser.parse_args()
    rows = generate_rows(n=args.n)
    write_csv(rows, args.out)
    print(f"Wrote {len(rows)} rows to {args.out}")

if __name__ == "__main__":
    main()
