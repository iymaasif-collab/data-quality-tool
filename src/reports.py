"""Export CSV summaries and a chart."""
import matplotlib
matplotlib.use("Agg")  # render to file without opening a window
import matplotlib.pyplot as plt
import pandas as pd


def save_quality_summary(stats: dict, path) -> None:
    pd.DataFrame(list(stats.items()), columns=["metric", "value"]).to_csv(path, index=False)


def save_rejected(rejected: pd.DataFrame, path) -> None:
    rejected.to_csv(path, index=False)


def save_chart(monthly: pd.DataFrame, products: pd.DataFrame, path) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    ax1.bar(monthly["month"], monthly["revenue"], color="#D40511")
    ax1.set_title("Monthly Revenue")
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Revenue ($)")
    ax1.tick_params(axis="x", rotation=45)

    ax2.barh(products["product"], products["revenue"], color="#FFCC00")
    ax2.set_title("Top Products by Revenue")
    ax2.set_xlabel("Revenue ($)")
    ax2.invert_yaxis()  # biggest on top

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)