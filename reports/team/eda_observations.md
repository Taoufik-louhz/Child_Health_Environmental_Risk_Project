# Exploratory Data Analysis – Observations
**Author:** Esraa Naanoush (Exploratory Data Analysis)
**Date:** 22 November 2026
**Branch:** feat/member3-eda

## What I ran
- Environment: GitHub Codespaces (browser), Python 3.14
- `pip install -r requirements.txt`
- `python src/eda_comparison.py`

Output: Records: 2713 | Countries: 198 | Annual summary rows: 14.
Three files were saved: `eda_annual_summary.csv`, `eda_mortality_trend.png`,
`eda_pm25_country_comparison.png`. This matches the expected output in the guide.

## What I checked
- Both figures have a title, labelled axes and units
  (deaths per 1,000 live births; PM2.5 in micrograms/m3), and cover 2010–2023.
- The mortality chart states that it shows an unweighted country-year mean.
- **Independent check:** the `Countries` column in the annual summary adds up to
  2,713, which equals the total number of records. Each country-year is counted once.
- The number of countries per year is not constant: 196–198 in 2010–2017,
  then it falls to 188 in 2022–2023.

## Observations
1. **Child mortality fell steadily.** The unweighted mean under-five mortality fell
   from 35.9 (2010) to 24.9 (2023) deaths per 1,000 live births, about a 31% drop.
   It went down in every year except 2022 (26.4 in 2021 → 27.2 in 2022).
2. **Interpreting the 2022 rise with care.** In 2022 the sample has 188 countries,
   compared with 198 in 2016. Because the mean is unweighted and the set of
   countries changes, part of the year-to-year movement may come from which
   countries are included, not only from real changes in mortality.
3. **Environmental indicators also improved on average.** Mean PM2.5 fell from
   22.6 to 19.3 µg/m³, and mean "at least basic" water access rose every year,
   from 85.3% to 89.9%.
4. 4. **Morocco vs Hungary (PM2.5, values read from the chart, ±0.1).**
   Hungary started higher (19.0 µg/m³ in 2010, peaking at 20.3 in 2011) and fell
   to 11.2 by 2023, about a 41% decrease. The decline was not smooth: PM2.5 rose
   again to 17.0 in 2018 before dropping sharply to 14.1 in 2019. Morocco stayed
   in a narrower range (12.7–15.5) and was slightly higher in 2023 (14.2) than in
   2010 (13.7), with its highest value in 2022 (15.5). The lines cross between 2019
   and 2020: before that Hungary was higher, and from 2020 onwards Morocco was higher.

## Limitations
- These are descriptive, unweighted averages, not population-weighted global figures.
- Trends happening at the same time (lower PM2.5, better water, lower mortality)
  show an association, not causation.
