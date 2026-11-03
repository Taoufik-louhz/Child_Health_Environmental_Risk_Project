
from pathlib import Path
import pandas as pd

# Project paths
BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"

# Load the original UNICEF Excel file
excel_files = list(
    RAW_DIR.glob("Under-five_Mortality_Rates*.xlsx")
)

if len(excel_files) != 1:
    raise FileNotFoundError(
        "Expected one UNICEF mortality Excel file in data/raw"
    )

unicef_raw = pd.read_excel(
    excel_files[0],
    sheet_name="U5MR Country estimates",
    header=14
)

# Keep only median estimates
unicef_median = unicef_raw[
    unicef_raw["Uncertainty.Bounds*"] == "Median"
].copy()

# Identify year columns
year_columns = [
    col for col in unicef_median.columns
    if str(col).split(".")[0].isdigit()
    and 1950 <= int(str(col).split(".")[0]) <= 2024
]

# Convert from wide to long format
unicef_clean = unicef_median.melt(
    id_vars=["ISO.Code", "Country.Name"],
    value_vars=year_columns,
    var_name="Year",
    value_name="Under5_Mortality_Rate"
)

# Standardize columns
unicef_clean = unicef_clean.rename(columns={
    "ISO.Code": "ISO3",
    "Country.Name": "Country"
})

unicef_clean["Year"] = (
    unicef_clean["Year"].astype(float).astype(int)
)

unicef_clean["Under5_Mortality_Rate"] = pd.to_numeric(
    unicef_clean["Under5_Mortality_Rate"],
    errors="coerce"
)

unicef_clean = unicef_clean.sort_values(
    ["ISO3", "Year"]
).reset_index(drop=True)

# Validate the result
assert len(unicef_clean) == 15000
assert unicef_clean["ISO3"].nunique() == 200
assert not unicef_clean.duplicated(
    ["ISO3", "Year"]
).any()

print("=== UNICEF PIPELINE ===")
print("Status: PASSED")
print("Records:", len(unicef_clean))
print("Countries:", unicef_clean["ISO3"].nunique())
print("Years:", unicef_clean["Year"].min(),
      "-", unicef_clean["Year"].max())
print("Missing values:",
      unicef_clean["Under5_Mortality_Rate"].isna().sum())

# STEP 41B: WHO PM2.5 Data Pipeline

# Load original WHO dataset
who_raw = pd.read_csv(RAW_DIR / "who_pm25.csv")

# Keep country-level total measurements
who_clean = who_raw[
    (who_raw["Dim1"] == "Total") &
    (who_raw["Location type"] == "Country")
].copy()

# Select required columns
who_clean = who_clean[
    [
        "SpatialDimValueCode",
        "Location",
        "Period",
        "FactValueNumeric"
    ]
]

# Standardize column names
who_clean = who_clean.rename(columns={
    "SpatialDimValueCode": "ISO3",
    "Location": "Country",
    "Period": "Year",
    "FactValueNumeric": "PM25"
})

# Convert data types
who_clean["Year"] = who_clean["Year"].astype(int)

who_clean["PM25"] = pd.to_numeric(
    who_clean["PM25"],
    errors="coerce"
)

# Sort by country and year
who_clean = who_clean.sort_values(
    ["ISO3", "Year"]
).reset_index(drop=True)

# Validate WHO data
assert len(who_clean) == 3178
assert who_clean["ISO3"].nunique() == 227
assert who_clean["PM25"].notna().all()
assert not who_clean.duplicated(
    ["ISO3", "Year"]
).any()

print("\n=== WHO PM2.5 PIPELINE ===")
print("Status: PASSED")
print("Records:", len(who_clean))
print("Countries:", who_clean["ISO3"].nunique())
print(
    "Years:",
    who_clean["Year"].min(),
    "-",
    who_clean["Year"].max()
)
print("Missing PM2.5:", who_clean["PM25"].isna().sum())


# STEP 41C: JMP Drinking Water Pipeline

# Load original JMP dataset
jmp_raw = pd.read_csv(
    RAW_DIR / "jmp_drinking_water.csv"
)

# Convert values to numeric
jmp_raw["value"] = pd.to_numeric(
    jmp_raw["value"],
    errors="coerce"
)

# Convert service levels into separate columns
water_wide = jmp_raw.pivot(
    index=["country", "year"],
    columns="service_level",
    values="value"
).reset_index()

# Calculate At least basic water coverage
water_wide["Water_AtLeastBasic_Pct"] = (
    water_wide["At least basic"].combine_first(
        water_wide["Basic service"]
        + water_wide["Safely managed service"]
    )
)

# Keep safely managed water coverage
water_wide["Water_SafelyManaged_Pct"] = (
    water_wide["Safely managed service"]
)

# Standardize columns
water_clean = water_wide.rename(columns={
    "country": "ISO3",
    "year": "Year"
})

water_clean = water_clean[
    [
        "ISO3",
        "Year",
        "Water_AtLeastBasic_Pct",
        "Water_SafelyManaged_Pct"
    ]
].copy()

water_clean["Year"] = (
    water_clean["Year"].astype(int)
)

# Keep records with available basic-water data
water_clean = water_clean.dropna(
    subset=["Water_AtLeastBasic_Pct"]
).copy()

water_clean["Water_AtLeastBasic_Pct"] = (
    water_clean["Water_AtLeastBasic_Pct"].round(6)
)

water_clean = water_clean.sort_values(
    ["ISO3", "Year"]
).reset_index(drop=True)

# Validate JMP data
assert len(water_clean) == 3157
assert water_clean["ISO3"].nunique() == 231

assert not water_clean.duplicated(
    ["ISO3", "Year"]
).any()

assert water_clean["Water_AtLeastBasic_Pct"].between(
    0, 100
).all()

assert water_clean["Water_SafelyManaged_Pct"].dropna().between(
    0, 100
).all()

print("\n=== JMP DRINKING WATER PIPELINE ===")
print("Status: PASSED")
print("Records:", len(water_clean))
print("Countries:", water_clean["ISO3"].nunique())

print(
    "Years:",
    water_clean["Year"].min(),
    "-",
    water_clean["Year"].max()
)

print(
    "Missing Safely Managed:",
    water_clean["Water_SafelyManaged_Pct"].isna().sum()
)


# STEP 41D: Automated Data Merge and Export

from pathlib import Path
import pandas as pd

PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# 1. Keep UNICEF records from 2010 to 2023
unicef_period = unicef_clean[
    unicef_clean["Year"].between(2010, 2023)
].copy()

# 2. Match UNICEF and WHO
matched = unicef_period.merge(
    who_clean[["ISO3", "Year", "PM25"]],
    on=["ISO3", "Year"],
    how="inner",
    validate="one_to_one"
)

# 3. Add drinking water indicators
master = matched.merge(
    water_clean[
        [
            "ISO3",
            "Year",
            "Water_AtLeastBasic_Pct",
            "Water_SafelyManaged_Pct"
        ]
    ],
    on=["ISO3", "Year"],
    how="left",
    validate="one_to_one"
)

# 4. Prepare analysis datasets
main = master.dropna(
    subset=["Water_AtLeastBasic_Pct"]
).copy()

secondary = master.dropna(
    subset=["Water_SafelyManaged_Pct"]
).copy()

datasets = {
    "master_dataset.csv": (master, 2786, 199),
    "main_analysis.csv": (main, 2713, 198),
    "secondary_analysis.csv": (secondary, 1932, 139)
}

print("\n=== AUTOMATED MERGE AND EXPORT ===")

for filename, (dataframe, expected_rows, expected_countries) in datasets.items():

    output = dataframe.sort_values(
        ["ISO3", "Year"]
    ).reset_index(drop=True)

    # Validate before saving
    assert len(output) == expected_rows
    assert output["ISO3"].nunique() == expected_countries

    assert not output.duplicated(
        ["ISO3", "Year"]
    ).any()

    # Compare with the previous saved version
    file_path = PROCESSED_DIR / filename

    if file_path.exists():
        previous = pd.read_csv(file_path).sort_values(
            ["ISO3", "Year"]
        ).reset_index(drop=True)

        pd.testing.assert_frame_equal(
            output,
            previous,
            check_dtype=False,
            check_exact=False,
            rtol=1e-8,
            atol=1e-6
        )

        print(f"{filename}: matches previous results")

    # Export validated data
    output.to_csv(file_path, index=False)

    print(f"{filename}: SAVED")
    print("Records:", len(output))
    print("Countries:", output["ISO3"].nunique())
    print("-" * 35)

print("\nAUTOMATED DATA PIPELINE COMPLETED!")
