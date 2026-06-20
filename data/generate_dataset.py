"""
Generate a realistic marketing-campaign dataset for A/B and performance analysis.

The scenario: a cross-sell / customer-engagement campaign promoting an offer to an
existing customer base across multiple channels and regions. Customers are randomly
split into a control group (A, standard offer) and a treatment group (B, personalised
offer). We model a realistic funnel: contacted -> opened -> clicked -> converted.

Run:
    python data/generate_dataset.py
Output:
    data/marketing_campaign.csv
"""
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)        # fixed seed -> reproducible numbers
N = 40_000

REGIONS  = ["North", "South", "East", "West", "Central"]
SEGMENTS = ["New", "Active", "Dormant", "High-Value"]
CHANNELS = ["Email", "SMS", "Push", "Web"]
OFFERS   = ["Discount", "Cashback", "Bundle", "Loyalty-Points"]

# Base funnel probabilities per channel: P(open), P(click|open)
CHANNEL_OPEN  = {"Email": 0.42, "SMS": 0.55, "Push": 0.38, "Web": 0.30}
CHANNEL_CLICK = {"Email": 0.28, "SMS": 0.22, "Push": 0.18, "Web": 0.25}

# Base conversion (given click) by segment
SEG_CONV = {"New": 0.10, "Active": 0.22, "Dormant": 0.06, "High-Value": 0.30}
SEG_WEIGHTS = [0.30, 0.40, 0.20, 0.10]

# Treatment (group B) uplift multipliers — the personalised offer performs better
B_OPEN_MULT  = 1.06
B_CLICK_MULT = 1.12
B_CONV_MULT  = 1.25     # the headline lift we want the A/B test to detect

AOV = {"New": 1800, "Active": 2600, "Dormant": 1500, "High-Value": 5200}  # avg order value (INR)


def clip(p):
    return np.clip(p, 0.0, 0.98)


def main():
    age = RNG.integers(21, 70, N)
    region = RNG.choice(REGIONS, N)
    segment = RNG.choice(SEGMENTS, N, p=SEG_WEIGHTS)
    channel = RNG.choice(CHANNELS, N, p=[0.45, 0.25, 0.15, 0.15])
    group = RNG.choice(["A", "B"], N)            # 50/50 split
    offer = RNG.choice(OFFERS, N)
    prior_purchases = RNG.poisson(2.2, N)

    is_b = (group == "B")

    p_open = np.array([CHANNEL_OPEN[c] for c in channel])
    p_open = clip(p_open * np.where(is_b, B_OPEN_MULT, 1.0))
    opened = RNG.random(N) < p_open

    p_click = np.array([CHANNEL_CLICK[c] for c in channel])
    p_click = clip(p_click * np.where(is_b, B_CLICK_MULT, 1.0))
    clicked = opened & (RNG.random(N) < p_click)

    p_conv = np.array([SEG_CONV[s] for s in segment])
    # loyal customers (more prior purchases) convert a bit more
    p_conv = p_conv * (1 + 0.03 * np.minimum(prior_purchases, 5))
    p_conv = clip(p_conv * np.where(is_b, B_CONV_MULT, 1.0))
    converted = clicked & (RNG.random(N) < p_conv)

    revenue = np.where(
        converted,
        np.array([AOV[s] for s in segment]) * RNG.uniform(0.6, 1.6, N),
        0.0,
    ).round(0)

    df = pd.DataFrame({
        "customer_id": np.arange(1, N + 1),
        "age": age,
        "age_group": pd.cut(age, [20, 30, 40, 50, 60, 70],
                            labels=["21-30", "31-40", "41-50", "51-60", "61-69"]),
        "region": region,
        "segment": segment,
        "channel": channel,
        "campaign_group": group,
        "offer_type": offer,
        "prior_purchases": prior_purchases,
        "contacted": 1,
        "opened": opened.astype(int),
        "clicked": clicked.astype(int),
        "converted": converted.astype(int),
        "revenue": revenue,
    })

    out = "data/marketing_campaign.csv"
    df.to_csv(out, index=False)
    print(f"Wrote {out}  rows={len(df):,}")
    print(f"Overall conversion: {df.converted.mean():.3%}")
    print(df.groupby('campaign_group').converted.mean())


if __name__ == "__main__":
    main()
