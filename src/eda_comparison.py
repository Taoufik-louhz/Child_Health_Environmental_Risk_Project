"""Member 3: independently create two EDA figures and a summary table.

Run from the repository root: python src/eda_comparison.py
"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "processed" / "main_analysis.csv"
OUT = ROOT / "reports" / "team"
OUT.mkdir(parents=True, exist_ok=True)

if not DATA_FILE.exists():
    raise FileNotFoundError(f"Missing {DATA_FILE}")
df = pd.read_csv(DATA_FILE)
assert df[["ISO3", "Year"]].duplicated().sum() == 0

annual = df.groupby("Year", as_index=False).agg(
    Countries=("ISO3", "nunique"),
    Avg_Mortality=("Under5_Mortality_Rate", "mean"),
    Avg_PM25=("PM25", "mean"),
    Avg_Basic_Water=("Water_AtLeastBasic_Pct", "mean"),
)
annual.to_csv(OUT / "eda_annual_summary.csv", index=False)

# Separate plots prevent different units from being confused.
fig, ax = plt.subplots(figsize=(9, 4.6))
ax.plot(annual["Year"], annual["Avg_Mortality"], marker="o")
ax.set(title="Mean under-five mortality across available country-years",
       xlabel="Year", ylabel="Deaths per 1,000 live births")
ax.grid(alpha=.25)
fig.text(.5, .01, "Unweighted country-year mean; country coverage can vary by year.",
         ha="center", fontsize=9)
fig.tight_layout(rect=[0, .05, 1, 1])
fig.savefig(OUT / "eda_mortality_trend.png", dpi=180)
plt.close(fig)

# A distinct, meaningful comparison between two countries in our dataset.
selected = df[df["Country"].isin(["Morocco", "Hungary"])].copy()
if selected["Country"].nunique() != 2:
    raise ValueError("Morocco or Hungary is missing; review selected examples")
fig, ax = plt.subplots(figsize=(9, 4.6))
for country, subset in selected.groupby("Country"):
    subset = subset.sort_values("Year")
    ax.plot(subset["Year"], subset["PM25"], marker="o", label=country)
ax.set(title="PM2.5 comparison: Morocco and Hungary (2010-2023)",
       xlabel="Year", ylabel="PM2.5 (micrograms/m3)")
ax.grid(alpha=.25)
ax.legend()
fig.tight_layout()
fig.savefig(OUT / "eda_pm25_country_comparison.png", dpi=180)
plt.close(fig)

print("=== EDA COMPARISON ===")
print(f"Records: {len(df)} | Countries: {df['ISO3'].nunique()}")
print(f"Annual summary rows: {len(annual)}")
print("SAVED: reports/team/eda_annual_summary.csv")
print("SAVED: reports/team/eda_mortality_trend.png")
print("SAVED: reports/team/eda_pm25_country_comparison.png")
print("EDA analysis completed successfully.")
