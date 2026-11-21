# Data source and preprocessing profile

This file is generated from the processed data in the project.
The original UNICEF, WHO and JMP files are not included in the repository.

## Dataset sizes

| Dataset | Records | Countries | Year range | Missing main indicator |
|---|---:|---:|---|---:|
| UNICEF under-five mortality | 15000 | 200 | 1950-2024 | 1904 |
| WHO PM2.5 | 3178 | 227 | 2010-2023 | 0 |
| Integrated master | 2786 | 199 | 2010-2023 | 0 |
| Main analysis | 2713 | 198 | 2010-2023 | 0 |
| Safely managed sample | 1932 | 139 | 2010-2023 | 0 |

## Integration facts

- Country and year keys: ISO3 and Year.
- Master: 2786 country-year rows.
- Basic water missing in master: 73 rows (not replaced by zero).
- Main complete-case sample: 2713 rows.

## Human review (complete this yourself)

- Which indicator definition did you verify in the README?
- Which step of the preprocessing script did you check?
- Did you find an improvement or possible limitation?
- Record the official source page that you opened and the date.

Note: This report is a profile of processed extracts, not a new raw-data import.
