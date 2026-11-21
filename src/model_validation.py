"""Member 4: independently re-estimate and check the four saved regression models.

Run from the repository root: python src/model_validation.py
The models are observational, not causal.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "main_analysis.csv"
REFERENCE = ROOT / "reports" / "model_comparison.csv"
OUT = ROOT / "reports" / "team"
OUT.mkdir(parents=True, exist_ok=True)

main = pd.read_csv(DATA)
ref = pd.read_csv(REFERENCE)
assert len(main) == 2713
main["Log_Mortality"] = np.log(main["Under5_Mortality_Rate"])
log_formula = "Log_Mortality ~ PM25 + Water_AtLeastBasic_Pct + C(ISO3) + C(Year)"
level_formula = "Under5_Mortality_Rate ~ PM25 + Water_AtLeastBasic_Pct + C(ISO3) + C(Year)"

def fit(formula, frame):
    return smf.ols(formula=formula, data=frame).fit(
        cov_type="cluster", cov_kwds={"groups": frame["ISO3"]}
    )

models = {
    "Level Fixed Effects": fit(level_formula, main),
    "Log Fixed Effects": fit(log_formula, main),
}
sens = main[main["Under5_Mortality_Rate"] <= 200].copy()
models["Log Sensitivity"] = fit(log_formula, sens)

fd = main.sort_values(["ISO3", "Year"]).copy()
fd["Year_Gap"] = fd.groupby("ISO3")["Year"].diff()
fd["Delta_Log_Mortality"] = fd.groupby("ISO3")["Log_Mortality"].diff()
fd["Delta_PM25"] = fd.groupby("ISO3")["PM25"].diff()
fd["Delta_Water"] = fd.groupby("ISO3")["Water_AtLeastBasic_Pct"].diff()
fd = fd[fd["Year_Gap"].eq(1)].dropna(subset=[
    "Delta_Log_Mortality", "Delta_PM25", "Delta_Water"
]).copy()
models["First Differences"] = fit(
    "Delta_Log_Mortality ~ Delta_PM25 + Delta_Water + C(Year)", fd
)

rows = []
for model_name, model in models.items():
    for label, variable in [
        ("PM2.5", "Delta_PM25" if model_name == "First Differences" else "PM25"),
        ("Drinking Water", "Delta_Water" if model_name == "First Differences" else "Water_AtLeastBasic_Pct"),
    ]:
        match = ref[(ref["Model"] == model_name) & (ref["Factor"] == label)]
        if len(match) != 1:
            raise ValueError(f"Expected exactly one reference row for {model_name} / {label}")
        reference = match.iloc[0]
        coefficient = float(model.params[variable])
        pvalue = float(model.pvalues[variable])
        nobs = int(model.nobs)
        r2 = float(model.rsquared)
        ok = (
            abs(coefficient - float(reference["Coefficient"])) < .00025
            and abs(r2 - float(reference["R_Squared"])) < .0006
            and nobs == int(reference["Observations"])
            and abs(pvalue - float(reference["P_Value"])) < .002
        )
        rows.append({
            "Model": model_name, "Factor": label,
            "Reestimated_Coefficient": coefficient,
            "Saved_Coefficient": reference["Coefficient"],
            "Reestimated_P": pvalue, "Saved_P": reference["P_Value"],
            "Records": nobs, "R_Squared": r2, "Passed": ok,
        })

result = pd.DataFrame(rows)
result.to_csv(OUT / "model_validation_results.csv", index=False)
print("=== MODEL VALIDATION ===")
print(result[["Model", "Factor", "Records", "Passed"]].to_string(index=False))
print("SAVED: reports/team/model_validation_results.csv")
if not result["Passed"].all():
    raise SystemExit("FAILED: review model version and assumptions")
print("ALL 8 COEFFICIENT CHECKS PASSED")
print("Note: model agreement does not demonstrate causation.")
