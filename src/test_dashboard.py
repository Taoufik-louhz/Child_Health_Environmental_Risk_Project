"""Member 5: automated tests for the data logic used by the Streamlit dashboard.

Run from the project root: python -m unittest discover -s tests -p "test_dashboard.py" -v
These are data-logic tests; also check the real Streamlit interface manually.
"""
from pathlib import Path
import unittest
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "main_analysis.csv"
MODELS = ROOT / "reports" / "model_comparison.csv"

class DashboardDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = pd.read_csv(DATA)
        cls.models = pd.read_csv(MODELS)

    def test_main_data_size(self):
        self.assertEqual(len(self.df), 2713)
        self.assertEqual(self.df["ISO3"].nunique(), 198)

    def test_country_and_year_filter(self):
        rows = self.df[self.df["Country"].eq("Morocco") &
                       self.df["Year"].between(2018, 2023)]
        self.assertEqual(len(rows), 6)
        self.assertEqual(set(rows["Year"]), set(range(2018, 2024)))

    def test_single_year_correlations_unavailable(self):
        one = self.df[self.df["Country"].eq("Morocco") & self.df["Year"].eq(2023)]
        self.assertEqual(len(one), 1)
        self.assertLess(len(one), 3)  # Dashboard needs >=3 records + variation.

    def test_country_comparison_independent_of_main_country(self):
        compared = self.df[self.df["Country"].isin(["Morocco", "Hungary"]) &
                           self.df["Year"].between(2018, 2023)]
        self.assertEqual(len(compared), 12)
        self.assertEqual(compared["Country"].nunique(), 2)

    def test_full_sample_correlation_signs(self):
        pm = self.df["PM25"].corr(self.df["Under5_Mortality_Rate"])
        water = self.df["Water_AtLeastBasic_Pct"].corr(self.df["Under5_Mortality_Rate"])
        self.assertGreater(pm, 0.3)
        self.assertLess(water, -0.75)

    def test_saved_model_table(self):
        self.assertEqual(len(self.models), 8)
        fd = self.models[self.models["Model"].eq("First Differences")]
        self.assertEqual(len(fd), 2)
        self.assertTrue(fd["Observations"].eq(2515).all())
        self.assertAlmostEqual(float(fd.iloc[0]["R_Squared"]), 0.0163, places=3)

    def test_dashboard_file_exists_and_parses(self):
        import ast
        src = (ROOT / "dashboard.py").read_text(encoding="utf-8")
        ast.parse(src)
        self.assertIn("load_model_results", src)
        self.assertIn("download_button", src)

if __name__ == "__main__":
    unittest.main(verbosity=2)
