# Scheduling - Resource Planning App 📅

**A Streamlit web application to manage and monitor project resource allocation for the Data Intelligence area.**

## Key Features
- **Project Management:** Add new projects, assign team members, and update details with comprehensive metadata.
- **Resource Allocation:** Record each person's load (FTE) for every month, years ahead with interactive data editing.
- **Filterable Schedule View:** Slice the table by project, user, year, status, and other dimensions.
- **Analytics Dashboard:** Pie chart view of FTE distribution and monthly workload per user with interactive filters.
- **Chat Assistant (Gemini):** Conversational assistant that leverages Google Gemini Flash 2.5 to answer questions about the data and how to use the app.

## Quick Start

```bash
git clone https://github.com/YOUR_ORG/scheduling.git
cd scheduling
python -m venv venv
source venv/bin/activate   # on Windows use venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env  # then edit with your Google API key
# or set GOOGLE_API_KEY environment variable

streamlit run Scheduling.py
```

## Repository Structure

```
scheduling/
├── Scheduling.py              # Main Streamlit application
├── pages/
│   ├── 2_Projects.py         # Project management and CRUD operations
│   ├── 4_Analytics.py        # Analytics and visualization dashboard
│   └── 5_Chat.py             # AI chat assistant with Gemini
├── src/
│   ├── __init__.py
│   ├── data_access.py        # Excel file operations and data persistence
│   ├── models.py             # Data models and schemas
│   └── utils.py              # Utility functions and helpers
├── data/                     # Excel data storage
├── requirements.txt
└── README.md
```

## Data Model Overview

The application is built around the `Scheduling` sheet of the Excel workbook, which includes attributes such as:

- **Project Information:** `PROJECT_DESCR`, `CLIENT`, `PM_SM`, `SOW_ID`, `JIRA_KEY`
- **Classification:** `ITEM_TYPE`, `DELIVERY_TYPE`, `WORKSTREAM`, `PROJECT_STREAM`, `AREA_CC`
- **Timeline:** `START_DATE`, `END_DATE`, `YEAR`, `YEAR_OF_COMPETENCE`
- **Resource Management:** `USER`, `JOB`, `PLANNED_FTE`, `ACTUAL_FTE`, `STATUS`, `PROGRESS_%`
- **Monthly Allocation:** `gen`, `feb`, `mar`, `apr`, `mag`, `giu`, `lug`, `ago`, `set`, `ott`, `nov`, `dic`

Allowed values for many of these fields are defined in the **LoVs** sheet (list‑of‑values).

## Features in Detail

### 📋 Projects Page
- **Add New Projects:** Comprehensive form with all project metadata
- **Resource Allocation:** Dynamic FTE allocation per user and month
- **Data Validation:** Ensures data integrity and proper formatting
- **User Suggestions:** Auto-complete based on existing data

### 📈 Analytics Page
- **FTE Distribution:** Interactive pie charts by various dimensions
- **Monthly Workload:** Line charts showing FTE trends per user
- **Year Filtering:** Analyze data by specific years
- **User Filtering:** Focus on specific team members

### 💬 Chat Assistant
- **Natural Language Queries:** Ask questions about your data in plain English
- **Gemini Integration:** Powered by Google's latest AI model
- **Context Awareness:** Understands your scheduling data structure
- **Interactive Help:** Get guidance on using the application

## Environment Setup

### Required Environment Variables
```bash
GOOGLE_API_KEY=your_google_api_key_here
```

### API Key Setup
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file or set as environment variable

## Data Storage

The application uses Excel files for data persistence:
- **Primary Data:** `data/SCHEDULING.xlsx` (main scheduling data)
- **Backup System:** Automatic backups with timestamps
- **Data Integrity:** Error handling and recovery mechanisms

## Roadmap

1. **v0.1 (Current)** – Streamlit application with Excel backend and Gemini integration
2. **v0.2** – Persist data to SQLite, add authentication via Streamlit‑Auth
3. **v0.3** – Enhanced AI features and advanced analytics
4. **v1.0** – Containerisation with Docker and CI/CD to Cloud Run / ECS

## Troubleshooting

### Common Issues
- **Excel File Errors:** The app will automatically create a new file with sample data if the existing one is corrupted
- **API Key Issues:** Ensure your Google API key is properly set in environment variables
- **Data Type Errors:** The app handles data type conversion automatically

### Data Recovery
If your Excel file becomes corrupted:
1. Check the `data/` folder for backup files
2. The app will automatically create a new file with sample data
3. You can restore from backup by copying the backup file to `SCHEDULING.xlsx`

---

_Made with ❤️ by Data Intelligence._
