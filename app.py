"""Streamlit calculator for the project's final All Features model."""

from pathlib import Path

import streamlit as st

from risk_model import predict_probability


YOUDEN_CUTOFF = 0.373


st.set_page_config(
    page_title="GlycaPep-PD CVD Risk Calculator", page_icon="🫀", layout="wide"
)
st.markdown(
    "<style>" + Path(__file__).with_name("ui.css").read_text() + "</style>",
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class="brandbar">
      <div class="brand"><span class="brandmark" aria-hidden="true">+</span>GlycaPep-PD</div>
      <span class="research-tag">Research tool</span>
    </div>
    <div class="hero">
      <p class="eyebrow">Peritoneal dialysis · 1-year horizon</p>
      <h1><span>GlycaPep-PD</span> CVD Risk Calculator</h1>
      <p class="intro">1-Year CVD Risk Calculator for PD Patients Integrating Clinical
      Indicators and Glycated Peptide Biomarkers</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("#### Model formula")
with st.container(key="formula_panel"):
    probability_formula, predictor_formula = st.columns([1, 3])
    with probability_formula:
        st.latex(r"p = \frac{1}{1 + e^{-\eta}}")
    with predictor_formula:
        st.latex(
            r"""
            \begin{aligned}
            \eta ={}& 4.540128
            - 0.999037(\mathrm{T\ Kt/v})
            + 0.773180(\mathrm{Diabetes}) \\
            &+ 4.856619(\mathrm{cTnT})
            + 0.052606(\mathrm{GA})
            - 0.067553(\mathrm{ALB}) \\
            &- 1.271284(\mathrm{P})
            + 0.000176316(\mathrm{A2MG})
            + 0.057099(\mathrm{APOB}).
            \end{aligned}
            """
        )
    st.caption("Diabetes: No = 0; Yes = 1. Coefficients are rounded for display.")

st.markdown("#### Calculator")
with st.form("risk_calculator"):
    clinical, peptides = st.columns([2, 1], gap="medium")
    with clinical, st.container(key="clinical_panel"):
        st.markdown('<div class="panel-kicker">6 measurements</div>', unsafe_allow_html=True)
        st.markdown("##### Clinical indicators")
        left, right = st.columns(2)
        with left:
            ktv = st.number_input(
                "T Kt/v (unitless)",
                min_value=0.0,
                value=None,
                step=0.01,
                help="Total Kt/V: total urea clearance index used to assess dialysis adequacy.",
            )
        with right:
            diabetes = st.selectbox(
                "Diabetes (Yes/No)",
                ["Select", "No", "Yes"],
                help="Whether the patient has diabetes. Yes = 1; No = 0.",
            )
        left, right = st.columns(2)
        with left:
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
        with right:
            ga = st.number_input(
                "GA (%)",
                min_value=0.0,
                value=None,
                step=0.1,
                help="Glycated albumin: the percentage of serum albumin with glucose attached.",
            )
        left, right = st.columns(2)
        with left:
            alb = st.number_input(
                "ALB (g/L)",
                min_value=0.0,
                value=None,
                step=0.1,
                help="Serum albumin concentration, measured by the clinical laboratory.",
            )
        with right:
            phosphorus = st.number_input(
                "P (mmol/L)",
                min_value=0.0,
                value=None,
                step=0.01,
                help="Serum phosphate (phosphorus) concentration.",
            )
    with peptides, st.container(key="peptide_panel"):
        st.markdown('<div class="panel-kicker">2 measurements</div>', unsafe_allow_html=True)
        st.markdown("##### Glycated peptide biomarkers")
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

        st.markdown(
            """<div class="peptide-notes">
            <strong>A2MG</strong> · alpha-2-macroglobulin<br>
            <code>GEAFTLK(g)ATVLNYLPK</code><br><br>
            <strong>APOB</strong> · apolipoprotein B-100<br>
            <code>K(g)QHLFVK</code>
            </div>""",
            unsafe_allow_html=True,
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
        with st.container(key="result_panel"):
            result_value, result_label = st.columns([2, 1])
            with result_value:
                st.metric(
                    "Model-predicted probability of Endpoint = 1",
                    f"{probability:.1%}",
                )
            with result_label:
                badge_class = "likely" if classification == "Likely" else "unlikely"
                st.markdown(
                    f'<span class="result-badge {badge_class}">{classification}</span>'
                    '<p class="result-cutoff">37.3% Youden cutoff</p>',
                    unsafe_allow_html=True,
                )
            st.caption(
                f"Unrounded model probability: {probability:.6f}. "
                "The word follows the 37.3% Youden cutoff, "
                "not a clinical risk category."
            )

with st.container(key="research_footer"):
    st.caption(
        "Research use only. This model output has not been established as a "
        "calibrated absolute clinical risk; it should not be used alone for care decisions."
    )
