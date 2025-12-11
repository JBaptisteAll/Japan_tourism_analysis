
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=E60026&height=120&section=header&text=Japan%20Travel%20Insights&fontSize=38&fontColor=ffffff&fontAlignY=35" />
</p>
<p align="center">  </p>


[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://japantravelsurveyanalysis.streamlit.app/)
![GitHub Actions](https://github.com/JBaptisteAll/Japan_tourism_analysis/actions/workflows/run_clean_import.yml/badge.svg)

---

# Technical Documentation

## 1. Project Overview

This repository contains an end-to-end data pipeline and analytics application built around a survey about travel intentions to Japan, with a specific focus on the Yamagata prefecture.

The goal is to:
- Collect structured feedback from potential travellers in French and English.
- Centralize and standardize responses in a single cleaned dataset.
- Automate the data refresh process on a fixed schedule.
- Expose an interactive Streamlit dashboard that allows stakeholders (e.g. 360, local tourism actors) to explore the data and download filtered datasets.

Technically, this project demonstrates:
- Automated data ingestion from Google Sheets.
- Centralized data cleaning and standardization logic in Python.
- Scheduled data processing with GitHub Actions.
- A performant, cached Streamlit application for exploratory analysis.
- A clear separation between **data pipeline** and **data product**.

---

## 2. High-Level Architecture

```mermaid
flowchart LR
    A[Google Forms FR] --> B[Google Sheet FR]
    A2[Google Forms EN] --> B2[Google Sheet EN]

    B --> C[Combined Sheet via IMPORTRANGE]
    B2 --> C

    C --> D[Python Processing Script]
    D --> E[data_processed/df_clean.csv]

    E --> F[Streamlit App]
    F -->|Download CSV / Filtered Data| G[End Users (360, stakeholders)]

    H[GitHub Actions (cron)] --> D
```

### Key ideas:

- Two separate forms (FR/EN) feed two answer sheets.
- A third sheet uses ``IMPORTRANGE`` to centralize all responses.
- A Python script reads from the central sheet, cleans and standardizes the data, and writes a single processed CSV.
- The Streamlit app reads the processed CSV and provides interactive analysis.
- A GitHub Actions workflow runs on a bi-monthly schedule to keep the processed dataset up to date.

---

## 3. Data Collection Layer

- Forms:
    - ``Google Form (FR)`` – French questionnaire.
    - ``Google Form (EN)`` – English questionnaire.
    - The questionnaire contains branching logic (e.g. some questions are skipped if the user has no interest in Japan).

- Raw Storage:
    - ``Google Sheet FR`` and ``Google Sheet EN`` each collect responses from their respective forms.
    - A third sheet uses ``IMPORTRANGE`` to union the two sheets into a single combined table.

- Access Control:
    - Only the project owner has write access to the Google Sheets.
    - Sheets are protected to avoid accidental structure changes.
    - The Python script connects using the ``fileId`` and ``gid``, not the sheet name, to ensure robust identification of the data source.

---

## 4. Repository Structure

```
.
├── .devcontainer/
│   └── devcontainer.json        
├── .github/workflows
│   └── run_clean_import.yml     
├── Archives/
│   └── 01_clean.ipynb           # Initial cleaning experiments
├── Assets/
│   ├── regiions_of_japan.png    # potentially used for .md
├── data_processed/
│   ├── df_clean.csv             # clean csv for streamlit
├── clean_import.py              # Python script
├── JTSA_app.py                  # Streamlit app
├── README.md                    # This file
└── requirements.txt             # Python dependencies
```

## 5. Data Processing & Cleaning
### 5.1 Data Fetching

- The script connects to the combined Google Sheet using:
    - A ``fileId`` (unique ID of the Google Sheet file).
    - A ``gid`` (ID of the specific worksheet/tab).

- The credentials and configuration (fileId, gid, API key or service account) are stored as environment variables or in a ``.env`` file (ignored by Git).

### 5.2 Cleaning Rules Module

All data cleaning logic is centralized in ``clean_import.py.``

Typical responsibilities:

- Standardize languages (e.g. unify French/English values into a single language).
- Normalize categories (e.g. motivations, perceived barriers, budget ranges).
- Harmonize age groups, country names, and other categorical fields.
- Handle free-text responses by mapping them into broader categories where relevant.

Example:  
*Global cleaning helpers (functions)*
```python
def normalize_text(s):
    if pd.isna(s): return s
    return (str(s)
            .strip()
            .lower()
            .replace("à", "a").replace("â", "a").replace("ä", "a")
            ...
            .replace("$", "").replace("€", "").replace("-"," "))

def clean_age (age):
    if pd.isna(age):
        return None
    age = str(age).strip()
    if age.startswith("18"):
        return "18-24"
    elif age.startswith("25"):
        return "25-34"
    ...
    else:
        return "18 and less"

def smart_split(val):
    if pd.isna(val):
        return[]
    s = str(val)
    parts = re.split(r',(?![^()]*\))', s)
    parts = [p.strip() for p in parts if p.strip()]
    return parts

def list_to_fixed_cols_prefs(lst, k=MAX_CHOICES):
    lst = (lst + [np.nan]*k) [:k]
    return pd.Series(lst, index=[f"most_wanted_pref_to_visit_{i+1}" for i in range(k)])

```
*Renaming columns*
```python
df_clean = df_clean.rename(columns={
    "Quel est votre nationalité?": "nationality",
    "  Dans quel pays résidez-vous actuellement ?  ": "country",

    ...

    "Qu’est-ce qui rendrait le Japon plus attractif comme destination pour vous ?  ": "recomendation_to_improve_attractiveness"
})
```
*Mapping with and without normalization*
```python
#Japan_prefered_accomodation (normalize_text) 
clean_japan_accomodation = {

    "hotel classique (3 4 etoiles)": "Standard hotel (3–4 stars)",
    "hotel haut de gamme / luxe (5 etoiles)": "Luxury / high-end hotel (5 stars)",
    "ryokan (auberge traditionnelle)": "Ryokan (traditional Japanese inn)",
    "capsule hotel": "Capsule hotel",
    "airbnb / logement chez l’habitant": "Airbnb / homestay",
    "hostel/ auberge de jeunesse": "Hostel"
}

#rating_interest_*
clean_rating_japan = {

    "Pas du tout important": "Not important at all",
    "Peu important": "Slightly important",
    "Assez important": "Moderately important",
    "Très important": "Very important",
    "Essentiel": "Essential",
}
```

*Multi-choice question processing*
```python
regions_list = df_clean["most_wanted_pref_to_visit"].apply(smart_split)
df_prefs = regions_list.apply(list_to_fixed_cols_prefs)
df_clean = pd.concat([df_clean, df_prefs], axis=1)
```

*Column-by-column cleaning*
```python
df_clean["nationality"] = (df_clean["nationality"]
                               .map(normalize_text)
                               .map(mapping)
                               .fillna(df_clean["nationality"]))
    
df_clean["age_group"] = df_clean["age_group"].apply(clean_age)

rating_cols = ['rating_interest_culture_and_history', 'rating_interest_food',
       'rating_interest_nature_hiking', 'rating_interest_shopping_and_techno',
       'rating_interest_events_and_festivals', 'rating_interest_wellness',
       'rating_interest_theme_park']
df_clean[rating_cols] = (df_clean[rating_cols]
                            .map(lambda x: clean_rating_japan.get(x, x)))
```

### 5.3 Orchestration Script

The orchestration of the end-to-end transformation is done with ``clean_import.py``:

```python
df_clean.to_csv("data_processed/df_clean.csv", index=False)
```

This script is:
- Executed manually during development.
- Triggered automatically by GitHub Actions on a schedule.

---

## 6. Streamlit Application

The Streamlit app is located in ``JTSA_app.py`` and is designed for interactive exploratory analysis.

Key features:
- Filters by nationality, age group, interest in Japan, preferred regions, perceived barriers, etc.

- Pre-built charts to understand:
    - Who is interested in visiting Japan.
    - Which regions/cities are most attractive.
    - Why some travellers are not interested in Japan or choose other destinations.

- Download buttons:
    - Full raw dataset.
    - Filtered subset based on selected filters.

### 6.1 Data Loading & Caching

Because the dataset only changes twice a month, the app uses a cache with a long TTL:

```python
@st.cache_data(ttl=15*24*3600) #Update every 15 days
def load_data(path: str = "data_processed/df_clean.csv") -> pd.DataFrame: 
    df = pd.read_csv(path)
```

This ensures:
- Fast app startup and interactions.
- Automatic cache refresh every 15 days, aligned with the GitHub Actions schedule.

---

## 7. Automation with GitHub Actions

The workflow ``run_clean_import.yml`` is responsible for:
- Checking out the repository.
- Installing Python and dependencies.
- Loading environment variables / secrets (e.g. Google credentials, export URL).
- Running ``clean_import.py``.
- Committing and pushing the updated ``data_processed/df_clean.csv`` back to the repository (optional, depending on the chosen strategy).

Example structure:
```yml
name: Process Survey Data

on:
  schedule:
    - cron: "0 6 1,15 * *"  # 1st and 15th of each month at 05:00 UTC
  workflow_dispatch:        # manual trigger

jobs:
  process-data:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run processing script
        env:
          GOOGLE_SHEET_EXPORT_URL: ${{ secrets.GOOGLE_SHEET_EXPORT_URL }}
        run: python -m src.process_data

      # Optionally commit and push updated CSV file
      # - name: Commit and push changes
      #   run: |
      #     git config user.name "github-actions[bot]"
      #     git config user.email "github-actions[bot]@users.noreply.github.com"
      #     git add data_processed/df_clean.csv
      #     git commit -m "Update processed survey data"
      #     git push
```

---

## 8. Future Work

Planned or possible extensions:

- Add an LLM-powered chatbot connected to the cleaned CSV to answer natural language questions about the dataset.
- Generate PDF reports based on user-selected charts.
- Implement segmentation / clustering of traveller profiles to support more targeted recommendations for tourism strategies.
- Add unit tests for key cleaning functions (e.g. country and age mappings).

--- 

## 9. Contact
For questions or collaboration, please contact the project owner via GitHub or LinkedIn.