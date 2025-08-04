import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="HSP & PLS Clinical Trial Extractor", layout="wide")
st.title("🧬 HSP & PLS Clinical Trial Extractor")

def get_trials(condition, max_studies=100, recruitment_status=None, phase_filter=None, industry_only=False):
    url = "https://clinicaltrials.gov/api/query/study_fields"
    fields = [
        "BriefTitle", "EnrollmentCount", "InterventionName", "StudyType",
        "StartDate", "PrimaryCompletionDate", "SponsorName", "LeadSponsorName",
        "Phase", "OverallStatus", "CollaboratorName", "PrincipalInvestigator"
    ]
    params = {
        "expr": condition,
        "fields": ",".join(fields),
        "min_rnk": 1,
        "max_rnk": max_studies,
        "fmt": "json"
    }
    r = requests.get(url, params=params)
    if r.status_code != 200:
        return []
    studies = r.json().get("StudyFieldsResponse", {}).get("StudyFields", [])
    
    filtered = []
    for s in studies:
        status = "; ".join(s.get("OverallStatus", [])).strip().lower()
        phase = "; ".join(s.get("Phase", [])).strip().lower()
        sponsor = "; ".join(s.get("LeadSponsorName", [])).strip().lower()
        
        if recruitment_status and recruitment_status.lower() not in status:
            continue
        if phase_filter and phase_filter.lower() not in phase:
            continue
        if industry_only and not any(ind in sponsor for ind in ["inc", "ltd", "pharma", "gmbh", "s.a.", "llc", "plc", "corporation"]):
            continue
        
        filtered.append(s)
    return filtered

def format_trials(raw_data, gene_mapping=None):
    rows = []
    for study in raw_data:
        interventions = "; ".join(study.get("InterventionName", []))
        trial_name = "; ".join(study.get("BriefTitle", []))
        gene_target = ""
        if gene_mapping:
            for gene in gene_mapping:
                if gene.lower() in trial_name.lower() or gene.lower() in interventions.lower():
                    gene_target = gene
                    break
        rows.append({
            "Trial Name": trial_name,
            "Participants": "; ".join(study.get("EnrollmentCount", [])),
            "Drug": interventions,
            "Type(Obs/Int)": "; ".join(study.get("StudyType", [])),
            "TimeFrame Start": "; ".join(study.get("StartDate", [])),
            "TimeFrame End": "; ".join(study.get("PrimaryCompletionDate", [])),
            "Sponsor": "; ".join(study.get("LeadSponsorName", [])),
            "Investigator": "; ".join(study.get("PrincipalInvestigator", [])),
            "Notes": "",
            "Phase": "; ".join(study.get("Phase", [])),
            "Gene/Pathway": gene_target
        })
    return pd.DataFrame(rows)

# UI filters
st.sidebar.header("🔍 Filters")
recruitment_status = st.sidebar.selectbox(
    "Recruitment Status",
    ["", "Recruiting", "Not yet recruiting", "Active, not recruiting", "Completed", "Suspended", "Withdrawn"],
    index=0
)
phase_filter = st.sidebar.selectbox(
    "Study Phase",
    ["", "Phase 1", "Phase 2", "Phase 3", "Phase 4"],
    index=0
)
industry_only = st.sidebar.checkbox("Industry Only Trials")

uploaded_gene_file = st.sidebar.file_uploader("Optional: Upload Gene Mapping (CSV with column 'Gene')")

gene_list = None
if uploaded_gene_file:
    gene_df = pd.read_csv(uploaded_gene_file)
    gene_list = gene_df["Gene"].dropna().tolist()

if st.button("🔍 Fetch Clinical Trials"):
    with st.spinner("Fetching trials from ClinicalTrials.gov..."):
        hsp_raw = get_trials(
            "Hereditary Spastic Paraplegia",
            recruitment_status=recruitment_status if recruitment_status else None,
            phase_filter=phase_filter if phase_filter else None,
            industry_only=industry_only
        )
        pls_raw = get_trials(
            "Primary Lateral Sclerosis",
            recruitment_status=recruitment_status if recruitment_status else None,
            phase_filter=phase_filter if phase_filter else None,
            industry_only=industry_only
        )
        hsp_df = format_trials(hsp_raw, gene_mapping=gene_list)
        pls_df = format_trials(pls_raw, gene_mapping=gene_list)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            hsp_df.to_excel(writer, index=False, sheet_name="HSP Trials")
            pls_df.to_excel(writer, index=False, sheet_name="PLS Trials")

        st.success(f"✅ Done! {len(hsp_df)} HSP trials and {len(pls_df)} PLS trials ready.")
        st.download_button(
            "📥 Download Excel File",
            output.getvalue(),
            file_name="HSP_PLS_Clinical_Trials.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
