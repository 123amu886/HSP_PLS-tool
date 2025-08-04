# 🧬 HSP & PLS Clinical Trial Extractor

A Streamlit-based tool to extract, filter, and export clinical trials for:
- **Hereditary Spastic Paraplegia (HSP)**
- **Primary Lateral Sclerosis (PLS)**

Data is sourced from [ClinicalTrials.gov](https://clinicaltrials.gov) and formatted like industry asset-tracking sheets.

---

## 🚀 Features

- 🔎 Filter by:
  - Trial recruitment status
  - Sponsor type (e.g., industry-only)
- 📑 Separate Excel sheets for HSP and PLS
- 🧬 Optional gene/pathway tagging (via trial title/intervention match)
- 🧾 Excel columns match standard disease portfolio trackers

---

## 📁 Output Columns

| Column           | Description                              |
|------------------|------------------------------------------|
| Trial Name        | Title of the clinical trial             |
| Participants      | Enrollment estimate                     |
| Drug              | Intervention(s) studied                 |
| Type(Obs/Int)     | Interventional or Observational         |
| TimeFrame Start   | Study start date                        |
| TimeFrame End     | Completion date                         |
| Sponsor           | Lead sponsor name                       |
| Investigator      | Listed study investigator               |
| Notes             | Blank column for manual entry           |
| Phase             | Study phase                             |
| Status            | Current recruitment status              |
| Gene/Pathway      | Auto-matched gene if enabled            |

---

## 🛠 Setup Instructions

### 1. Install dependencies

```bash
pip install -r requirements.txt
