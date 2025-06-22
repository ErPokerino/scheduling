
def to_fte(days: float) -> float:
    """Convert person‑days to FTE units (assuming 20 work days per month)."""
    return days / 20.0
