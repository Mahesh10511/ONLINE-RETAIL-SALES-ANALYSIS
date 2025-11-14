import argparse
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def load_prepare(df_path):
    df = pd.read_csv(df_path, parse_dates=["InvoiceDate"])
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    # only positive revenue
    df = df[df["Revenue"] > 0]
    return df

def compute_rfm(df, snapshot_date=None):
    if snapshot_date is None:
        snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)
    agg = df.groupby("CustomerID").agg({
        "InvoiceDate": lambda x: (snapshot_date - x.max()).days,
        "InvoiceNo": "nunique",
        "Revenue": "sum"
    }).reset_index().rename(columns={
        "InvoiceDate": "Recency",
        "InvoiceNo": "Frequency",
        "Revenue": "Monetary"
    })
    return agg

def run_kmeans(rfm, n_clusters=3):
    rfm_clean = rfm.copy()
    # log transform Monetary to reduce skew
    rfm_clean["Monetary"] = rfm_clean["Monetary"].apply(lambda x: np.log1p(x))
    X = rfm_clean[["Recency","Frequency","Monetary"]].values
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(Xs)
    rfm["Cluster"] = labels
    return rfm, kmeans

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", default="../outputs/reports")
    parser.add_argument("--clusters", type=int, default=3)
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    df = load_prepare(args.input)
    rfm = compute_rfm(df)
    rfm_clust, model = run_kmeans(rfm, n_clusters=args.clusters)
    rfm_clust.to_csv(out/"rfm_customers.csv", index=False)
    print("Saved rfm_customers.csv to", out)
    # basic cluster summary
    summary = rfm_clust.groupby("Cluster").agg({"Recency":"mean","Frequency":"mean","Monetary":"mean","CustomerID":"count"})
    summary = summary.rename(columns={"CustomerID":"Count"})
    summary.to_csv(out/"rfm_cluster_summary.csv")
    print("Saved rfm_cluster_summary.csv")
    print(summary)

if __name__ == "__main__":
    main()
