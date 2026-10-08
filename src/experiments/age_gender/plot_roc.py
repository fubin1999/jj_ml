"""Plot held-out ROC curves for the original and age/gender models."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import roc_auc_score, roc_curve


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "results/experiments/age_gender"
COHORTS = [
    ("test1_single_center", "Single-center test (n=72, events=16)"),
    ("test2_multi_center", "Multi-center test (n=102, events=17)"),
]
MODELS = [
    ("Original all features", "Original model", "#2463A6", "-"),
    ("+ Age and Gender", "+ Age and Gender", "#D47A30", "-"),
]


def main():
    predictions = pd.read_csv(HERE / "predictions.csv")
    metrics = pd.read_csv(HERE / "metrics.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.7), sharex=True, sharey=True)

    for ax, (cohort, title) in zip(axes, COHORTS):
        subset = predictions[predictions.cohort == cohort]
        for model, label, color, linestyle in MODELS:
            data = subset[subset.model == model]
            if data.sample_number.duplicated().any():
                raise ValueError(f"Duplicate sample in {cohort}, {model}")
            fpr, tpr, _ = roc_curve(data["true"], data["prob"])
            auc = roc_auc_score(data["true"], data["prob"])
            saved_auc = metrics.loc[(metrics.cohort == cohort) & (metrics.model == model), "roc_auc"]
            if len(saved_auc) != 1 or abs(auc - saved_auc.iloc[0]) > 1e-10:
                raise ValueError(f"AUC mismatch in {cohort}, {model}")
            ax.plot(fpr, tpr, color=color, linestyle=linestyle, linewidth=2.2, label=f"{label} (AUC {auc:.3f})")

        ax.plot([0, 1], [0, 1], color="#999999", linestyle="--", linewidth=1, label="Chance")
        ax.set(title=title, xlim=(0, 1), ylim=(0, 1))
        ax.set_aspect("equal", adjustable="box")
        ax.grid(color="#E6E6E6", linewidth=0.7)
        ax.legend(loc="lower right", frameon=True, fontsize=8.5)
        ax.set_xlabel("False positive rate (1 - specificity)")

    axes[0].set_ylabel("True positive rate (sensitivity)")
    fig.suptitle("ROC curves: adding age and gender", fontsize=14)
    fig.tight_layout()
    fig.savefig(HERE / "roc_comparison.pdf", bbox_inches="tight")
    fig.savefig(HERE / "roc_comparison.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
