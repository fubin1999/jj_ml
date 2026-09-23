"""Streamlit calculator for the project's final All Features model."""

import streamlit as st

from risk_model import predict_probability


st.set_page_config(page_title="GlycaPep-PD CVD Risk Calculator", page_icon="🫀")

st.title("GlycaPep-PD CVD Risk Calculator")
st.subheader(
    "1-Year CVD Risk Calculator for PD Patients Integrating Clinical "
    "Indicators and Glycated Peptide Biomarkers"
)
st.write("Enter measurements using the same units and definitions as the training data.")

with st.form("risk_calculator"):
    clinical, peptides = st.columns(2)
    with clinical:
        st.markdown("#### Clinical indicators")
        ktv = st.number_input("T Kt/v", min_value=0.0, value=None, step=0.01)
        diabetes = st.selectbox("Diabetes", ["Select", "No", "Yes"])
        ctnt = st.number_input("cTnT", min_value=0.0, value=None, step=0.001, format="%.3f")
        ga = st.number_input("GA", min_value=0.0, value=None, step=0.1)
        alb = st.number_input("ALB", min_value=0.0, value=None, step=0.1)
        phosphorus = st.number_input("P", min_value=0.0, value=None, step=0.01)
    with peptides:
        st.markdown("#### Glycated peptide biomarkers")
        a2mg = st.number_input("A2MG", min_value=0.0, value=None, step=0.01)
        apob = st.number_input("APOB", min_value=0.0, value=None, step=0.01)

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
        st.metric("Model-predicted probability of Endpoint = 1", f"{probability:.1%}")
        st.caption(f"Unrounded model probability: {probability:.6f}")

st.caption(
    "Research use only. This model output has not been established as a "
    "calibrated absolute clinical risk; it should not be used alone for care decisions."
)
