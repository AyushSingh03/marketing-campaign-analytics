"""
Exploratory visuals for the campaign (data-visualization layer).
Saves PNG charts to outputs/figures/ — these mirror what the Looker Studio
dashboard shows, and are embedded in the README.

Run:
    python python/eda_report.py
"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA = Path("data/marketing_campaign.csv")
FIG = Path("outputs/figures")
FIG.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"figure.dpi": 120, "font.size": 10, "axes.grid": True,
                     "grid.alpha": 0.3, "axes.spines.top": False, "axes.spines.right": False})
BLUE, GREY = "#0b5394", "#9aa0a6"


def main():
    df = pd.read_csv(DATA)

    # 1. Funnel
    stages = ["contacted", "opened", "clicked", "converted"]
    vals = [df[s].sum() for s in stages]
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar([s.capitalize() for s in stages], vals, color=BLUE)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width()/2, v, f"{v/vals[0]:.0%}",
                ha="center", va="bottom")
    ax.set_title("Campaign funnel (share of contacted)")
    ax.set_ylabel("Customers")
    fig.tight_layout(); fig.savefig(FIG / "01_funnel.png"); plt.close(fig)

    # 2. A/B conversion
    cr = df.groupby("campaign_group").converted.mean()
    fig, ax = plt.subplots(figsize=(5, 4))
    bars = ax.bar(["A (control)", "B (treatment)"], cr.values * 100,
                  color=[GREY, BLUE])
    for b, v in zip(bars, cr.values * 100):
        ax.text(b.get_x() + b.get_width()/2, v, f"{v:.2f}%", ha="center", va="bottom")
    ax.set_title("Conversion rate: A/B test")
    ax.set_ylabel("Conversion rate (%)")
    fig.tight_layout(); fig.savefig(FIG / "02_ab_conversion.png"); plt.close(fig)

    # 3. Conversion by segment
    seg = df.groupby("segment").converted.mean().sort_values() * 100
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(seg.index, seg.values, color=BLUE)
    for i, v in enumerate(seg.values):
        ax.text(v, i, f" {v:.1f}%", va="center")
    ax.set_title("Conversion rate by customer segment")
    ax.set_xlabel("Conversion rate (%)")
    fig.tight_layout(); fig.savefig(FIG / "03_conversion_by_segment.png"); plt.close(fig)

    # 4. Conversion by channel
    ch = df.groupby("channel").converted.mean().sort_values() * 100
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(ch.index, ch.values, color=BLUE)
    for i, v in enumerate(ch.values):
        ax.text(v, i, f" {v:.1f}%", va="center")
    ax.set_title("Conversion rate by channel")
    ax.set_xlabel("Conversion rate (%)")
    fig.tight_layout(); fig.savefig(FIG / "04_conversion_by_channel.png"); plt.close(fig)

    print(f"Saved 4 figures to {FIG}")


if __name__ == "__main__":
    main()
