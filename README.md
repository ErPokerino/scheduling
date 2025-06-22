
# Scheduling - Resource Planning App 📅

**A Streamlit web application to manage and monitor project resource allocation for the Data Intelligence area.**

## Key Features
- **Project CRUD:** Add new projects, assign team members, and update details.
- **Monthly Allocation Grid:** Record each person's load (FTE) for every month, years ahead.
- **Filterable Schedule View:** Slice the table by project, user, year, status, etc.
- **Analytics Dashboard:** Charts summarising total capacity vs. booked effort per competence center, role, or individual.
- **Chat Assistant (placeholder):** Framework ready for future LLM integration to query or operate on the data using natural language.

## Quick Start

```bash
git clone https://github.com/YOUR_ORG/scheduling.git
cd scheduling
python -m venv .venv
source .venv/bin/activate   # on Windows use .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Repository Structure

```
scheduling/
├── app.py
├── pages/
│   ├── 1_Dashboard.py
│   ├── 2_Projects.py
│   ├── 3_Schedule.py
│   ├── 4_Analytics.py
│   └── 5_Chat.py
├── src/
│   ├── __init__.py
│   ├── data_access.py
│   ├── models.py
│   └── utils.py
├── requirements.txt
└── README.md
```

## Data Model Overview

The application is built around the `Scheduling` sheet of the legacy Excel workbook, which includes attributes such as:

- `ITEM_TYPE`, `DELIVERY_TYPE`, `WORKSTREAM`, `PROJECT_STREAM`
- `START_DATE`, `END_DATE`
- `PROJECT_DESCR`, `CLIENT`, `STATUS`
- `USER`, `JOB`, `PLANNED_FTE`
- Monthly allocation columns: `gen`, `feb`, ..., `dic`, `gen1`, ..., `dic1`

Allowed values for many of these fields are defined in the **LoVs** sheet (list‑of‑values).

## Roadmap

1. **v0.1 (this repo)** – Streamlit skeleton with in‑memory pandas backend.
2. **v0.2** – Persist data to SQLite, add authentication via Streamlit‑Auth.
3. **v0.3** – Integrate an LLM as chat assistant (e.g., OpenAI GPT‑4o) to run filtered queries, explain dashboards, and trigger actions.
4. **v1.0** – Containerisation with Docker and CI/CD to Cloud Run / ECS.

---

_Made with ❤️ by Data Intelligence._
