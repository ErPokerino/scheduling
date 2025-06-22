from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import pandas as pd
import streamlit as st


def to_fte(days: float) -> float:
    """Convert person‑days to FTE units (assuming 20 work days per month)."""
    return days / 20.0


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Generate UI controls to filter a DataFrame column-wise and return the filtered view.

    The function renders, inside an *expander*, widgets that adapt to the dtype of
    each column so that users can interactively constrain the data shown in the
    table. It supports:
    - Categorical / low-cardinality columns   → multiselect of allowed values.
    - Numeric columns                        → range slider.
    - Datetime columns                       → date range picker.
    - All other dtypes (strings, objects …)  → substring / regex text input.

    Parameters
    ----------
    df : pd.DataFrame
        The source DataFrame.

    Returns
    -------
    pd.DataFrame
        The filtered DataFrame.
    """
    if df.empty:
        return df

    df_filtered = df.copy()

    with st.expander("🔍 Filtra dati", expanded=False):
        if st.button("❌ Azzera filtri", key=f"reset_{id(df)}"):
            # Rimuove tutte le chiavi di sessione relative ai filtri e ricarica la pagina
            for k in list(st.session_state.keys()):
                if k.startswith("filter_"):
                    st.session_state.pop(k)
            st.experimental_rerun()

        for col in df_filtered.columns:
            if is_categorical_dtype(df_filtered[col]) or df_filtered[col].nunique() < 15:
                # Treat as categorical
                values = df_filtered[col].dropna().unique().tolist()
                selected = st.multiselect(
                    f"Valori per `{col}`",
                    options=values,
                    default=list(values),
                    key=f"filter_cat_{col}",
                )
                df_filtered = df_filtered[df_filtered[col].isin(selected)]

            elif is_numeric_dtype(df_filtered[col]):
                min_val = float(df_filtered[col].min())
                max_val = float(df_filtered[col].max())
                if min_val == max_val:
                    continue  # nothing to filter
                step = (max_val - min_val) / 100.0 or 1.0
                user_min, user_max = st.slider(
                    f"Range `{col}`",
                    min_value=min_val,
                    max_value=max_val,
                    value=(min_val, max_val),
                    step=step,
                    key=f"filter_num_{col}",
                )
                df_filtered = df_filtered[df_filtered[col].between(user_min, user_max)]

            elif is_datetime64_any_dtype(df_filtered[col]):
                start_date = df_filtered[col].min().date()
                end_date = df_filtered[col].max().date()
                date_min, date_max = st.date_input(
                    f"Range `{col}`",
                    value=(start_date, end_date),
                    key=f"filter_date_{col}",
                )
                if isinstance(date_min, tuple):
                    # When user clears selection the widget may return a single date
                    date_min, date_max = date_min
                df_filtered = df_filtered[
                    df_filtered[col].between(pd.to_datetime(date_min), pd.to_datetime(date_max))
                ]

            else:
                text = st.text_input(
                    f"Filtro testo / regex in `{col}`",
                    key=f"filter_text_{col}",
                )
                if text:
                    df_filtered = df_filtered[df_filtered[col].astype(str).str.contains(text, case=False, na=False)]

    return df_filtered
