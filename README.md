# Scheduling - Resource Planning App 📅

**A comprehensive Streamlit web application for managing and monitoring project resource allocation with AI-powered insights and advanced analytics.**

## 🚀 Key Features

### 🤖 AI-Powered Chat Assistant
- **Schedulo AI:** Intelligent chatbot powered by Google Gemini 2.5 Flash
- **Multimodal Analysis:** Upload and analyze images (screenshots, charts, documents)
- **Natural Language Queries:** Ask questions about your data in plain English
- **Context Awareness:** Understands your scheduling data structure and provides relevant insights
- **Conversation Memory:** Maintains context across chat sessions

### 📊 Advanced Analytics Dashboard
- **KPI Dashboard:** Real-time metrics (projects, users, clients, PMs, FTE allocation)
- **Specific Reports:** Detailed analysis by Project, User, PM, and Client
- **Interactive Visualizations:** Pie charts, trend lines, heatmaps, and data tables
- **Dynamic Filtering:** Filter by year, users, dimensions, and custom criteria
- **FTE Breakdown:** Monthly allocation analysis and capacity planning

### 📋 Project Management
- **Comprehensive CRUD:** Add, edit, delete projects with full metadata
- **Resource Allocation:** Interactive FTE allocation per user and month
- **Data Validation:** Ensures data integrity and proper formatting
- **User Suggestions:** Auto-complete based on existing data
- **Excel Integration:** Seamless data persistence with automatic backups

### 🔍 Smart Data Handling
- **Robust Error Handling:** Automatic recovery from corrupted files
- **Data Type Management:** Intelligent conversion and validation
- **Backup System:** Automatic timestamped backups
- **Sample Data:** Auto-generation of example data for new installations

## 🛠️ Quick Start

### Prerequisites
- Python 3.8+
- Google API Key for Gemini AI

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_ORG/scheduling.git
cd scheduling

# Create virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env  # Then edit with your Google API key
# or set GOOGLE_API_KEY environment variable

# Run the application
streamlit run Scheduling.py
```

### Environment Setup

#### Required Environment Variables
```bash
GOOGLE_API_KEY=your_google_api_key_here
```

#### API Key Setup
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file or set as environment variable

## 📁 Repository Structure

```
scheduling/
├── Scheduling.py              # Main Streamlit application
├── pages/
│   ├── 2_Projects.py         # Project management and CRUD operations
│   ├── 4_Analytics.py        # Advanced analytics and visualization dashboard
│   └── 5_Chat.py             # AI chat assistant with Gemini (multimodal)
├── src/
│   ├── __init__.py
│   ├── data_access.py        # Excel file operations and data persistence
│   ├── models.py             # Data models and schemas
│   └── utils.py              # Utility functions and helpers
├── data/                     # Excel data storage
├── requirements.txt          # Python dependencies
├── TODO.md                   # Development roadmap and progress
└── README.md                 # This file
```

## 📊 Data Model Overview

The application is built around the `Scheduling` sheet of the Excel workbook, which includes:

### Project Information
- `PROJECT_DESCR`: Project name and description
- `CLIENT`: Client name
- `PM_SM`: Project Manager/Scrum Master
- `SOW_ID`, `JIRA_KEY`: Contract and ticket references

### Classification
- `ITEM_TYPE`: Activity type (Development, Analysis, Testing, etc.)
- `DELIVERY_TYPE`: Delivery type (Internal, External, etc.)
- `WORKSTREAM`, `PROJECT_STREAM`, `AREA_CC`: Organizational classification

### Timeline
- `START_DATE`, `END_DATE`: Project start and end dates
- `YEAR`, `YEAR_OF_COMPETENCE`: Year tracking

### Resource Management
- `USER`: Team member name
- `JOB`: Job role/position
- `PLANNED_FTE`, `ACTUAL_FTE`: Planned vs actual FTE allocation
- `STATUS`: Project status (Not Started, In Progress, Completed, etc.)
- `PROGRESS_%`: Project completion percentage

### Monthly Allocation
- `gen`, `feb`, `mar`, `apr`, `mag`, `giu`, `lug`, `ago`, `set`, `ott`, `nov`, `dic`: Monthly FTE allocation

Allowed values for many fields are defined in the **LoVs** sheet (list-of-values).

## 🎯 Features in Detail

### 🤖 AI Chat Assistant (Schedulo)
- **Natural Language Processing:** Ask questions like "Show me all projects for M. Sorrentino" or "Which projects are behind schedule?"
- **Image Analysis:** Upload screenshots, charts, or documents for AI analysis
- **Contextual Responses:** AI understands your data structure and provides relevant insights
- **Interactive Help:** Get guidance on using the application and interpreting data

### 📈 Advanced Analytics
- **Dashboard KPI:** Overview metrics with real-time updates
- **Project Reports:** Detailed analysis by specific project with FTE trends
- **User Reports:** Individual resource analysis with project breakdown
- **PM Reports:** Project manager workload and resource management insights
- **Client Reports:** Client-specific project and resource analysis
- **Interactive Charts:** Zoom, filter, and explore data visually

### 📋 Project Management
- **Add New Projects:** Comprehensive form with all project metadata
- **Resource Allocation:** Dynamic FTE allocation per user and month
- **Data Validation:** Ensures data integrity and proper formatting
- **User Suggestions:** Auto-complete based on existing data
- **Bulk Operations:** Efficient data entry and management

## 🔧 Configuration

### Data Storage
The application uses Excel files for data persistence:
- **Primary Data:** `data/SCHEDULING.xlsx` (main scheduling data)
- **Backup System:** Automatic backups with timestamps
- **Data Integrity:** Error handling and recovery mechanisms

### Customization
- **Themes:** Customizable appearance via Streamlit configuration
- **Data Sources:** Extensible to support other data formats
- **AI Models:** Configurable AI provider and model selection

## 🚀 Roadmap

### Current Version (v0.2)
- ✅ Streamlit application with Excel backend
- ✅ Google Gemini AI integration
- ✅ Advanced analytics dashboard
- ✅ Multimodal image analysis
- ✅ Robust data handling and validation

### Upcoming Features (v0.3)
- 🔄 Authentication and role-based access
- 🔄 Advanced search and filtering
- 🔄 Export functionality (CSV, Excel, PDF)
- 🔄 Real-time notifications
- 🔄 Mobile-responsive design

### Future Versions (v1.0+)
- 📋 SQLite/PostgreSQL database backend
- 📋 Docker containerization
- 📋 Cloud deployment (Streamlit Community Cloud, Azure, AWS)
- 📋 API endpoints for external integrations
- 📋 Advanced AI features (predictions, auto-scheduling)

## 🛠️ Troubleshooting

### Common Issues

#### Excel File Errors
- The app automatically creates a new file with sample data if the existing one is corrupted
- Check the `data/` folder for backup files
- Restore from backup by copying the backup file to `SCHEDULING.xlsx`

#### API Key Issues
- Ensure your Google API key is properly set in environment variables
- Verify the key has access to Gemini API
- Check API quotas and limits

#### Data Type Errors
- The app handles data type conversion automatically
- Ensure Excel file format is compatible (xlsx)
- Check for special characters in data fields

#### Performance Issues
- Large datasets may require optimization
- Consider filtering data for better performance
- Monitor memory usage with large Excel files

### Data Recovery
If your Excel file becomes corrupted:
1. Check the `data/` folder for backup files
2. The app will automatically create a new file with sample data
3. You can restore from backup by copying the backup file to `SCHEDULING.xlsx`

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest

# Format code
black .

# Lint code
flake8
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Streamlit** for the amazing web framework
- **Google Gemini** for powerful AI capabilities
- **Plotly** for interactive visualizations
- **Pandas** for data manipulation
- **OpenPyXL** for Excel file handling

---

**Made with ❤️ by Data Intelligence Team**

*For support and questions, please open an issue on GitHub or contact the development team.*
