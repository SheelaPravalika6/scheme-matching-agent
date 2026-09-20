import streamlit as st
from backend.agent import run_eligibility_check

# --- Page setup ---
st.set_page_config(page_title="Scheme Matcher", page_icon="🎯", layout="centered")

# --- Custom styling ---
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }
    .main-header h1 {
        font-size: 2.2rem;
        margin-bottom: 0.2rem;
    }
    .main-header p {
        color: #888;
        font-size: 1rem;
    }
    .scheme-card {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #2ecc71;
    }
    .near-miss-card {
        background-color: #fffbf0;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #f39c12;
    }
    .badge-match {
        background-color: #2ecc71;
        color: white;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-near {
        background-color: #f39c12;
        color: white;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .doc-chip {
        display: inline-block;
        background-color: #e8eaf0;
        padding: 2px 10px;
        border-radius: 8px;
        font-size: 0.8rem;
        margin: 2px 4px 2px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="main-header">
    <h1>🎯 Government Scheme-Matching Assistant</h1>
    <p>Answer a few quick questions and discover which schemes you actually qualify for — with clear reasoning, not guesswork.</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# --- Input form ---
with st.form("profile_form"):
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Your age", min_value=18, max_value=100, value=25, step=1)
        category = st.selectbox("Your category", ["general", "obc", "sc", "st", "women"])
    with col2:
        occupation = st.selectbox("Current occupation", ["unemployed", "entrepreneur", "self-employed", "student", "salaried"])
        education = st.selectbox("Highest education", ["8th pass", "10th pass", "12th pass", "graduate", "post-graduate"])

    submitted = st.form_submit_button("🔍 Check My Eligibility", use_container_width=True)

# --- Run the check ---
if submitted:
    progress_text = "Checking your profile against government schemes..."
    my_bar = st.progress(0, text=progress_text)
    for pct in [20, 45, 70, 100]:
        my_bar.progress(pct, text=progress_text)
    my_bar.empty()

    try:
        with st.spinner("Generating your personalized explanation..."):
            result = run_eligibility_check(
                age=age, category=category, occupation=occupation, education=education
            )
    except Exception as e:
        st.error(f"Something went wrong: {e}")
        st.stop()

    matches = result["raw_results"]["matches"]
    near_misses = result["raw_results"]["near_misses"]

    st.divider()

    if not matches and not near_misses:
        st.warning("No matching or near-miss schemes found for this profile. Try adjusting your answers.")
    else:
        if matches:
            st.markdown("### ✅ You're eligible for these schemes")
            for scheme in matches:
                docs_html = "".join([f'<span class="doc-chip">{d}</span>' for d in scheme["documents_required"]])
                reasons_html = "".join([f"<li>{r}</li>" for r in scheme["reasons_passed"]])
                st.markdown(f"""
                <div class="scheme-card">
                    <span class="badge-match">MATCH</span>
                    <h4 style="margin-top:8px;">{scheme['name']}</h4>
                    <b>Why you qualify:</b>
                    <ul>{reasons_html}</ul>
                    <b>Documents required:</b><br>{docs_html}
                </div>
                """, unsafe_allow_html=True)

        if near_misses:
            st.markdown("### 🟡 Almost eligible")
            for scheme in near_misses:
                docs_html = "".join([f'<span class="doc-chip">{d}</span>' for d in scheme["documents_required"]])
                reasons_html = "".join([f"<li>{r}</li>" for r in scheme["reasons_failed"]])
                st.markdown(f"""
                <div class="near-miss-card">
                    <span class="badge-near">NEAR MISS</span>
                    <h4 style="margin-top:8px;">{scheme['name']}</h4>
                    <b>What's missing:</b>
                    <ul>{reasons_html}</ul>
                    <b>Documents you'd need if eligible:</b><br>{docs_html}
                </div>
                """, unsafe_allow_html=True)

        st.divider()
        with st.expander("📝 Read full AI explanation"):
            st.markdown(result["explanation"])