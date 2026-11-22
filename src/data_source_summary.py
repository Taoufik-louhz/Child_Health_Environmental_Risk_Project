"""Member 2: inspect processed international data and document preprocessing outputs.

Run from the project root: python src/data_source_summary.py
The original raw files are NOT bundled in the private GitHub repository.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUT = ROOT / "reports" / "team"
OUT.mkdir(parents=True, exist_ok=True)

SOURCES = [
    ("UNICEF under-five mortality", "unicef_under5_mortality.csv", "Under5_Mortality_Rate", "per 1,000 live births"),
    ("WHO PM2.5", "who_pm25.csv", "PM25", "micrograms/m3"),
    ("Integrated master", "master_dataset.csv", "Under5_Mortality_Rate", "per 1,000 live births"),
    ("Main analysis", "main_analysis.csv", "Water_AtLeastBasic_Pct", "percentage"),
    ("Safely managed sample", "secondary_analysis.csv", "Water_SafelyManaged_Pct", "percentage"),
]

records = []
for label, filename, indicator, unit in SOURCES:
    path = DATA / filename
    if not path.is_file():
        raise FileNotFoundError(f"Missing {path}. Clone the full project first.")
    df = pd.read_csv(path)
    needed = {"ISO3", "Year", indicator}
    if not needed.issubset(df.columns):
        raise ValueError(f"{filename} is missing {sorted(needed - set(df.columns))}")
    if df.duplicated(["ISO3", "Year"]).any():
        raise ValueError(f"Duplicate ISO3/Year in {filename}")
    records.append({
        "Dataset": label,
        "File": filename,
        "Main_Indicator": indicator,
        "Unit": unit,
        "Rows": len(df),
        "Countries": df["ISO3"].nunique(),
        "Start_Year": int(df["Year"].min()),
        "End_Year": int(df["Year"].max()),
        "Missing_Indicator": int(df[indicator].isna().sum()),
    })

summary = pd.DataFrame(records)
summary.to_csv(OUT / "data_sources_profile.csv", index=False)
master = pd.read_csv(DATA / "master_dataset.csv")
main = pd.read_csv(DATA / "main_analysis.csv")
assert len(master) == 2786 and len(main) == 2713, "Different data version - review before reporting"
missing_water = int(master["Water_AtLeastBasic_Pct"].isna().sum())
assert missing_water == 73

notes = [
    "# Data source and preprocessing profile",
    "",
    "This file is generated from the processed data in the project.",
    "The original UNICEF, WHO and JMP files are not included in the repository.",
    "", "## Dataset sizes", "",
    "| Dataset | Records | Countries | Year range | Missing main indicator |",
    "|---|---:|---:|---|---:|",
]
for rec in records:
    notes.append(f"| {rec['Dataset']} | {rec['Rows']} | {rec['Countries']} | {rec['Start_Year']}-{rec['End_Year']} | {rec['Missing_Indicator']} |")
notes += [
    "", "## Integration facts", "",
    "- Country and year keys: ISO3 and Year.",
    f"- Master: {len(master)} country-year rows.",
    f"- Basic water missing in master: {missing_water} rows (not replaced by zero).",
    f"- Main complete-case sample: {len(main)} rows.",

    "", "Note: This report is a profile of processed extracts, not a new raw-data import.",
]
(OUT / "data_source_profile.md").write_text("\n".join(notes) + "\n", encoding="utf-8")
print("=== DATA SOURCE PROFILE ===")
print(summary[["Dataset", "Rows", "Countries", "Missing_Indicator"]].to_string(index=False))
print(f"Basic water missing in master: {missing_water}")
print("SAVED: reports/team/data_sources_profile.csv")
print("SAVED: reports/team/data_source_profile.md")
