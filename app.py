"""Streamlit calculator for the project's final All Features model."""

import streamlit as st

from risk_model import predict_probability


YOUDEN_CUTOFF = 0.373


st.set_page_config(page_title="GlycaPep-PD CVD Risk Calculator", page_icon="🫀")

st.title("GlycaPep-PD CVD Risk Calculator")
st.subheader(
    "1-Year CVD Risk Calculator for PD Patients Integrating Clinical "
    "Indicators and Glycated Peptide Biomarkers"
)
st.write("Enter measurements using the same scale and definitions as the training data.")

with st.form("risk_calculator"):
    clinical, peptides = st.columns(2)
    with clinical:
        st.markdown("#### Clinical indicators")
        ktv = st.number_input(
            "T Kt/v (unitless)",
            min_value=0.0,
            value=None,
            step=0.01,
            help="Total Kt/V: total urea clearance index used to assess dialysis adequacy.",
        )
        diabetes = st.selectbox(
            "Diabetes (Yes/No)",
            ["Select", "No", "Yes"],
            help="Whether the patient has diabetes. Yes = 1; No = 0.",
        )
        ctnt = st.number_input(
            "cTnT (ng/mL)",
            min_value=0.0,
            value=None,
            step=0.001,
            format="%.3f",
            help=(
                "Cardiac troponin T, a blood marker of heart muscle injury. "
                "If the report uses ng/L, divide by 1,000 before entering "
                "(for example, 74 ng/L = 0.074 ng/mL)."
            ),
        )
        ga = st.number_input(
            "GA (%)",
            min_value=0.0,
            value=None,
            step=0.1,
            help="Glycated albumin: the percentage of serum albumin with glucose attached.",
        )
        alb = st.number_input(
            "ALB (g/L)",
            min_value=0.0,
            value=None,
            step=0.1,
            help="Serum albumin concentration, measured by the clinical laboratory.",
        )
        phosphorus = st.number_input(
            "P (mmol/L)",
            min_value=0.0,
            value=None,
            step=0.01,
            help="Serum phosphate (phosphorus) concentration.",
        )
    with peptides:
        st.markdown("#### Glycated peptide biomarkers")
        a2mg = st.number_input(
            "A2MG (pg/µL)",
            min_value=0.0,
            value=None,
            step=0.01,
            help=(
                "Glycated peptide GEAFTLK(g)ATVLNYLPK from "
                "alpha-2-macroglobulin (A2MG)."
            ),
        )
        apob = st.number_input(
            "APOB (pg/µL)",
            min_value=0.0,
            value=None,
            step=0.01,
            help=(
                "Glycated peptide K(g)QHLFVK from "
                "apolipoprotein B-100 (APOB). Enter its peptide assay "
                "result, not a routine serum APOB concentration."
            ),
        )

    submitted = st.form_submit_button("Calculate risk", type="primary")

if submitted:
    values = {
        "T Kt/v": ktv,
        "Diabetes": {"Select": None, "No": 0, "Yes": 1}[diabetes],
        "cTnT": ctnt,
        "GA": ga,
        "ALB": alb,
        "P": phosphorus,
        "A2MG": a2mg,
        "APOB": apob,
    }
    missing = [name for name, value in values.items() if value is None]
    if missing:
        st.error("Enter all eight measurements before calculating: " + ", ".join(missing))
    else:
        probability = predict_probability(values)
        classification = "Likely" if probability >= YOUDEN_CUTOFF else "Unlikely"
        st.metric(
            "Model-predicted probability of Endpoint = 1",
            f"{probability:.1%} · {classification}",
        )
        st.caption(
            f"Unrounded model probability: {probability:.6f}. "
            "The word follows the 37.3% Youden cutoff, "
            "not a clinical risk category."
        )

st.caption(
    "Research use only. This model output has not been established as a "
    "calibrated absolute clinical risk; it should not be used alone for care decisions."
)
