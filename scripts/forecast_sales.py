import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import seaborn as sns
sns.set()

def load_monthly(df_path):
    df = pd.read_csv(df_path, parse_dates=["InvoiceDate"])
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    ts = df.set_index("InvoiceDate").resample("M")["Revenue"].sum().reset_index()
    ts["month"] = ts["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
    ts = ts[["month","Revenue"]]
    return ts

def forecast_linear(ts, months_ahead=6):
    # create numeric index
    ts = ts.copy()
    ts["t"] = np.arange(len(ts))
    X = ts[["t"]].values
    y = ts["Revenue"].values
    model = LinearRegression()
    model.fit(X, y)
    future_t = np.arange(len(ts), len(ts)+months_ahead).reshape(-1,1)
    preds = model.predict(future_t)
    future_months = pd.date_range(ts["month"].iloc[-1] + pd.offsets.MonthBegin(1), periods=months_ahead, freq='MS')
    df_future = pd.DataFrame({"month": future_months, "Revenue": preds})
    return df_future, model

def plot_forecast(ts, future, out_path):
    plt.figure(figsize=(10,5))
    plt.plot(ts["month"], ts["Revenue"], label="Historical")
    plt.plot(future["month"], future["Revenue"], label="Forecast", linestyle="--", marker="o")
    plt.title("Monthly Revenue Forecast (Linear baseline)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print("Saved forecast plot to", out_path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", default="../outputs/figures")
    parser.add_argument("--months", type=int, default=6)
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    ts = load_monthly(args.input)
    if len(ts) < 6:
        print("Not enough data for forecasting. Need at least 6 months.")
        return
    future, model = forecast_linear(ts, months_ahead=args.months)
    (out/ "monthly_forecast.csv").write_text(future.to_csv(index=False))
    plot_forecast(ts, future, out/"monthly_forecast.png")
    print("Forecast saved.")

if __name__ == "__main__":
    main()
