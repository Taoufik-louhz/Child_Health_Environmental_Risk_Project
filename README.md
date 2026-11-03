# Child Health & Environmental Risk Factors

**Data Analysis Group Project**  
**University:** Széchenyi István University  
**Programme:** MSc Computer Science Engineering  
**Course:** Data Analysis

## Project overview

This project explores how **ambient PM2.5 air pollution** and **access to drinking water** are associated with **under-five mortality** at the country-year level. It combines international datasets from UNICEF, the World Health Organization (WHO), and the WHO/UNICEF Joint Monitoring Programme (JMP).

The analysis covers **2010–2023**. It is an **observational study**: statistical associations must not be interpreted as causal effects.

### Research questions

1. Is PM2.5 air pollution associated with under-five mortality?
2. Is access to basic drinking water associated with lower under-five mortality?
3. How do these relationships change when accounting for country and year differences and using alternative statistical specifications?

## Data sources

| Source | Original file in `data/raw/` | Indicator | Units |
|---|---|---|---|
| UNICEF / UN IGME | `Under-five_Mortality_Rates_2025-1.xlsx` | Under-five mortality, median estimate | Deaths per 1,000 live births |
| WHO | `who_pm25.csv` | Annual country-level PM2.5 concentration (`Dim1 = Total`, `Location type = Country`) | µg/m³ |
| WHO/UNICEF JMP | `jmp_drinking_water.csv` | At least basic and safely managed drinking water services | Percentage of population |

**Official reference pages:**

- [UNICEF under-five mortality data](https://data.unicef.org/resources/dataset/under-five-mortality-data/)
- [WHO PM2.5 indicator documentation](https://www.who.int/data/gho/data/indicators/indicator-details/GHO/concentrations-of-fine-particulate-matter-%28pm2-5%29)
- [WHO/UNICEF JMP data documentation](https://washdata.org/data/api)

**Data-version note:** The analyses use the supplied **2025 UNICEF Excel extract**, not whichever release is most recent on the reference page. The exact download dates and export versions of the local WHO and JMP CSV files are not established. Newer downloads may produce different results.

## Data preparation

The preparation pipeline:

1. Extracts the **median** under-five mortality estimates from the UNICEF workbook and reshapes years into rows.
2. Selects WHO country-level total PM2.5 measurements.
3. Pivots JMP water service levels and uses the reported *At least basic* value when available; otherwise, it adds *Basic service* and *Safely managed service*.
4. Standardizes country ISO3 codes and years, then joins records by **`ISO3` and `Year`**.
5. Preserves missing water estimates rather than replacing them with zero.
6. Produces the master, main-analysis, and secondary-analysis datasets.

| Dataset | File | Country-year records | Countries / territories |
|---|---|---:|---:|
| Master | `data/processed/master_dataset.csv` | 2,786 | 199 |
| Main (complete basic-water observations) | `data/processed/main_analysis.csv` | 2,713 | 198 |
| Secondary (safely managed water available) | `data/processed/secondary_analysis.csv` | 1,932 | 139 |

The two analysis samples are not identical. Comparisons of basic versus safely managed water are estimated on the **same 1,932 observations**.

## Project structure

```text
Child_Health_Environmental_Risk_Project/
├── data/
│   ├── raw/
│   │   ├── Under-five_Mortality_Rates_2025-1.xlsx
│   │   ├── who_pm25.csv
│   │   └── jmp_drinking_water.csv
│   └── processed/
│       ├── unicef_under5_mortality.csv
│       ├── who_pm25.csv
│       ├── master_dataset.csv
│       ├── main_analysis.csv
│       └── secondary_analysis.csv
├── src/
│   ├── data_pipeline.py
│   └── validate_datasets.py
├── reports/
│   ├── figures/
│   └── model_comparison.csv
├── Group_Child_Health_Analysis.ipynb
├── dashboard.py
├── requirements.txt
└── README.md
```

This layout shows the **expected project files**, including generated outputs. Keep filenames and paths unchanged unless the corresponding code is updated.

## Installation and execution

Run the commands below **from the project root** (the folder containing `dashboard.py`). Python and `pip` are required.

### 1. Install dependencies

```bash
python -m pip install -r requirements.txt
```

The `requirements.txt` file pins the versions reported by the working project environment. `ipython` is included without an exact version pin.

### 2. Generate the processed data

Place all three original source files in `data/raw/`, then run:

```bash
python src/data_pipeline.py
```

The pipeline checks expected dataset sizes and, if processed CSV files already exist, compares the regenerated output with them before writing. These counts are **version-specific**; changing source releases may require revisiting the validation rules.

### 3. Validate the datasets

```bash
python src/validate_datasets.py
```

The validator checks columns, country-year uniqueness, expected ranges, water-indicator consistency, and whether the analysis datasets agree with the master data.

### 4. Open the analysis notebook

For a new environment, install a notebook interface if needed:

```bash
python -m pip install jupyterlab
jupyter lab
```

Open `Group_Child_Health_Analysis.ipynb` and run all cells from the beginning, with the working directory set to the project root. The notebook contains exploratory data analysis, correlation calculations, fixed-effects regressions, sensitivity checks, first-difference modelling, and visualizations.

### 5. Launch the Streamlit dashboard

Ensure these files exist before starting it:

- `data/processed/main_analysis.csv`
- `reports/model_comparison.csv`

Then run:

```bash
python -m streamlit run dashboard.py
```

The app provides country and year filters, descriptive indicators, trends, scatter plots, Pearson and Spearman correlations, a precomputed regression comparison, country comparisons, and CSV downloads.

**Important:** Dashboard correlations respond to the selected filters, but the regression results in `reports/model_comparison.csv` are **precomputed from the full study** and do **not** change with country/year filters. The data pipeline does **not** regenerate this model-comparison CSV; it must be kept consistent with the notebook when model specifications are updated.

## Analytical methods

- **Exploratory analysis:** descriptive statistics, distributions, boxplots, and IQR-based outlier flags.
- **Correlation:** pooled Pearson and Spearman coefficients, plus within-country de-meaned correlations.
- **Two-way fixed effects:** mortality levels with country and year effects.
- **Log-linear fixed effects:** log mortality with country and year effects.
- **Sensitivity analysis:** repeats the log model after excluding six observations above 200 deaths per 1,000 live births; the original data remain unchanged.
- **Water-indicator comparison:** separate regressions for basic and safely managed drinking water on the same sample.
- **First differences:** annual changes in log mortality, PM2.5, and basic-water access, including year effects.

Regression standard errors are **clustered by country**.

## Main findings

The main study includes **2,713 country-year observations from 198 countries and territories**.

- **Basic drinking water** has a negative and statistically significant association with under-five mortality across the main regression specifications.
- **PM2.5** is **not statistically significant in the level fixed-effects model** (coefficient ≈ −0.1483; p ≈ 0.2644), but is **positive and statistically significant** in the log fixed-effects model (≈ +0.71% per additional µg/m³; p ≈ 0.0021) and the first-difference model (≈ +0.17% for an additional 1 µg/m³ annual increase; p ≈ 0.0059).
- In the log fixed-effects model, a one-percentage-point increase in basic-water coverage is associated with approximately **1.09% lower** mortality (p < 0.0001).
- Excluding six extreme mortality observations yields similar log-model associations, but this one sensitivity test does not establish general model robustness.
- The first-difference model has **R² ≈ 0.0163**; it explains only a small share of annual log-mortality variation (including the contribution of year effects).

Outlier screening identified **136 mortality**, **90 PM2.5**, and **181 basic-water** flagged country-year records under the 1.5×IQR rule. The six mortality observations above 200 matched the values in the original UNICEF Excel extract. Source agreement does not independently validate the demographic estimates.

## Interpretation and limitations

This is a cross-country observational analysis. Country-year records are repeated observations, not independent individuals. Unmeasured factors such as income, healthcare access, education, and conflict may affect the estimated relationships. Missing water observations limit sample coverage. PM2.5 conclusions are sensitive to model specification, and coefficients or R² values across different outcome scales should not be compared directly.

The project **does not establish causation** or support individual-level risk claims.

## Updating or extending the project

If replacing source files with newer releases, document the version/date, rerun the pipeline and validation, rerun the notebook, and update `reports/model_comparison.csv` before displaying regression results in Streamlit. Verify all reported figures and sample sizes, since the current pipeline includes checks for the original source snapshot.
