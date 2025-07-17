# Scheduling - Resource Planning App 📅

**A comprehensive Streamlit web application for managing and monitoring project resource allocation with AI-powered insights, advanced analytics, and real-time data sharing across all sections.**

## 🚀 Key Features

### 🔄 Real-Time Data Sharing (NEW v2.0)
- **Cross-Section Data Access:** Data loaded in Scheduling section is immediately available in Analytics, Chat, and Projects
- **Automatic Notifications:** Each section shows when data has been updated
- **Intelligent Caching:** Optimized performance with smart cache management
- **Session State Management:** Seamless data sharing across application sections
- **Import/Export Integration:** Manual file uploads automatically update all sections

### 🔐 Secure Access Control
- **Code-Based Authentication:** Simple and secure login system
- **Session Management:** Automatic logout and session control
- **Environment Configuration:** Flexible access code management
- **Security Best Practices:** Follows industry standards for access control

### 🤖 AI-Powered Chat Assistant
- **Schedulo AI:** Intelligent chatbot powered by Google Gemini 2.5 Flash
- **Multimodal Analysis:** Upload and analyze images (screenshots, charts, documents)
- **Natural Language Queries:** Ask questions about your data in plain English
- **Context Awareness:** Understands your scheduling data structure and provides relevant insights
- **Conversation Memory:** Maintains context across chat sessions
- **Real-Time Data Access:** Chatbot can access newly uploaded data immediately

### 📊 Advanced Analytics Dashboard
- **KPI Dashboard:** Real-time metrics (projects, users, clients, PMs, FTE allocation)
- **Specific Reports:** Detailed analysis by Project, User, PM, and Client
- **Interactive Visualizations:** Pie charts, trend lines, heatmaps, and data tables
- **Dynamic Filtering:** Filter by year, users, dimensions, and custom criteria
- **FTE Breakdown:** Monthly allocation analysis and capacity planning
- **Live Data Updates:** Analytics automatically reflect newly imported data

### 📋 Project Management
- **Comprehensive CRUD:** Add, edit, delete projects with full metadata
- **Resource Allocation:** Interactive FTE allocation per user and month
- **Data Validation:** Ensures data integrity and proper formatting
- **User Suggestions:** Auto-complete based on existing data
- **Excel Integration:** Seamless data persistence with automatic backups
- **Cross-Section Updates:** Changes in Projects are immediately visible in other sections

### 🔍 Smart Data Handling
- **Robust Error Handling:** Automatic recovery from corrupted files
- **Data Type Management:** Intelligent conversion and validation
- **Backup System:** Automatic timestamped backups
- **Sample Data:** Auto-generation of example data for new installations
- **Shared Data Management:** Centralized data access with fallback mechanisms

## 🛠️ Quick Start

### Prerequisites
- Python 3.8+
- Google API Key for Gemini AI (optional, for chat features)

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

# Set up environment variables (optional)
cp config.env.example .env  # Then edit with your access code
# or set ACCESS_CODE environment variable

# Run the application
streamlit run Scheduling.py
```

### Docker Deployment (Recommended)

```bash
# Build and run with Docker
./docker-build.sh build && ./docker-build.sh run

# Or on Windows
docker-build.bat build && docker-build.bat run

# Export/Import Docker image
./docker-build.sh export  # Creates scheduling-app-v2.0_TIMESTAMP.tar
./docker-build.sh import scheduling-app-v2.0_TIMESTAMP.tar
```

### Environment Setup

#### Required Environment Variables
```bash
# Codice di accesso per l'applicazione (default: "warhammer")
ACCESS_CODE=your_access_code_here

# API Key per Google Gemini (opzionale, per funzionalità chat)
GOOGLE_API_KEY=your_google_api_key_here
```

#### Access Code Setup
1. **Default Code:** The application uses "warhammer" as the default access code
2. **Custom Code:** Create a `.env` file with `ACCESS_CODE=your_secure_code`
3. **Security:** Change the default code in production environments

#### API Key Setup
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file or set as environment variable

## 📁 Repository Structure

```
scheduling/
├── Scheduling.py              # Main Streamlit application with data sharing
├── pages/
│   ├── 2_Projects.py         # Project management and CRUD operations
│   ├── 4_Analytics.py        # Advanced analytics and visualization dashboard
│   └── 5_Chat.py             # AI chat assistant with Gemini (multimodal)
├── src/
│   ├── __init__.py
│   ├── data_access.py        # Excel file operations and shared data management
│   ├── models.py             # Data models and schemas
│   └── utils.py              # Utility functions and data sharing helpers
├── data/                     # Excel data storage
├── .streamlit/               # Streamlit configuration for optimized performance
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker configuration with v2.0 optimizations
├── docker-compose.yml        # Docker Compose with data sharing support
├── docker-build.sh           # Linux build script with export/import
├── docker-build.bat          # Windows build script with export/import
├── README-Data-Sharing.md    # Detailed documentation for data sharing features
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

### 🔄 Data Sharing System (v2.0)
- **Immediate Access:** Data uploaded in Scheduling is instantly available in all sections
- **Smart Notifications:** Each section displays data update timestamps
- **Cache Management:** Intelligent cache invalidation and refresh
- **Fallback System:** Automatic fallback to file-based loading if shared data unavailable
- **Performance Optimization:** Reduced loading times through shared session state

### 🤖 AI Chat Assistant (Schedulo)
- **Natural Language Processing:** Ask questions like "Show me all projects for M. Sorrentino" or "Which projects are behind schedule?"
- **Image Analysis:** Upload screenshots, charts, or documents for AI analysis
- **Contextual Responses:** AI understands your data structure and provides relevant insights
- **Interactive Help:** Get guidance on using the application and interpreting data
- **Real-Time Data:** Chatbot can access newly uploaded data immediately

### 📈 Advanced Analytics
- **Dashboard KPI:** Overview metrics with real-time updates
- **Project Reports:** Detailed analysis by specific project with FTE trends
- **User Reports:** Individual resource analysis with project breakdown
- **PM Reports:** Project manager workload and resource management insights
- **Client Reports:** Client-specific project and resource analysis
- **Interactive Charts:** Zoom, filter, and explore data visually
- **Live Data Integration:** Analytics automatically reflect newly imported data

### 📋 Project Management
- **Add New Projects:** Comprehensive form with all project metadata
- **Resource Allocation:** Dynamic FTE allocation per user and month
- **Data Validation:** Ensures data integrity and proper formatting
- **User Suggestions:** Auto-complete based on existing data
- **Bulk Operations:** Efficient data entry and management
- **Cross-Section Updates:** Changes immediately visible in Analytics and Chat

## 🔐 Security & Authentication

### Access Control
- **Login System:** Simple code-based authentication
- **Session Management:** Automatic logout on page refresh
- **Default Access:** Code "warhammer" for development
- **Production:** Change default code via environment variables

### Security Best Practices
- **Environment Variables:** Store sensitive codes in `.env` files
- **Git Ignore:** `.env` files are excluded from version control
- **Code Rotation:** Regularly update access codes
- **Access Logging:** Monitor application access (future feature)

## 🔧 Configuration

### Data Storage
The application uses Excel files for data persistence:
- **Primary Data:** `data/SCHEDULING.xlsx` (main scheduling data)
- **Backup System:** Automatic backups with timestamps
- **Data Integrity:** Error handling and recovery mechanisms
- **Shared Access:** Session state management for cross-section data access

### Docker Configuration
- **Optimized Images:** Streamlit configuration optimized for data sharing
- **Performance Tuning:** Memory limits and resource management
- **Cache Volumes:** Persistent cache for improved performance
- **Export/Import:** Easy deployment with Docker image export/import

### Customization
- **Themes:** Customizable appearance via Streamlit configuration
- **Data Sources:** Extensible to support other data formats
- **AI Models:** Configurable AI provider and model selection

## 🚀 Roadmap

### Current Version (v2.0)
- ✅ Streamlit application with Excel backend
- ✅ Google Gemini AI integration
- ✅ Advanced analytics dashboard
- ✅ Multimodal image analysis
- ✅ Robust data handling and validation
- ✅ **Real-time data sharing across all sections**
- ✅ **Automatic notifications and cache management**
- ✅ **Docker optimization and export/import functionality**

### Upcoming Features (v3.0)
- 🔄 Authentication and role-based access

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
