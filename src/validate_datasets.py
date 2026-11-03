"""Validate all three processed datasets for the pinned 2010–2023 project release.

Run from the project root with:
    python src/validate_datasets.py

This checks data integrity; it does not certify the accuracy of source estimates.
"""
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "processed"

EXPECTED = {
    "master_dataset.csv": (2786, 199),
    "main_analysis.csv": (2713, 198),
    "secondary_analysis.csv": (1932, 139),
}

REQUIRED = [
    "ISO3", "Country", "Year", "Under5_Mortality_Rate", "PM25",
    "Water_AtLeastBasic_Pct", "Water_SafelyManaged_Pct",
]
KEYS = ["ISO3", "Year"]
WATER = ["Water_AtLeastBasic_Pct", "Water_SafelyManaged_Pct"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_file(filename, expected_rows, expected_countries):
    path = DATA_DIR / filename
    require(path.is_file(), f"Missing processed file: {path}")
    df = pd.read_csv(path)

    missing_cols = set(REQUIRED) - set(df.columns)
    require(not missing_cols, f"{filename}: missing columns {sorted(missing_cols)}")
    require(df["ISO3"].notna().all(), f"{filename}: missing ISO3 code")
    require(df["Country"].notna().all(), f"{filename}: missing country name")
    require(df["ISO3"].astype(str).str.fullmatch(r"[A-Z]{3}").all(),
            f"{filename}: invalid ISO3 code format")
    require(df["Country"].astype(str).str.strip().ne("").all(),
            f"{filename}: blank country name")
    require(not df.duplicated(KEYS).any(),
            f"{filename}: duplicate ISO3 + Year records")

    require(df["Year"].notna().all() and df["Year"].between(2010, 2023).all()
            and (df["Year"] % 1 == 0).all(),
            f"{filename}: invalid year")
    require(df["Under5_Mortality_Rate"].between(0, 1000).all(),
            f"{filename}: invalid or missing mortality")
    require(df["PM25"].ge(0).all(),
            f"{filename}: invalid or missing PM2.5")

    for column in WATER:
        require(df[column].dropna().between(0, 100).all(),
                f"{filename}: {column} outside 0–100%")

    both = df[WATER].notna().all(axis=1)
    consistent = (
        df.loc[both, "Water_SafelyManaged_Pct"]
        <= df.loc[both, "Water_AtLeastBasic_Pct"] + 1e-6
    )
    require(consistent.all(),
            f"{filename}: safely managed water exceeds at-least-basic coverage")

    if filename == "main_analysis.csv":
        require(df["Water_AtLeastBasic_Pct"].notna().all(),
                "Main dataset must have complete basic-water coverage")
    if filename == "secondary_analysis.csv":
        require(df[WATER].notna().all().all(),
                "Secondary dataset must have complete basic and safely managed water")

    require(len(df) == expected_rows, f"{filename}: expected {expected_rows} rows, got {len(df)}")
    require(df["ISO3"].nunique() == expected_countries,
            f"{filename}: expected {expected_countries} countries, got {df['ISO3'].nunique()}")
    print(f"{filename}: PASSED | {len(df):,} records | {df['ISO3'].nunique()} countries")
    return df


def check_derived_subset(master, derived, column, filename):
    expected = (master.dropna(subset=[column])
                .sort_values(KEYS).reset_index(drop=True))
    actual = derived.sort_values(KEYS).reset_index(drop=True)
    try:
        pd.testing.assert_frame_equal(
            actual[REQUIRED], expected[REQUIRED],
            check_dtype=False, check_exact=False, atol=1e-6, rtol=1e-8
        )
    except AssertionError as exc:
        raise ValueError(f"{filename}: does not match corresponding master records") from exc
    print(f"{filename}: matches master_dataset.csv")


def main():
    print("=== PROJECT DATA VALIDATION ===")
    datasets = {
        filename: validate_file(filename, *shape)
        for filename, shape in EXPECTED.items()
    }
    master = datasets["master_dataset.csv"]
    check_derived_subset(master, datasets["main_analysis.csv"],
                         "Water_AtLeastBasic_Pct", "main_analysis.csv")
    check_derived_subset(master, datasets["secondary_analysis.csv"],
                         "Water_SafelyManaged_Pct", "secondary_analysis.csv")
    print("\nALL DATASETS PASSED VALIDATION!")


if __name__ == "__main__":
    main()
