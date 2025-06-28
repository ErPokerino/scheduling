from pathlib import Path
import pandas as pd
import shutil
from datetime import datetime

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "SCHEDULING.xlsx"
DATA_FILE.parent.mkdir(exist_ok=True, parents=True)

def create_backup():
    """Create a backup of the current file if it exists."""
    if DATA_FILE.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = DATA_FILE.parent / f"SCHEDULING_backup_{timestamp}.xlsx"
        try:
            shutil.copy2(DATA_FILE, backup_file)
            return backup_file
        except Exception as e:
            print(f"Failed to create backup: {e}")
    return None

def create_new_scheduling_file():
    """Create a new scheduling Excel file with proper structure."""
    # Create sample data structure based on the code analysis
    sample_data = {
        'PROJECT_DESCR': ['Sample Project 1', 'Sample Project 2'],
        'USER': ['User1', 'User2'],
        'CLIENT': ['Client A', 'Client B'],
        'PM_SM': ['PM1', 'PM2'],
        'ITEM_TYPE': ['Development', 'Analysis'],
        'DELIVERY_TYPE': ['Internal', 'External'],
        'WORKSTREAM': ['WS1', 'WS2'],
        'YEAR_OF_COMPETENCE': [2024, 2024],
        'START_DATE': ['2024-01-01', '2024-02-01'],
        'END_DATE': ['2024-12-31', '2024-12-31'],
        'SOW_ID': ['SOW001', 'SOW002'],
        'JIRA_KEY': ['JIRA-001', 'JIRA-002'],
        'PROJECT_STREAM': ['Stream1', 'Stream2'],
        'AREA_CC': ['Area1', 'Area2'],
        'JOB': ['Job1', 'Job2'],
        'PLANNED_FTE': [1, 2],
        'ACTUAL_FTE': [1, 2],
        'STATUS': ['In Progress', 'Not Started'],
        'PROGRESS_%': [50, 0],
        'YEAR': [2024, 2024],
        'gen': [1, 1],
        'feb': [1, 1],
        'mar': [1, 1],
        'apr': [1, 1],
        'mag': [1, 1],
        'giu': [1, 1],
        'lug': [1, 1],
        'ago': [1, 1],
        'set': [1, 1],
        'ott': [1, 1],
        'nov': [1, 1],
        'dic': [1, 1]
    }
    
    df = pd.DataFrame(sample_data)
    
    # Convert date columns
    df['START_DATE'] = pd.to_datetime(df['START_DATE'])
    df['END_DATE'] = pd.to_datetime(df['END_DATE'])
    
    # Create LoVs sheet with sample data
    lovs_data = {
        'Category': [
            'Status', 'Status', 'Status', 'Status', 'Status',
            'Item Type', 'Item Type', 'Item Type',
            'Delivery Type', 'Delivery Type'
        ],
        'Value': [
            'Not Started', 'In Progress', 'Completed', 'On Hold', 'Cancelled',
            'Development', 'Analysis', 'Testing',
            'Internal', 'External'
        ]
    }
    lovs_df = pd.DataFrame(lovs_data)
    
    # Save to new Excel file
    with pd.ExcelWriter(DATA_FILE, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Scheduling', index=False)
        lovs_df.to_excel(writer, sheet_name='LoVs', index=False)
    
    return df

def load_scheduling(sheet_name: str = "Scheduling") -> pd.DataFrame:
    """Load the scheduling sheet as DataFrame with error handling."""
    try:
        df = pd.read_excel(DATA_FILE, sheet_name=sheet_name)
        
        # Normalize data types to prevent Arrow conversion issues
        # Ensure YEAR_OF_COMPETENCE is always string
        if "YEAR_OF_COMPETENCE" in df.columns:
            df["YEAR_OF_COMPETENCE"] = df["YEAR_OF_COMPETENCE"].fillna("").astype(str)
        
        # Ensure other text columns are strings
        text_columns = ["PM_SM", "WORKSTREAM", "SOW_ID", "JIRA_KEY", "PROJECT_STREAM", "AREA_CC", "JOB", "STATUS", 
                       "CLIENT", "ITEM_TYPE", "DELIVERY_TYPE"]
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].fillna("").astype(str)
        
        # Ensure numeric columns are integers
        numeric_columns = ["YEAR", "PROGRESS_%", "PLANNED_FTE", "ACTUAL_FTE"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        
        # Ensure date columns are datetime objects
        date_columns = ["START_DATE", "END_DATE"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        
        return df
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        print("Creating backup and new file...")
        
        # Create backup of corrupted file
        backup_file = create_backup()
        if backup_file:
            print(f"Backup created: {backup_file}")
        
        # Create new file with sample data
        print("Creating new scheduling file with sample data...")
        return create_new_scheduling_file()

def save_scheduling(df: pd.DataFrame, sheet_name: str = "Scheduling") -> None:
    """Save the DataFrame back to the Excel file with error handling."""
    try:
        # Load existing LoVs if they exist
        try:
            existing_lovs = pd.read_excel(DATA_FILE, sheet_name="LoVs")
        except:
            existing_lovs = None
        
        with pd.ExcelWriter(DATA_FILE, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            if existing_lovs is not None:
                existing_lovs.to_excel(writer, sheet_name="LoVs", index=False)
    except Exception as e:
        print(f"Error saving Excel file: {e}")
        # Fallback: try to save with overwrite
        try:
            with pd.ExcelWriter(DATA_FILE, engine="openpyxl", mode="w") as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        except Exception as e2:
            print(f"Failed to save file: {e2}")
            raise

def load_lovs() -> pd.DataFrame:
    """Load the LoVs sheet as DataFrame with error handling."""
    try:
        return pd.read_excel(DATA_FILE, sheet_name="LoVs")
    except Exception as e:
        print(f"Error loading LoVs: {e}")
        # Return empty DataFrame with expected structure
        return pd.DataFrame(columns=pd.Index(['Category', 'Value']))
