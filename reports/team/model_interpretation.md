\# Member 4 – Model Interpretation



\## PM2.5 Significance in Level and Log Specifications



The results show that PM2.5 is not statistically significant in the Level Fixed Effects model (coefficient = -0.1483, p-value = 0.2644). However, it is statistically significant in the Log Fixed Effects model (coefficient = 0.00706, p-value = 0.00210). The PM2.5 coefficient also remains statistically significant in the Log Sensitivity model (p-value = 0.00239) and the First Differences model (p-value = 0.00588).



The difference in statistical significance between the level and log specifications may be explained by the transformation of the dependent variable. The level model examines mortality in its original scale, whereas the log models examine mortality in logarithmic form. This transformation changes the model's functional form and can affect coefficient estimates, standard errors, and statistical significance.



The positive PM2.5 coefficients in the log models indicate a positive statistical association with under-five mortality in these specifications, while the level model does not provide statistically significant evidence of an association.



\## Why This Is Not Evidence of Causation



These models use observational data. Although country and year fixed effects are included in some specifications, other factors may still influence pollution levels and child mortality. Statistical significance does not establish that PM2.5 causes changes in under-five mortality. The findings should therefore be interpreted as statistical associations rather than causal effects.



\## Validation



I independently ran the model validation script on my computer. All eight coefficient checks passed, confirming that the re-estimated coefficients, p-values, R-squared values, and observation counts matched the saved reference results within the specified tolerances.



The validation output was saved to `reports/team/model\_validation\_results.csv`.

