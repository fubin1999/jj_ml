"""Compare the published all-features model with a forced Age + Gender variant.

Run from the repository root with the Python environment used for modeling.ipynb:
    python src/experiments/age_gender/run.py
"""

from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegressionCV
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    f1_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn import set_config


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results/experiments/age_gender"
PEPTIDES = ["A2MG", "APOB"]
DEMOGRAPHICS = ["Age", "Gender"]
set_config(transform_output="pandas")


def make_model(x_columns, add_demographics):
    # Keep the original six-feature selection unchanged. Demographics enter only
    # through a separate passthrough branch in the additional experiment.
    candidates = [c for c in x_columns if c not in PEPTIDES + DEMOGRAPHICS]
    original_candidates = [c for c in x_columns if c not in PEPTIDES]
    return Pipeline(
        [
            ("impute", SimpleImputer(strategy="mean")),
            ("scaler", StandardScaler()),
            (
                "fs",
                ColumnTransformer(
                    [
                        (
                            "kbest",
                            SelectKBest(f_classif, k=6),
                            candidates if add_demographics else original_candidates,
                        ),
                        ("peptides", "passthrough", PEPTIDES),
                    ]
                    + ([("demographics", "passthrough", DEMOGRAPHICS)] if add_demographics else [])
                ),
            ),
            ("logreg", LogisticRegressionCV(class_weight="balanced")),
        ]
    )


def metrics(y, pred, prob):
    return {
        "roc_auc": roc_auc_score(y, prob),
        "pr_auc": average_precision_score(y, prob),
        "accuracy": accuracy_score(y, pred),
        "balanced_accuracy": balanced_accuracy_score(y, pred),
        "f1": f1_score(y, pred, zero_division=0),
        "sensitivity": recall_score(y, pred, zero_division=0),
        "specificity": recall_score(y, pred, pos_label=0, zero_division=0),
    }


def main():
    train = pd.read_csv(ROOT / "results/data/train.csv", index_col=0)
    x_train = train.drop(columns="Endpoint")
    y_train = train["Endpoint"]
    tests = {
        "test1_single_center": pd.read_csv(ROOT / "results/data/test1.csv", index_col=0),
        "test2_multi_center": pd.read_csv(ROOT / "results/data/test2.csv", index_col=0),
    }
    for name, data in [("train", train), *tests.items()]:
        if data[DEMOGRAPHICS].isna().any().any():
            raise ValueError(f"{name}: Age or Gender is missing")
        if not set(data["Gender"].unique()).issubset({0, 1}):
            raise ValueError(f"{name}: Gender must be coded 0/1")

    predictions = []
    scores = []
    selections = []
    for label, add_demographics in [("Original all features", False), ("+ Age and Gender", True)]:
        model = make_model(x_train.columns, add_demographics)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")
            model.fit(x_train, y_train)

        selector = model.named_steps["fs"].named_transformers_["kbest"]
        candidate_columns = [
            c for c in x_train.columns if c not in PEPTIDES + (DEMOGRAPHICS if add_demographics else [])
        ]
        selections.extend({"model": label, "feature": c} for c in np.array(candidate_columns)[selector.get_support()])
        for cohort, data in tests.items():
            y = data["Endpoint"]
            x = data[x_train.columns]
            pred = model.predict(x)
            prob = model.predict_proba(x)[:, 1]
            predictions.extend(
                {
                    "cohort": cohort,
                    "sample_number": sample,
                    "model": label,
                    "true": truth,
                    "pred": prediction,
                    "prob": probability,
                }
                for sample, truth, prediction, probability in zip(y.index, y, pred, prob)
            )
            scores.append({"cohort": cohort, "model": label, "n": len(y), "events": int(y.sum()), **metrics(y, pred, prob)})

    predictions = pd.DataFrame(predictions)
    # The original notebook's persisted outputs are an independent parity check.
    for cohort, filename in [("test1_single_center", "result_test1.csv"), ("test2_multi_center", "result_test2.csv")]:
        saved = pd.read_csv(ROOT / "results/data" / filename)
        saved = saved[saved.feature_type == "All Features"].set_index("sample_number")
        current = predictions[(predictions.cohort == cohort) & (predictions.model == "Original all features")].set_index("sample_number")
        if not saved.index.equals(current.index):
            raise AssertionError(f"{cohort}: original prediction sample order differs")
        np.testing.assert_array_equal(current["pred"], saved["pred"])
        np.testing.assert_allclose(current["prob"], saved["prob"], rtol=1e-7, atol=1e-8)

    scores = pd.DataFrame(scores)
    metric_columns = list(metrics(np.array([0, 1]), np.array([0, 1]), np.array([0.0, 1.0])))
    baseline = scores[scores.model == "Original all features"].set_index("cohort")
    augmented = scores[scores.model == "+ Age and Gender"].set_index("cohort")
    delta = augmented[metric_columns] - baseline[metric_columns]
    delta.insert(0, "cohort", delta.index)
    delta = delta.reset_index(drop=True)

    OUT.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(OUT / "predictions.csv", index=False)
    scores.to_csv(OUT / "metrics.csv", index=False)
    delta.to_csv(OUT / "delta.csv", index=False)
    pd.DataFrame(selections).to_csv(OUT / "selected_clinical_features.csv", index=False)
    print(scores.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print("\nAugmented minus original:\n", delta.to_string(index=False, float_format=lambda x: f"{x:+.4f}"))


if __name__ == "__main__":
    main()
