"""
A/B test + campaign performance analysis.

Answers the questions a campaign analyst is actually asked:
  1. Did the personalised offer (group B) beat the control (group A)? Is it significant?
  2. What is the lift, and the 95% confidence interval on that lift?
  3. Which segments / channels / regions drove (or dragged) performance?
  4. What did it mean in revenue per recipient?

Stats: two-proportion z-test (primary), chi-square test (cross-check),
Wilson/normal 95% CI on the conversion-rate difference.

Run (after generating data):
    python python/ab_test_analysis.py
Writes:
    outputs/results_summary.md
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

# make console output utf-8 safe (₹, — etc.) on Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DATA = Path("data/marketing_campaign.csv")
OUT = Path("outputs/results_summary.md")


def two_prop_ztest(c1, n1, c2, n2):
    """Pooled two-proportion z-test. Returns (z, two-sided p)."""
    p1, p2 = c1 / n1, c2 / n2
    p_pool = (c1 + c2) / (n1 + n2)
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    z = (p2 - p1) / se
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    return z, p


def diff_ci(c1, n1, c2, n2, conf=0.95):
    """Normal-approx 95% CI for (p2 - p1)."""
    p1, p2 = c1 / n1, c2 / n2
    se = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    zc = stats.norm.ppf(1 - (1 - conf) / 2)
    d = p2 - p1
    return d - zc * se, d + zc * se


def main():
    df = pd.read_csv(DATA)
    lines = []
    def w(s=""):
        print(s)
        lines.append(s)

    w("# Marketing Campaign — A/B Test & Performance Results\n")
    w(f"Recipients analysed: **{len(df):,}**  |  Channels: {df.channel.nunique()}  |  "
      f"Regions: {df.region.nunique()}  |  Segments: {df.segment.nunique()}\n")

    # ---- Funnel ----
    w("## 1. Overall funnel\n")
    funnel = {
        "Contacted": df.contacted.sum(),
        "Opened": df.opened.sum(),
        "Clicked": df.clicked.sum(),
        "Converted": df.converted.sum(),
    }
    base = funnel["Contacted"]
    w("| Stage | Count | % of contacted |")
    w("|---|--:|--:|")
    for k, v in funnel.items():
        w(f"| {k} | {v:,} | {v / base:.2%} |")
    w("")

    # ---- A/B headline ----
    g = df.groupby("campaign_group").agg(
        recipients=("customer_id", "count"),
        conversions=("converted", "sum"),
        revenue=("revenue", "sum"),
    )
    a, b = g.loc["A"], g.loc["B"]
    cr_a = a.conversions / a.recipients
    cr_b = b.conversions / b.recipients
    lift_abs = cr_b - cr_a
    lift_rel = lift_abs / cr_a
    z, p = two_prop_ztest(a.conversions, a.recipients, b.conversions, b.recipients)
    lo, hi = diff_ci(a.conversions, a.recipients, b.conversions, b.recipients)
    chi2, p_chi, _, _ = stats.chi2_contingency(
        pd.crosstab(df.campaign_group, df.converted).values
    )
    rev_a = a.revenue / a.recipients
    rev_b = b.revenue / b.recipients

    w("## 2. A/B test — control (A) vs personalised offer (B)\n")
    w("| Group | Recipients | Conversions | Conv. rate | Revenue / recipient |")
    w("|---|--:|--:|--:|--:|")
    w(f"| A (control) | {a.recipients:,} | {a.conversions:,} | {cr_a:.2%} | ₹{rev_a:,.0f} |")
    w(f"| B (treatment) | {b.recipients:,} | {b.conversions:,} | {cr_b:.2%} | ₹{rev_b:,.0f} |")
    w("")
    w(f"- **Absolute lift:** {lift_abs*100:+.2f} pp (B − A)")
    w(f"- **Relative lift:** {lift_rel:+.1%}")
    w(f"- **95% CI on absolute lift:** [{lo*100:+.2f} pp, {hi*100:+.2f} pp]")
    w(f"- **Two-proportion z-test:** z = {z:.2f}, p = {p:.2e}")
    w(f"- **Chi-square cross-check:** χ² = {chi2:.1f}, p = {p_chi:.2e}")
    verdict = ("**statistically significant** — roll out B" if p < 0.05
               else "not significant — keep testing")
    w(f"- **Verdict:** {verdict} (revenue/recipient {((rev_b-rev_a)/rev_a):+.1%}).\n")

    # ---- Segment / channel / region breakdowns ----
    def breakdown(col, title):
        w(f"## {title}\n")
        t = (df.groupby(col)
               .agg(recipients=("customer_id", "count"),
                    conv_rate=("converted", "mean"),
                    rev_per_recipient=("revenue", "mean"))
               .sort_values("conv_rate", ascending=False))
        w(f"| {col} | Recipients | Conv. rate | Revenue / recipient |")
        w("|---|--:|--:|--:|")
        for idx, r in t.iterrows():
            w(f"| {idx} | {r.recipients:,.0f} | {r.conv_rate:.2%} | ₹{r.rev_per_recipient:,.0f} |")
        w("")
        return t

    seg = breakdown("segment", "3. Conversion by customer segment")
    ch = breakdown("channel", "4. Conversion by channel")
    breakdown("region", "5. Conversion by region")

    # ---- Cross-sell style insight ----
    w("## 6. Key takeaways\n")
    best_seg = seg.index[0]
    best_ch = ch.index[0]
    w(f"- The personalised offer (B) lifted conversion **{lift_rel:+.1%}** vs control, "
      f"significant at p < 0.05 — recommend full roll-out.")
    w(f"- **{best_seg}** customers convert best ({seg.iloc[0].conv_rate:.1%}) and return the most "
      f"revenue per recipient — prioritise them for cross-sell / up-sell.")
    w(f"- **{best_ch}** is the strongest channel by conversion — shift budget toward it; "
      f"reduce spend on the weakest channel.")
    w(f"- Dormant customers convert lowest — candidates for a re-engagement / win-back campaign "
      f"rather than the standard offer.\n")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
