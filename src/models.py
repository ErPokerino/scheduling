
from dataclasses import dataclass
import datetime as dt

@dataclass
class Project:
    descr: str
    client: str
    item_type: str
    delivery_type: str
    start: dt.date
    end: dt.date

# Additional dataclasses could go here...
