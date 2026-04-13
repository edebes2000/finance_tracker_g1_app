import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from fintrackpy import process_statement


st.set_page_config(page_title="Finance Tracker", layout="wide")

st.title("Personal Finance Tracker")
st.write("Upload a Santander statement (.xlsx or .csv) to generate a summary report.")

uploaded_file = st.file_uploader(
    "Upload statement",
    type=["xlsx", "csv"]
)

if uploaded_file is not None:
    try:
        # Keep original extension so your loader can detect file type
        suffix = Path(uploaded_file.name).suffix.lower()

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getbuffer())
            temp_path = tmp.name

        ledger = process_statement(temp_path)

        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Income", f"{ledger.total_income():,.2f}")
        col2.metric("Total Expenses", f"{ledger.total_expenses():,.2f}")
        col3.metric("Net Total", f"{ledger.net_total():,.2f}")

        # First 20 transactions
        st.subheader("Transactions Preview (First 20)")
        preview_rows = []

        for tx in list(ledger)[:20]:
            preview_rows.append(
                {
                    "Date": tx.date,
                    "Description": tx.description,
                    "Amount": tx.amount,
                    "Category": tx.category if tx.category is not None else "uncategorized",
                }
            )

        preview_df = pd.DataFrame(preview_rows)
        st.dataframe(preview_df, use_container_width=True)

        # Category totals
        st.subheader("Spending by Category")

        category_totals = ledger.category_totals(kind="expense")

        df = pd.DataFrame(
            list(category_totals.items()),
            columns=["Category", "Total"]
        )

        # Keep only expenses (negative totals) and convert to positive for visualization
        df["Total"] = df["Total"].abs()

        st.bar_chart(df.set_index("Category"))

    except Exception as e:
        st.error(f"An error occurred while processing the statement: {e}")
