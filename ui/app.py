import streamlit as st
import pandas as pd
from models import ComprehensiveDiagnosisReport

def render_dashboard(report: ComprehensiveDiagnosisReport):
    st.set_page_config(page_title="Bug Diagnosis Report", layout="wide")
    st.title("🐞 Automated Bug Diagnosis Report")
    st.caption("Powered by Milestone 3 Multi-Agent RAG Pipeline")
    st.markdown("---")

    # 1. Submission Overview
    sub = report.input_data.submission
    st.subheader(f"📌 Submission: [{sub.bug_id}] {sub.title}")
    st.info(sub.description)

    # 2. Triage & Log Analysis Summary Grid
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🚦 Triage Agent Output")
        t = report.input_data.triage
        st.write(f"**Severity:** `{t.severity}` | **Priority:** `{t.priority}`")
        st.write(f"**Component:** `{t.affected_component}`")
        st.write(f"**Confidence:** `{t.confidence_score * 100:.0f}%`")
        st.caption(f"Reasoning: {t.reasoning}")

    with col2:
        st.markdown("### 📋 Log Analysis Output")
        la = report.input_data.log_analysis
        st.write(f"**Exception:** `{la.exception_type or 'N/A'}`")
        st.write(f"**Failure Point:** `{la.failure_point or 'N/A'}`")
        st.write(f"**Path:** `{la.affected_code_path or 'N/A'}`")
        st.caption(f"Error: {la.error_message or 'None'}")

    st.markdown("---")

    # 3. Root Cause Agent (M3.1)
    st.markdown("## 🔍 Root Cause Analysis")
    rc = report.root_cause_analysis
    if rc.status == "Insufficient Evidence":
        st.warning("⚠️ Insufficient Evidence: Could not establish a confident root cause from historical knowledge base.")
    else:
        for idx, h in enumerate(rc.hypotheses, 1):
            with st.expander(f"Hypothesis #{idx}: {h.hypothesis} (Confidence: {h.confidence_score*100:.0f}%)", expanded=(idx==1)):
                st.markdown(f"**Agent Reasoning:** {h.agent_reasoning}")
                st.markdown("**Retrieved Knowledge Base Evidence:**")
                for ev in h.retrieved_evidence:
                    st.markdown(f"- `{ev}`")

    st.markdown("---")

    # 4. Duplicate Detection Agent (M3.2)
    st.markdown("## 👯 Duplicate & Related Issues")
    dup = report.duplicate_detection
    
    badge_color = "red" if dup.duplicate_status == "Likely Duplicate" else "orange" if dup.duplicate_status == "Related Issue" else "green"
    st.markdown(f"**Status:** :{badge_color}[{dup.duplicate_status}]")

    if dup.top_matches:
        match_data = []
        for m in dup.top_matches:
            match_data.append({
                "Defect ID": m.defect_id,
                "Title": m.title,
                "Component": m.affected_component,
                "Similarity": f"{m.similarity_score * 100:.1f}%",
                "Historical Resolution": m.resolution_summary
            })
        st.table(pd.DataFrame(match_data))

    st.markdown("---")

    # 5. Remediation Agent (M3.3)
    st.markdown("## 🛠️ Recommended Remediation & Fix Plan")
    rem = report.remediation_plan
    
    if rem.status == "Insufficient Evidence":
        st.warning("⚠️ General guidance generated due to low historical ground confidence.")

    for opt in rem.options:
        st.success(f"**Action Plan:** {opt.recommendation}")
        rcol1, rcol2 = st.columns(2)
        with rcol1:
            st.write(f"**Target Location:** `{opt.target_module_or_file}`")
            st.write(f"**Source Basis:** `{opt.source_type}`")
            st.write(f"**Recommendation Confidence:** `{opt.confidence_score*100:.0f}%`")
        with rcol2:
            st.markdown("**Validation Checklist:**")
            for step in opt.validation_steps:
                st.markdown(f"- [ ] {step}")