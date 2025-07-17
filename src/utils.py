import streamlit as st
import pandas as pd
from typing import Optional


def to_fte(days: float) -> float:
    """Convert person‑days to FTE units (assuming 20 work days per month)."""
    return days / 20.0


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a widget on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df

def update_shared_data(df: pd.DataFrame) -> None:
    """
    Aggiorna i dati condivisi nel session state e invalida il cache
    
    Args:
        df (pd.DataFrame): DataFrame da condividere
    """
    if hasattr(st, 'session_state'):
        st.session_state.shared_scheduling_data = df.copy()
        st.session_state.data_last_updated = pd.Timestamp.now()
        # Invalida il cache per forzare il ricaricamento nelle altre sezioni
        st.cache_data.clear()

def get_shared_data() -> Optional[pd.DataFrame]:
    """
    Ottiene i dati condivisi dal session state se disponibili
    
    Returns:
        Optional[pd.DataFrame]: DataFrame condiviso o None se non disponibile
    """
    try:
        if hasattr(st, 'session_state') and 'shared_scheduling_data' in st.session_state:
            shared_data = st.session_state.shared_scheduling_data
            if shared_data is not None:
                return shared_data.copy()
    except Exception as e:
        print(f"Error loading shared data: {e}")
    
    return None

def show_data_update_info() -> None:
    """
    Mostra informazioni sui dati condivisi se disponibili
    """
    if hasattr(st, 'session_state') and 'data_last_updated' in st.session_state:
        if st.session_state.data_last_updated:
            st.info(f"📊 **Dati aggiornati:** {st.session_state.data_last_updated.strftime('%d/%m/%Y %H:%M:%S')}")

def clear_shared_data() -> None:
    """
    Pulisce i dati condivisi dal session state
    """
    if hasattr(st, 'session_state'):
        if 'shared_scheduling_data' in st.session_state:
            del st.session_state.shared_scheduling_data
        if 'data_last_updated' in st.session_state:
            del st.session_state.data_last_updated
        st.cache_data.clear()

# Import necessari per filter_dataframe
try:
    from pandas.api.types import (
        is_categorical_dtype,
        is_datetime64_any_dtype,
        is_numeric_dtype,
        is_object_dtype,
    )
except ImportError:
    # Fallback per versioni più vecchie di pandas
    def is_categorical_dtype(obj):
        return hasattr(obj, 'dtype') and obj.dtype.name == 'category'
    
    def is_datetime64_any_dtype(obj):
        return hasattr(obj, 'dtype') and 'datetime' in str(obj.dtype)
    
    def is_numeric_dtype(obj):
        return hasattr(obj, 'dtype') and obj.dtype in ['int64', 'float64', 'int32', 'float32']
    
    def is_object_dtype(obj):
        return hasattr(obj, 'dtype') and obj.dtype == 'object'
