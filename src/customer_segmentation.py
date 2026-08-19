from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"


def score_quartiles(series: pd.Series, ascending: bool = True) -> pd.Series:
    """Assign stable 1-to-4 quantile scores, tolerating tied values."""
    ranked = series.rank(method="first", ascending=ascending)
    return pd.qcut(ranked, q=4, labels=[1, 2, 3, 4]).astype(int)


def assign_segment(row: pd.Series) -> str:
    """Map RFM scores to practical customer segments."""
    rfm_score = row["R_Score"] + row["F_Score"] + row["M_Score"]
    if rfm_score >= 10 and row["R_Score"] >= 3:
        return "Champions"
    if row["R_Score"] >= 3 and row["F_Score"] >= 3:
        return "Loyal Customers"
    if row["R_Score"] >= 3 and row["F_Score"] <= 2:
        return "New Customers"
    if row["R_Score"] <= 2 and row["F_Score"] >= 3:
        return "At Risk"
    if rfm_score <= 5:
        return "Lost"
    return "Potential Loyalists"


def run_segmentation() -> None:
    """Build customer RFM segments from delivered Olist orders."""
    orders = pd.read_csv(
        PROCESSED_DIR / "cleaned_orders.csv",
        parse_dates=["order_purchase_timestamp"],
    )
    items = pd.read_csv(PROCESSED_DIR / "cleaned_order_items.csv")
    customers = pd.read_csv(PROCESSED_DIR / "cleaned_customers.csv")

    delivered_orders = orders.loc[orders["order_status"] == "delivered"].copy()
    transactions = delivered_orders[["order_id", "customer_id", "order_purchase_timestamp"]].merge(
        items[["order_id", "price"]],
        on="order_id",
        how="inner",
    )

    if transactions.empty:
        raise ValueError("No delivered order-item transactions are available for segmentation")

    snapshot_date = transactions["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
    rfm = (
        transactions.groupby("customer_id")
        .agg(
            Recency=("order_purchase_timestamp", lambda values: (snapshot_date - values.max()).days),
            Frequency=("order_id", "nunique"),
            Monetary=("price", "sum"),
        )
        .reset_index()
    )

    rfm["R_Score"] = score_quartiles(rfm["Recency"], ascending=False)
    rfm["F_Score"] = score_quartiles(rfm["Frequency"])
    rfm["M_Score"] = score_quartiles(rfm["Monetary"])
    rfm["RFM_Score"] = rfm[["R_Score", "F_Score", "M_Score"]].sum(axis=1)
    rfm["Segment"] = rfm.apply(assign_segment, axis=1)

    rfm = rfm.merge(
        customers[["customer_id", "customer_unique_id"]],
        on="customer_id",
        how="left",
    )
    output_columns = [
        "customer_id", "customer_unique_id", "Recency", "Frequency", "Monetary",
        "R_Score", "F_Score", "M_Score", "RFM_Score", "Segment",
    ]
    output_path = PROCESSED_DIR / "rfm_segments.csv"
    rfm[output_columns].to_csv(output_path, index=False)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    segment_counts = rfm["Segment"].value_counts().sort_values(ascending=False)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=segment_counts.values, y=segment_counts.index, hue=segment_counts.index, legend=False, palette="viridis")
    plt.title("Customer RFM Segments")
    plt.xlabel("Number of Customers")
    plt.ylabel("Segment")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "customer_segments.png")
    plt.close()

    print(f"Saved {len(rfm):,} customer segments to {output_path}")
    print(f"Saved segment chart to {FIGURES_DIR / 'customer_segments.png'}")


if __name__ == "__main__":
    run_segmentation()
