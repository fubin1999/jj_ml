# GlycaPep-PD CVD Risk Calculator

Streamlit interface for the **All Features** logistic regression model in
`notebook/modeling.ipynb`. It takes the six selected clinical indicators and
two glycated peptide biomarkers as raw measurements and displays the model's
predicted probability for `Endpoint = 1`.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

All eight fields are required in the interface. Use the same measurement scale
and definitions as `data/train.csv`; `Diabetes` is coded No = 0, Yes = 1.
The frozen model coefficients and training means are in `risk_model.py`.
The original modeling pipeline's mean imputation remains available in
`predict_probability()` for programmatic callers passing `None`.

## Input units

| Input | Unit shown in the app | Source status |
|---|---|---|
| T Kt/v | Unitless | Ratio |
| Diabetes | Yes / No | Original workbook defines 1 / 0 |
| cTnT | ng/mL | Provisional; inferred from the training values |
| GA | % | Provisional; inferred from the training values |
| ALB | g/L | Provisional; inferred from the training values |
| P | mmol/L | Provisional; inferred from the training values |
| A2MG, APOB | pg/µL | Supplied for this project; absent from the source workbooks |

The clinical units are consistent with common laboratory reporting conventions,
but the source workbooks do not record them. Confirm units against the original
laboratory reports before using new measurements. A2MG and APOB are peptide
assay outputs (peptides 156 and 157 in the workbook dictionary), not routine
serum protein concentrations. Their pg/µL unit was supplied separately and is
not recorded in the source workbooks.

The displayed number is the original model's probability output, not a
clinically calibrated absolute risk estimate. The interface is for research
use and should not be used alone for care decisions.
