### Drishti — Voter Duplicate Detection README

#### Project Title
**Drishti — Voter Duplicate Detection**

#### Short description
**Drishti** is a Streamlit web app that detects likely duplicate voter records by combining deterministic blocking, fuzzy string similarity, and phonetic matching. Upload a voter CSV to run detection, review flagged pairs in the UI, filter by confidence and similarity type, and export results for human verification.

---

### Table of contents
- **Overview**  
- **Prerequisites**  
- **Installation**  
- **Quick Start Usage**  
- **Input CSV Schema**  
- **How Detection Works**  
- **Filtering and Output**  
- **Evaluation and Metrics**  
- **Demo and Deliverables**  
- **Troubleshooting**  
- **License and Contact**

---

### Overview
**Purpose:** Clean electoral rolls by automatically surfacing duplicate or near‑duplicate voter records to reduce manual verification effort.  
**Key features:**  
- Upload voter CSV and run duplicate detection.  
- Composite scoring using name similarity, address similarity, and phonetic matching.  
- Filter results by **confidence score**, **name similarity**, and **address similarity**.  
- Export flagged pairs with scores and confidence labels for review.

---

### Prerequisites
- **Python 3.9+**  
- Internet access for installing dependencies (if not using a prebuilt environment)  
- Recommended memory: **4 GB+** for moderate datasets; scale resources for larger datasets.

---

### Installation
1. **Clone the repo**  
   ```bash
   git clone <your-repo-url>
   cd <repo-folder>
   ```
2. **Create and activate a virtual environment**  
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux / macOS
   venv\Scripts\activate      # Windows
   ```
3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Streamlit app**  
   ```bash
   streamlit run app.py
   ```
   Open the URL shown in the terminal to access the UI.

---

### Quick Start Usage
1. Open the app in your browser.  
2. On the home page, click **Upload Voter Database** and select your CSV file.  
3. Click **Run Detection**. The app will:  
   - Preprocess and normalize fields.  
   - Block records by coarse keys (city, PIN, polling station).  
   - Compute pairwise similarity scores for candidate pairs.  
4. Results appear in three tabs: **High Confidence**, **Medium Confidence**, **Low Confidence**.  
5. Use the filter controls to refine results:
   - **Confidence Score**: slider to set minimum composite score.  
   - **Name Similarity**: slider or dropdown to filter by name similarity threshold.  
   - **Address Similarity**: slider or dropdown to filter by address similarity threshold.  
6. Select pairs to **Mark as Duplicate**, **Ignore**, or **Export**.

---

### Input CSV Schema
Provide a CSV with these columns (header names are case sensitive):
- **Voter_ID**  
- **Full_Name**  
- **Father_Mother_Name**  
- **Date_of_Birth** (YYYY-MM-DD recommended)  
- **Gender**  
- **Address**  
- **City**  
- **State**  
- **PIN_Code**  
- **Polling_Station**  
- **Registration_Date** (YYYY-MM-DD recommended)

**Example row:**  
`EXZ9580800,Oscar Brahmbhatt,Ishwar Sheth,1979-03-11,Male,"461, Chopra, Khammam 013290",Jalgaon,Tamil Nadu,846997,PS-005,2019-03-27`

---

### How Detection Works
- **Preprocessing:** lowercasing, trimming, punctuation removal, common abbreviation expansion.  
- **Blocking:** group records by City / PIN_Code / Polling_Station to limit comparisons.  
- **Similarity measures:**  
  - **Name similarity:** Levenshtein or Jaro–Winkler on `Full_Name` and `Father_Mother_Name`.  
  - **Phonetic matching:** Soundex/Metaphone to catch phonetic variants.  
  - **Address similarity:** token overlap and normalized token matching.  
- **Composite score:** weighted combination of name, phonetic, address, and DOB similarity.  
- **Confidence labels:** thresholds map composite score to **High**, **Medium**, **Low**.

---

### Filtering and Output
- **Filters available in UI:**  
  - **Confidence Score** (composite): set minimum threshold.  
  - **Name Similarity**: filter by name similarity value.  
  - **Address Similarity**: filter by address similarity value.  
  - **Date of Birth match**: exact or fuzzy DOB match toggle.
- **Output format:** Export CSV of flagged pairs with columns:  
  `record_A_id, record_B_id, name_similarity, address_similarity, phonetic_match, dob_match, composite_score, confidence_label, suggested_action`
- **Suggested actions:** `merge`, `mark_duplicate`, `ignore`, `manual_review`.

---

### Evaluation and Metrics
- **Recommended evaluation:** create a labeled test set of known duplicate and non‑duplicate pairs. Compute **Precision**, **Recall**, and **F1** at chosen thresholds.  
- **Example reported metrics:** Precision 0.92, Recall 0.88, F1 0.90 (replace with your measured values after running evaluation).  
- **How to reproduce:** include `evaluate.py` script that accepts a labeled pairs CSV and outputs metrics.

---

### Demo and Deliverables
Include the following in your submission:
- `README.md` (this file)  
- `requirements.txt` and environment setup instructions  
- Source code: preprocessing, matching, scoring, Streamlit app  
- `results/` folder with sample flagged pairs CSV and evaluation outputs  
- Demo video (2–3 minutes) showing upload → detection → filtering → export

---

### Troubleshooting
- **App slow on large CSVs:** increase memory or run blocking with a smaller block key; consider running on a machine with more CPU cores.  
- **Missing columns error:** ensure CSV header names match the schema exactly.  
- **False positives:** lower the weight on address or phonetic matching or raise the composite score threshold.  
- **False negatives:** lower thresholds or expand blocking keys to allow more candidate pairs.

---

