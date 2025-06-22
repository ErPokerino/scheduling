
from pathlib import Path
import pandas as pd

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "SCHEDULING.xlsx"
DATA_FILE.parent.mkdir(exist_ok=True, parents=True)

def load_scheduling(sheet_name: str = "Scheduling") -> pd.DataFrame:
    """Load the scheduling sheet as DataFrame."""
    return pd.read_excel(DATA_FILE, sheet_name=sheet_name)

def save_scheduling(df: pd.DataFrame, sheet_name: str = "Scheduling") -> None:
    """Save the DataFrame back to the Excel file (simple overwrite)."""
    with pd.ExcelWriter(DATA_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

def load_lovs() -> pd.DataFrame:
    return pd.read_excel(DATA_FILE, sheet_name="LoVs")
