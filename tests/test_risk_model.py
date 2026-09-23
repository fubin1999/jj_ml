"""Check the frozen calculator against the notebook's saved predictions."""

import csv
import unittest
from pathlib import Path

from risk_model import FEATURES, predict_probability


ROOT = Path(__file__).resolve().parents[1]


class RiskModelTest(unittest.TestCase):
    def test_saved_holdout_predictions(self):
        for cohort in ("test1", "test2"):
            with self.subTest(cohort=cohort):
                with (ROOT / "results" / "data" / f"result_{cohort}.csv").open() as file:
                    expected = {
                        row["sample_number"]: float(row["prob"])
                        for row in csv.DictReader(file)
                        if row["feature_type"] == "All Features"
                    }
                with (ROOT / "data" / f"{cohort}.csv").open() as file:
                    rows = list(csv.DictReader(file))
                self.assertEqual(set(expected), {row["Sample number"] for row in rows})
                for row in rows:
                    values = {
                        name: float(row[name]) if row[name] else None
                        for name in FEATURES
                    }
                    with self.subTest(sample=row["Sample number"]):
                        self.assertAlmostEqual(
                            predict_probability(values),
                            expected[row["Sample number"]],
                            delta=1e-12,
                        )

    def test_invalid_diabetes_code(self):
        values = {name: mean for name, (_, mean, _) in FEATURES.items()}
        values["Diabetes"] = 2
        with self.assertRaisesRegex(ValueError, "Diabetes"):
            predict_probability(values)


if __name__ == "__main__":
    unittest.main()
