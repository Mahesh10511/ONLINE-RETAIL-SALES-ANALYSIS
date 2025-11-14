import argparse
import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid", palette="deep")

def load_data(path):
    df = pd.read_csv(path, parse_dates=["InvoiceDate"])
    # basic cleaning
    df = df.dropna(subset=["InvoiceNo","InvoiceDate","CustomerID","Quantity","UnitPrice"])
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["OrderDate"] = df["InvoiceDate"].dt.date
    return df

def kpis(df):
    total_revenue = df["Revenue"].sum()
    total_orders = df["InvoiceNo"].nunique()
    total_customers = df["CustomerID"].nunique()
    avg_order_value = df.groupby("InvoiceNo")["Revenue"].sum().mean()
    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "avg_order_value": avg_order_value
    }

def sales_over_time(df, out_dir):
    ts = df.groupby(pd.Grouper(key="InvoiceDate", freq="W"))["Revenue"].sum().reset_index()
    plt.figure(figsize=(10,5))
    sns.lineplot(data=ts, x="InvoiceDate", y="Revenue")
    plt.title("Weekly Revenue")
    plt.xlabel("")
    plt.tight_layout()
    p = Path(out_dir)/"weekly_revenue.png"
    plt.savefig(p)
    plt.close()
    print("Saved", p)

def top_products(df, out_dir, n=10):
    prod = df.groupby("Description")["Revenue"].sum().sort_values(ascending=False).head(n)
    plt.figure(figsize=(8,6))
    sns.barplot(x=prod.values, y=prod.index)
    plt.title("Top Products by Revenue")
    plt.xlabel("Revenue")
    plt.tight_layout()
    p = Path(out_dir)/"top_products.png"
    plt.savefig(p)
    plt.close()
    print("Saved", p)
    prod.to_csv(Path(out_dir)/"top_products.csv")

def top_customers(df, out_dir, n=10):
    cust = df.groupby("CustomerID")["Revenue"].sum().sort_values(ascending=False).head(n)
    plt.figure(figsize=(8,6))
    sns.barplot(x=cust.values, y=cust.index.astype(str))
    plt.title("Top Customers by Revenue")
    plt.xlabel("Revenue")
    plt.tight_layout()
    p = Path(out_dir)/"top_customers.png"
    plt.savefig(p)
    plt.close()
    print("Saved", p)
    cust.to_csv(Path(out_dir)/"top_customers.csv")

def monthly_sales_table(df, out_dir):
    ms = df.set_index("InvoiceDate").resample("M")["Revenue"].sum().reset_index()
    ms["month"] = ms["InvoiceDate"].dt.to_period("M").astype(str)
    ms[["month","Revenue"]].to_csv(Path(out_dir)/"monthly_revenue.csv", index=False)
    print("Saved monthly_revenue.csv")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="path to CSV")
    parser.add_argument("--out", default="../outputs/figures", help="output dir")
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    df = load_data(args.input)
    print("Loaded rows:", len(df))
    metrics = kpis(df)
    print("KPIs:", metrics)
    # save summary
    pd.Series(metrics).to_csv(Path(out)/"kpis.csv")

    sales_over_time(df, out)
    top_products(df, out)
    top_customers(df, out)
    monthly_sales_table(df, out)
    print("EDA complete. Outputs in", out)

if __name__ == "__main__":
    from pathlib import Path
    main()
