"""
Weather Forecasting - ML Lab Project
Predicts next-day mean temperature (regression) and rain/no-rain (classification)
Data: Open-Meteo Historical API (free, no API key). Default city: Raipur.

Run:  python weather_forecast.py
Or use your own CSV: python weather_forecast.py --csv weather.csv
(CSV needs columns: date, temp_mean, temp_max, temp_min, precip, wind_max, radiation)
"""
import argparse
import os
import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import (mean_absolute_error, mean_squared_error, r2_score,
                             accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix)
from sklearn.preprocessing import StandardScaler

os.makedirs("results", exist_ok=True)
os.makedirs("data", exist_ok=True)


# ---------------------------------------------------------------- 1. DATA
def fetch_data(lat=21.25, lon=81.63, start="2015-01-01", end="2025-12-31"):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat, "longitude": lon,
        "start_date": start, "end_date": end,
        "daily": ("temperature_2m_mean,temperature_2m_max,temperature_2m_min,"
                  "precipitation_sum,wind_speed_10m_max,shortwave_radiation_sum"),
        "timezone": "Asia/Kolkata",
    }
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    d = r.json()["daily"]
    df = pd.DataFrame({
        "date": pd.to_datetime(d["time"]),
        "temp_mean": d["temperature_2m_mean"],
        "temp_max": d["temperature_2m_max"],
        "temp_min": d["temperature_2m_min"],
        "precip": d["precipitation_sum"],
        "wind_max": d["wind_speed_10m_max"],
        "radiation": d["shortwave_radiation_sum"],
    })
    df.to_csv("data/weather_raw.csv", index=False)
    return df


def load_data(csv_path=None):
    if csv_path:
        return pd.read_csv(csv_path, parse_dates=["date"])
    if os.path.exists("data/weather_raw.csv"):
        return pd.read_csv("data/weather_raw.csv", parse_dates=["date"])
    return fetch_data()


# ---------------------------------------------------------------- 2. CLEAN + FEATURES
def build_features(df):
    df = df.sort_values("date").drop_duplicates("date").reset_index(drop=True)
    df = df.set_index("date").interpolate(limit_direction="both").reset_index()

    base_cols = ["temp_mean", "temp_max", "temp_min", "precip", "wind_max", "radiation"]

    # lag features (past 1,2,3,7 days)
    for col in base_cols:
        for lag in [1, 2, 3, 7]:
            df[f"{col}_lag{lag}"] = df[col].shift(lag)

    # rolling averages (shifted so today's value is not used to predict itself)
    for w in [3, 7, 14]:
        df[f"temp_roll{w}"] = df["temp_mean"].rolling(w).mean()
        df[f"precip_roll{w}"] = df["precip"].rolling(w).sum()

    # seasonality: cyclical encoding
    doy = df["date"].dt.dayofyear
    df["doy_sin"] = np.sin(2 * np.pi * doy / 365.25)
    df["doy_cos"] = np.cos(2 * np.pi * doy / 365.25)
    df["month"] = df["date"].dt.month

    # targets: tomorrow
    df["target_temp"] = df["temp_mean"].shift(-1)
    df["target_rain"] = (df["precip"].shift(-1) > 1.0).astype(int)  # >1mm = rainy

    return df.dropna().reset_index(drop=True)


# ---------------------------------------------------------------- 3. EVALUATION
def reg_metrics(y_true, y_pred):
    return {
        "MAE": mean_absolute_error(y_true, y_pred),
        "RMSE": np.sqrt(mean_squared_error(y_true, y_pred)),
        "R2": r2_score(y_true, y_pred),
    }


def clf_metrics(y_true, y_pred):
    return {
        "Accuracy": accuracy_score(y_true, y_pred),
        "Precision": precision_score(y_true, y_pred, zero_division=0),
        "Recall": recall_score(y_true, y_pred, zero_division=0),
        "F1": f1_score(y_true, y_pred, zero_division=0),
    }


# ---------------------------------------------------------------- 4. MAIN
def main(csv_path=None):
    raw = load_data(csv_path)
    df = build_features(raw)
    print(f"Dataset: {len(df)} rows, {df['date'].min().date()} to {df['date'].max().date()}")

    drop_cols = ["date", "target_temp", "target_rain"]
    features = [c for c in df.columns if c not in drop_cols]
    X, y_temp, y_rain = df[features], df["target_temp"], df["target_rain"]

    # time-based split (NO random shuffle -> avoids future leakage)
    split = int(len(df) * 0.8)
    X_tr, X_te = X.iloc[:split], X.iloc[split:]
    yt_tr, yt_te = y_temp.iloc[:split], y_temp.iloc[split:]
    yr_tr, yr_te = y_rain.iloc[:split], y_rain.iloc[split:]
    dates_te = df["date"].iloc[split:]

    # ---------- REGRESSION: next-day temperature
    scaler = StandardScaler().fit(X_tr)
    X_tr_s, X_te_s = scaler.transform(X_tr), scaler.transform(X_te)

    preds, results = {}, {}
    preds["Persistence (baseline)"] = X_te["temp_mean"].to_numpy()  # tomorrow = today

    lr = LinearRegression().fit(X_tr_s, yt_tr)
    preds["Linear Regression"] = lr.predict(X_te_s)

    rf = RandomForestRegressor(n_estimators=300, max_depth=15, n_jobs=-1, random_state=42)
    rf.fit(X_tr, yt_tr)
    preds["Random Forest"] = rf.predict(X_te)

    try:
        from xgboost import XGBRegressor  # type: ignore
        xgb = XGBRegressor(n_estimators=400, learning_rate=0.05, max_depth=5,
                           subsample=0.8, random_state=42)
        xgb.fit(X_tr, yt_tr)
        preds["XGBoost"] = xgb.predict(X_te)
    except ImportError:
        print("xgboost not installed, skipping (pip install xgboost)")

    for name, p in preds.items():
        results[name] = reg_metrics(yt_te, p)
    res_df = pd.DataFrame(results).T.round(3)
    print("\n=== Next-day Temperature Forecast ===")
    print(res_df)
    res_df.to_csv("results/regression_metrics.csv")

    # ---------- CLASSIFICATION: will it rain tomorrow?
    log = LogisticRegression(max_iter=1000, class_weight="balanced").fit(X_tr_s, yr_tr)
    rfc = RandomForestClassifier(n_estimators=300, max_depth=12, class_weight="balanced",
                                 n_jobs=-1, random_state=42).fit(X_tr, yr_tr)
    clf_results = {
        "Logistic Regression": clf_metrics(yr_te, log.predict(X_te_s)),
        "Random Forest": clf_metrics(yr_te, rfc.predict(X_te)),
    }
    clf_df = pd.DataFrame(clf_results).T.round(3)
    print("\n=== Rain / No-Rain Classification ===")
    print(clf_df)
    print("\nConfusion matrix (Random Forest):\n", confusion_matrix(yr_te, rfc.predict(X_te)))
    clf_df.to_csv("results/classification_metrics.csv")

    # ---------- PLOTS
    best = res_df["MAE"].drop("Persistence (baseline)").idxmin()
    d_plot = dates_te.to_numpy()[-120:]
    y_plot = yt_te.to_numpy()[-120:]
    p_plot = np.asarray(preds[best])[-120:]
    plt.figure(figsize=(12, 4))
    plt.plot(d_plot, y_plot, label="Actual")
    plt.plot(d_plot, p_plot, label=f"Predicted ({best})")
    plt.title("Next-day Temperature: Actual vs Predicted (last 120 days of test set)")
    plt.xlabel("Date"); plt.ylabel("Temperature (°C)")
    plt.legend(); plt.tight_layout()
    plt.savefig("results/actual_vs_predicted.png", dpi=150); plt.close()

    imp = pd.Series(rf.feature_importances_, index=features).nlargest(15)
    plt.figure(figsize=(8, 5))
    imp[::-1].plot(kind="barh")
    plt.title("Top 15 Feature Importances (Random Forest)")
    plt.tight_layout()
    plt.savefig("results/feature_importance.png", dpi=150); plt.close()

    err = pd.DataFrame({"month": dates_te.dt.month.to_numpy(),
                        "abs_err": np.abs(yt_te.to_numpy() - np.asarray(preds[best]))})
    err.groupby("month")["abs_err"].mean().plot(kind="bar", figsize=(8, 4))
    plt.title(f"Mean Absolute Error by Month ({best})")
    plt.ylabel("MAE (°C)"); plt.tight_layout()
    plt.savefig("results/error_by_month.png", dpi=150); plt.close()

    print("\nPlots saved in ./results/")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=None, help="optional path to your own CSV")
    args = ap.parse_args()
    main(args.csv)
