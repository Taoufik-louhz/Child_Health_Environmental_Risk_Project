
# STEP 33: Interactive Dashboard with Filters

import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Child Health & Environmental Risk",
    page_icon="🌍",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent

@st.cache_data
def load_data():
    file_path = BASE_DIR / "data" / "processed" / "main_analysis.csv"
    return pd.read_csv(file_path)

df = load_data()

# Dashboard Header
st.title("🌍 Child Health & Environmental Risk Factors")

st.markdown(
    "Exploring the relationships between child mortality, "
    "air pollution, and drinking water access."
)

st.caption(
    "Sources: UNICEF, WHO, WHO/UNICEF JMP | "
    "Period: 2010–2023 | Observational analysis"
)

# SIDEBAR FILTERS
st.sidebar.header("🔎 Data Filters")

countries = ["All countries"] + sorted(
    df["Country"].dropna().unique().tolist()
)

selected_country = st.sidebar.selectbox(
    "Select Country",
    countries
)

min_year = int(df["Year"].min())
max_year = int(df["Year"].max())

selected_years = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1
)

# Apply filters
filtered_df = df[
    df["Year"].between(
        selected_years[0],
        selected_years[1]
    )
].copy()

if selected_country != "All countries":
    filtered_df = filtered_df[
        filtered_df["Country"] == selected_country
    ]

# MAIN DASHBOARD
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Country-Year Records",
        f"{len(filtered_df):,}"
    )

with col2:
    st.metric(
        "Countries",
        filtered_df["ISO3"].nunique()
    )

with col3:
    st.metric(
        "Years",
        filtered_df["Year"].nunique()
    )

st.divider()


# STEP 34: Interactive Health and Environment KPIs

st.subheader("📊 Health & Environmental Indicators")

if not filtered_df.empty:

    kpi1, kpi2, kpi3 = st.columns(3)

    with kpi1:
        avg_mortality = filtered_df[
            "Under5_Mortality_Rate"
        ].mean()

        st.metric(
            "Avg. Child Mortality",
            f"{avg_mortality:.2f}",
            help="Deaths per 1,000 live births"
        )

    with kpi2:
        avg_pm25 = filtered_df["PM25"].mean()

        st.metric(
            "Avg. PM2.5",
            f"{avg_pm25:.2f} µg/m³"
        )

    with kpi3:
        avg_water = filtered_df[
            "Water_AtLeastBasic_Pct"
        ].mean()

        st.metric(
            "Avg. Basic Water Access",
            f"{avg_water:.2f}%"
        )

    st.caption(
        "Averages are calculated across the selected "
        "country-year records, without population weighting."
    )

st.divider()

# STEP 35: Interactive Trend Charts

import plotly.express as px

st.subheader("📈 Trends Over Time")

if not filtered_df.empty:

    # Calculate yearly averages for selected records
    yearly_trends = filtered_df.groupby(
        "Year", as_index=False
    ).agg(
        Child_Mortality=(
            "Under5_Mortality_Rate", "mean"
        ),
        PM25_Avg=("PM25", "mean"),
        Basic_Water=(
            "Water_AtLeastBasic_Pct", "mean"
        )
    )

    chart_settings = [
        (
            "Child_Mortality",
            "Child Mortality Over Time",
            "Deaths per 1,000 live births"
        ),
        (
            "PM25_Avg",
            "Air Pollution Over Time",
            "PM2.5 (µg/m³)"
        ),
        (
            "Basic_Water",
            "Drinking Water Access Over Time",
            "Population coverage (%)"
        )
    ]

    for column, title, ylabel in chart_settings:

        fig = px.line(
            yearly_trends,
            x="Year",
            y=column,
            markers=True,
            title=title,
            labels={
                "Year": "Year",
                column: ylabel
            }
        )

        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=7)
        )

        fig.update_layout(
            height=340,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        fig.update_xaxes(dtick=1)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.caption(
        "For multiple countries, each point is the "
        "unweighted average of available country "
        "records in that year. Country coverage "
        "may change over time."
    )

st.divider()

# STEP 36: Interactive Correlation Analysis

st.subheader("🔎 Environmental Correlation Analysis")

st.caption(
    "Correlations are recalculated using only the "
    "selected countries and years. "
    "They describe associations, not causation."
)

if not filtered_df.empty:

    factors = [
        (
            "PM25",
            "PM2.5 Air Pollution",
            "PM2.5 concentration (µg/m³)"
        ),
        (
            "Water_AtLeastBasic_Pct",
            "Basic Drinking Water",
            "Water access (%)"
        )
    ]

    correlation_rows = []

    chart_columns = st.columns(2)

    for i, (factor, title, xlabel) in enumerate(factors):

        valid = filtered_df[
            ["Country", "Year",
             factor, "Under5_Mortality_Rate"]
        ].dropna()

        enough_data = (
            len(valid) >= 3
            and valid[factor].nunique() > 1
            and valid["Under5_Mortality_Rate"].nunique() > 1
        )

        with chart_columns[i]:

            st.markdown(f"**{title} vs Child Mortality**")

            if enough_data:

                pearson = valid[factor].corr(
                    valid["Under5_Mortality_Rate"],
                    method="pearson"
                )

                spearman = valid[factor].corr(
                    valid["Under5_Mortality_Rate"],
                    method="spearman"
                )

                fig = px.scatter(
                    valid,
                    x=factor,
                    y="Under5_Mortality_Rate",
                    hover_data=["Country", "Year"],
                    labels={
                        factor: xlabel,
                        "Under5_Mortality_Rate":
                        "Deaths per 1,000 live births"
                    }
                )

                fig.update_traces(
                    marker=dict(size=8, opacity=0.55)
                )

                fig.update_layout(
                    height=360,
                    margin=dict(
                        l=10, r=10, t=20, b=10
                    )
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                st.write(f"Pearson: **{pearson:.3f}**")
                st.write(f"Spearman: **{spearman:.3f}**")

                correlation_rows.append({
                    "Factor": title,
                    "Records": len(valid),
                    "Pearson": round(pearson, 3),
                    "Spearman": round(spearman, 3)
                })

            else:
                st.info(
                    "Not enough variation or observations "
                    "to calculate correlations."
                )

    if correlation_rows:

        st.markdown("#### Correlation Summary")

        st.dataframe(
            pd.DataFrame(correlation_rows),
            use_container_width=True,
            hide_index=True
        )

    if filtered_df["ISO3"].nunique() == 1:
        st.warning(
            "Single-country correlations are exploratory. "
            "A short time series may show strong correlations "
            "simply because variables trend over time."
        )
    else:
        st.info(
            "Pooled correlations combine multiple countries "
            "and years. Country differences and time trends "
            "may influence these associations."
        )


# STEP 37: Statistical Model Comparison

st.divider()

st.subheader("📊 Statistical Model Comparison")

st.caption(
    "Precomputed regression results from the full study. "
    "These results are NOT recalculated by the "
    "country or year filters."
)

# Load saved regression results
@st.cache_data
def load_model_results():
    file_path = (
        BASE_DIR / "reports" / "model_comparison.csv"
    )
    return pd.read_csv(file_path)

model_results = load_model_results()

# Model selection
model_names = model_results["Model"].unique().tolist()

selected_models = st.multiselect(
    "Select statistical models",
    options=model_names,
    default=model_names
)

selected_results = model_results[
    model_results["Model"].isin(selected_models)
].copy()

if not selected_results.empty:

    # Prepare a readable results table
    display_results = selected_results[
        [
            "Model",
            "Factor",
            "Observations",
            "Coefficient",
            "Pct_Change",
            "P_Value",
            "R_Squared"
        ]
    ].copy()

    display_results["Coefficient"] = (
        display_results["Coefficient"].round(4)
    )

    display_results["Pct_Change"] = (
        display_results["Pct_Change"].apply(
            lambda x: (
                f"{x:+.2f}%"
                if pd.notna(x)
                else "—"
            )
        )
    )

    display_results["P_Value"] = (
        display_results["P_Value"].apply(
            lambda x: f"{x:.4g}"
        )
    )

    display_results["R_Squared"] = (
        display_results["R_Squared"].round(4)
    )

    st.dataframe(
        display_results,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("Select at least one model.")

# Methodological notes
with st.expander("How to interpret these models"):

    st.markdown("""
    **Level Fixed Effects**
    - Outcome: mortality rate per 1,000 live births.
    - Coefficients represent absolute rate differences.

    **Log Fixed Effects**
    - Outcome: natural log of the mortality rate.
    - Percentage changes describe estimated
      relative differences in mortality.

    **Log Sensitivity**
    - Same log model, temporarily excluding
      six records with mortality rates above 200.

    **First Differences**
    - Uses consecutive annual changes
      within countries.
    - Includes year effects.

    All models are observational and include
    country-clustered standard errors.

    Results do not establish causation.
    R-squared values should not be compared
    directly across different outcome scales.
    """)

st.warning(
    "Important: PM2.5 was not statistically "
    "significant in the level fixed-effects model, "
    "but was significant in the log and "
    "first-difference models. "
    "Results depend on model specification."
)

st.divider()


# STEP 38: Interactive Country Comparison

st.subheader("🌍 Country Comparison")

st.caption(
    "Compare environmental and child health trends "
    "across countries. This section uses the selected "
    "year range, independently of the main country filter."
)

# List available countries
available_countries = sorted(
    df["Country"].dropna().unique().tolist()
)

# Default comparison
default_countries = [
    country for country in ["Morocco", "Hungary"]
    if country in available_countries
]

selected_countries = st.multiselect(
    "Select countries to compare",
    options=available_countries,
    default=default_countries,
    max_selections=5
)

if selected_countries:

    comparison_df = df[
        df["Country"].isin(selected_countries)
        & df["Year"].between(
            selected_years[0],
            selected_years[1]
        )
    ].copy()

    if not comparison_df.empty:

        # Summary table
        country_summary = comparison_df.groupby(
            "Country", as_index=False
        ).agg(
            Records=("Year", "count"),
            Avg_Mortality=("Under5_Mortality_Rate", "mean"),
            Avg_PM25=("PM25", "mean"),
            Avg_Water=("Water_AtLeastBasic_Pct", "mean")
        )

        st.markdown("#### Country Overview")

        st.dataframe(
            country_summary.round(2),
            use_container_width=True,
            hide_index=True
        )

        # Interactive comparison charts
        comparison_charts = [
            (
                "Under5_Mortality_Rate",
                "Child Mortality Comparison",
                "Deaths per 1,000 live births"
            ),
            (
                "PM25",
                "PM2.5 Air Pollution Comparison",
                "PM2.5 concentration (µg/m³)"
            ),
            (
                "Water_AtLeastBasic_Pct",
                "Drinking Water Access Comparison",
                "Population coverage (%)"
            )
        ]

        for column, title, ylabel in comparison_charts:

            fig = px.line(
                comparison_df,
                x="Year",
                y=column,
                color="Country",
                markers=True,
                title=title,
                labels={
                    "Year": "Year",
                    column: ylabel
                }
            )

            fig.update_traces(
                line=dict(width=3),
                marker=dict(size=7)
            )

            fig.update_layout(
                height=380,
                margin=dict(
                    l=20, r=20, t=60, b=20
                ),
                legend_title_text="Country"
            )

            fig.update_xaxes(dtick=1)

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.caption(
            "Country averages are unweighted across "
            "available years. Comparisons are descriptive "
            "and do not establish causation."
        )

    else:
        st.warning(
            "No records available for the selected "
            "countries and years."
        )

else:
    st.info("Select at least one country to compare.")

st.divider()

# STEP 39: Export and Download Data

st.subheader("📥 Download Data")

st.caption(
    "Download the selected data as CSV files. "
    "The original datasets remain unchanged."
)

download_col1, download_col2 = st.columns(2)

# 1. Export filtered main dashboard data
with download_col1:

    st.markdown("**Filtered Dataset**")

    st.write(
        f"{len(filtered_df):,} country-year records"
    )

    filtered_export = filtered_df.sort_values(
        ["Country", "Year"]
    )

    st.download_button(
        label="⬇️ Download Filtered Dataset",
        data=filtered_export.to_csv(
            index=False
        ).encode("utf-8-sig"),
        file_name="filtered_child_health_data.csv",
        mime="text/csv",
        disabled=filtered_export.empty,
        use_container_width=True
    )

# 2. Export country comparison data
with download_col2:

    st.markdown("**Country Comparison**")

    comparison_export = df[
        df["Country"].isin(selected_countries)
        & df["Year"].between(
            selected_years[0],
            selected_years[1]
        )
    ].copy()

    comparison_export = comparison_export.sort_values(
        ["Country", "Year"]
    )

    st.write(
        f"{len(comparison_export):,} country-year records"
    )

    st.download_button(
        label="⬇️ Download Country Comparison",
        data=comparison_export.to_csv(
            index=False
        ).encode("utf-8-sig"),
        file_name="country_comparison.csv",
        mime="text/csv",
        disabled=comparison_export.empty,
        use_container_width=True
    )

st.divider()

st.subheader("Dataset Overview")

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
else:
    st.dataframe(
        filtered_df.head(20),
        use_container_width=True,
        hide_index=True
    )

st.info(
    "This dashboard explores statistical associations. "
    "The results do not establish causation."
)
