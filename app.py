import streamlit as st
from workflow import TriageWorkflow
from database import init_db, list_cases, get_case, update_review
from config import get_settings

st.set_page_config(page_title="Customer Complaint Triage", page_icon="🧭", layout="wide")
init_db()

@st.cache_resource
def get_workflow():
    return TriageWorkflow()

workflow = get_workflow()
settings = get_settings()

st.title("Customer Complaint Triage & Escalation Assistant")
st.caption("Project 033 | NLP-assisted triage with deterministic escalation rules and human review")

with st.sidebar:
    st.header("Configuration")
    st.write(f"LLM provider: **{settings.llm_provider}**")
    st.write("API status: **Configured**" if settings.api_configured else "**Offline / rules-only mode**")
    st.info("Safety/legal cases and uncertain results require human review. This demo never sends customer messages or changes production systems.")

tab_new, tab_cases, tab_about = st.tabs(["New complaint", "Case review", "About"])

with tab_new:
    st.subheader("Submit a complaint")
    with st.form("complaint_form"):
        customer_ref = st.text_input("Customer reference", value="DEMO-001", help="Use a synthetic reference for this demo.")
        channel = st.selectbox("Source channel", ["web", "email", "phone", "chat", "other"])
        complaint_text = st.text_area("Complaint", height=160, placeholder="Describe the customer's complaint...")
        submitted = st.form_submit_button("Analyze and create case", type="primary")
    if submitted:
        try:
            result = workflow.process_complaint(
                customer_ref=customer_ref,
                complaint_text=complaint_text,
                source_channel=channel,
            )
            st.success(f"Case created: {result['case_id']}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Category", result["category"])
            c2.metric("Priority", result["priority"])
            c3.metric("Sentiment", result["sentiment"])
            st.write("**Recommended queue:**", result["recommended_queue"])
            st.write("**Course / product detected:**", result["product_course_entity"] or "Not detected")
            st.write("**Urgency phrases:**", ", ".join(result["urgency_phrases"]) or "None detected")
            st.write("**Summary:**", result["llm_summary"] or "No LLM summary available; review the complaint manually.")
            st.write("**Human review required:**", "Yes" if result["human_review_required"] else "No")
            st.write("**LLM status:**", result["llm_status"])
            if result["human_review_required"]:
                st.warning("This case requires human review before any customer-impacting action.")
        except Exception as exc:
            st.error(f"Could not process complaint: {exc}")

with tab_cases:
    st.subheader("Recent cases")
    cases = list_cases(limit=100)
    if not cases:
        st.info("No cases yet. Submit a complaint in the first tab.")
    else:
        st.dataframe(cases, use_container_width=True, hide_index=True)
        selected = st.selectbox("Select case ID", [row["case_id"] for row in cases])
        detail = get_case(selected)
        if detail:
            st.markdown("---")
            st.write(f"**Complaint:** {detail['original_text']}")
            st.write(f"**Summary:** {detail['llm_summary'] or 'Not available'}")
            st.write(f"**Priority / queue:** {detail['priority']} / {detail['recommended_queue']}")
            st.write(f"**Current review status:** {detail['review_status']}")
            with st.form("review_form"):
                review_status = st.selectbox("Review decision", ["pending", "approved", "needs_follow_up", "rejected"])
                reviewer = st.text_input("Reviewer", value="Demo Reviewer")
                notes = st.text_area("Review notes")
                save_review = st.form_submit_button("Save review")
            if save_review:
                update_review(selected, review_status, reviewer, notes)
                st.success("Review saved to the local database.")
                st.rerun()

with tab_about:
    st.subheader("How the prototype works")
    st.markdown("""
    1. Validate complaint input and store the original text.
    2. Detect category, product/course name, sentiment and urgency phrases.
    3. Apply deterministic escalation rules. Safety/legal rules take precedence.
    4. If an API key is configured, request a neutral summary from the selected LLM provider.
    5. Validate the response and save the case and audit logs in SQLite.
    6. A human reviewer records the review status and notes.

    **Important safeguards**
    - Use synthetic, anonymized or trainer-approved data only.
    - Never put API keys in source code or GitHub.
    - The assistant does not issue refunds/certificates, grade learners, send messages or update production systems.
    - LLM output is advisory. Rules determine priority and human review remains in control.
    """)


import sqlite3
import pandas as pd
import streamlit as st

st.divider()
st.subheader("📊 Universal Triage Analytics")

try:
    # Adjust the DB path/table name if your config.py uses a different filename
    conn = sqlite3.connect("complaints.db")
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
    if not tables.empty:
        table_name = tables["name"].iloc[0]
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        if not df.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                if "priority" in df.columns:
                    st.caption("Complaints by Priority (P0–P3)")
                    st.bar_chart(df["priority"].value_counts())
            with col2:
                if "queue" in df.columns:
                    st.caption("Complaints by Support Queue")
                    st.bar_chart(df["queue"].value_counts())
            with col3:
                if "category" in df.columns:
                    st.caption("Complaints by Category")
                    st.bar_chart(df["category"].value_counts())
        else:
            st.info("Submit a complaint above to populate the live triage charts.")
    conn.close()
except Exception as e:
    st.caption(f"Analytics unavailable: {e}")
