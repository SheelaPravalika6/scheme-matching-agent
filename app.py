import streamlit as st
from backend.agent import run_eligibility_check

# Page setup
st.set_page_config(page_title="Government Scheme Matcher", page_icon="🎯", layout="centered")

st.title("🎯 Government Scheme-Matching Assistant")
st.write("Answer a few quick questions and find out which government schemes you qualify for.")

st.divider()

# --- Input form ---
with st.form("profile_form"):
    age = st.number_input("Your age", min_value=18, max_value=100, value=25, step=1)

    category = st.selectbox(
        "Your category",
        ["general", "obc", "sc", "st", "women"]
    )

    occupation = st.selectbox(
        "Your current occupation",
        ["unemployed", "entrepreneur", "self-employed", "student", "salaried"]
    )

    education = st.selectbox(
        "Your highest education level",
        ["8th pass", "10th pass", "12th pass", "graduate", "post-graduate"]
    )

    submitted = st.form_submit_button("Check My Eligibility")

# --- Run the check when the form is submitted ---
if submitted:
    with st.spinner("Checking your eligibility against government schemes..."):
        try:
            result = run_eligibility_check(
                age=age,
                category=category,
                occupation=occupation,
                education=education
            )
        except Exception as e:
            st.error(f"Something went wrong while checking eligibility: {e}")
            st.stop()

    matches = result["raw_results"]["matches"]
    near_misses = result["raw_results"]["near_misses"]

    st.divider()

    # --- No results at all ---
    if not matches and not near_misses:
        st.warning("No matching or near-miss schemes were found for this profile. Try adjusting your answers.")
    else:
        # --- Matched schemes ---
        if matches:
            st.subheader("✅ You're eligible for these schemes")
            for scheme in matches:
                with st.container(border=True):
                    st.markdown(f"### {scheme['name']}")
                    st.markdown("**Why you qualify:**")
                    for reason in scheme["reasons_passed"]:
                        st.markdown(f"- {reason}")
                    st.markdown("**Documents required:**")
                    st.markdown(", ".join(scheme["documents_required"]))

        # --- Near misses ---
        if near_misses:
            st.subheader("🟡 Almost eligible")
            for scheme in near_misses:
                with st.container(border=True):
                    st.markdown(f"### {scheme['name']}")
                    st.markdown("**What's missing:**")
                    for reason in scheme["reasons_failed"]:
                        st.markdown(f"- {reason}")
                    st.markdown("**Documents you'd need if eligible:**")
                    st.markdown(", ".join(scheme["documents_required"]))

        # --- AI explanation, full text ---
        st.divider()
        st.subheader("📝 Full explanation")
        st.markdown(result["explanation"])