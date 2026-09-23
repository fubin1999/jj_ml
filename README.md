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

All eight fields are required in the interface. Use the same measurement units
and definitions as `data/train.csv`; `Diabetes` is coded No = 0, Yes = 1.
The frozen model coefficients and training means are in `risk_model.py`.
The original modeling pipeline's mean imputation remains available in
`predict_probability()` for programmatic callers passing `None`.

The displayed number is the original model's probability output, not a
clinically calibrated absolute risk estimate. The interface is for research
use and should not be used alone for care decisions.
