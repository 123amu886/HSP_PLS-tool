import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="HSP & PLS Clinical Trial Extractor", layout="wide")
st.title("🧬 HSP & PLS Clinical Trial Extractor")

# -----------------------
# Sidebar Filters
# -----------------------
st.sidebar.header("Filter Trials")

status_options = [
    "Not yet recruiting", "Recruiting", "Enrolling by invitation",
    "Active, not recruiting", "Completed", "Terminated",
    "Withdrawn", "Suspended", "Unknown status"
]
selected_status = st.sidebar.multiselect(
    "📌 Trial Status",
    status_options,
    default=["Recruiting", "Active, not recruiting"]
)

industry_only = st.sidebar.checkbox("🏢 Industry Sponsored Only", value=False)

# You can expand this or allow CSV upload
gene_keywords = [
    "SPAST", "ATL1", "KIF5A", "ALS2", "PLS3",
    "SPG4", "REEP1", "SPG11", "SPG7"
]

# -----------------------
# Helper Functions
# -----------------------
def fetch_trials(condition, max_studies=100):
    """Query ClinicalTrials.gov API"""
    url = "https://clinicaltrials.gov/api/query/study_fields"
    fields = [
        "BriefTitle", "EnrollmentCount", "InterventionName", "StudyType",
        "StartDate", "PrimaryCompletionDate", "SponsorName", "Phase",
        "OverallStatus", "PrincipalInvestigator"
    ]
    params = {
        "expr": condition,
        "fields": ",".join(fields),
        "min_rnk": 1,
        "max_rnk": max_studies,
        "fmt": "json"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("StudyFieldsResponse", {}).get("StudyFields", [])
    else:
        return []

def tag_genes(text):
    """Return matched gene symbols in title/intervention"""
    return ", ".join([g for g in gene_keywords if g.lower() in text.lower()])

def format_trial_data(studies):
    """Convert raw trials to structured DataFrame"""
    records = []

    for study in studies:
        status = "; ".join(study.get("OverallStatus", []))
        sponsor = "; ".join(study.get("SponsorName", [])).lower()

        if status not in selected_status:
            continue

        if industry_only:
            if not any(keyword in sponsor for keyword in ["inc", "ltd", "pharma", "gmbh", "corp", "biosciences"]):
                continue

        title = "; ".join(study.get("BriefTitle", []))
        drug = "; ".join(study.get("InterventionName", []))
        gene = tag_genes(title + " " + drug)

        records.append({
            "Trial Name": title,
            "Participants": "; ".join(study.get("EnrollmentCount", [])),
            "Drug": drug,
            "Type(Obs/Int)": "; ".join(study.get("StudyType", [])),
            "TimeFrame Start": "; ".join(study.get("StartDate", [])),
            "TimeFrame End": "; ".join(study.get("PrimaryCompletionDate", [])),
            "Sponsor": "; ".join(study.get("SponsorName", [])),
            "Investigator": "; ".join(study.get("PrincipalInvestigator", [])),
            "Notes": "",
            "Phase": "; ".join(study.get("Phase", [])),
            "Status": status,
            "Gene/Pathway": gene
        })

    return pd.DataFrame(records)

# -----------------------
# Main UI Trigger
# -----------------------
if st.button("🔍 Fetch Clinical Trials"):

    with st.spinner("Fetching HSP & PLS trials from ClinicalTrials.gov..."):
        hsp_raw = fetch_trials("Hereditary Spastic Paraplegia")
        pls_raw = fetch_trials("Primary Lateral Sclerosis")

        hsp_df = format_trial_data(hsp_raw)
        pls_df = format_trial_data(pls_raw)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            hsp_df.to_excel(writer, index=False, sheet_name="HSP Trials")
            pls_df.to_excel(writer, index=False, sheet_name="PLS Trials")
        output.seek(0)  # 🔁 ensure buffer is reset

        st.success("✅ Excel file ready!")
        st.download_button(
            label="📥 Download Excel File",
            data=output,
            file_name="HSP_PLS_Clinical_Trials.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
