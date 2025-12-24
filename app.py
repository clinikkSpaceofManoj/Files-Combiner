import streamlit as st
import pandas as pd
import io

st.title("📂 Universal File Combiner Tool")
st.write("Upload CSV, Excel (xlsx/xls), or TXT files. Tool will combine them into one Excel file.")

uploaded_files = st.file_uploader(
    "Upload your files",
    type=["csv", "xlsx", "xls", "txt", "tsv"],
    accept_multiple_files=True
)

def read_file(file):
    name = file.name.lower()

    # CSV
    if name.endswith(".csv"):
        return pd.read_csv(file, dtype=str)

    # TXT / TSV → auto detect separator
    if name.endswith(".txt") or name.endswith(".tsv"):
        return pd.read_csv(file, dtype=str, sep=None, engine="python")

    # Excel
    if name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(file, dtype=str)

    return None


if uploaded_files:
    combined_list = []

    for file in uploaded_files:
        df = read_file(file)
        if df is not None:
            df["source_file"] = file.name
            combined_list.append(df)
        else:
            st.warning(f"❌ Could not read file: {file.name}")

    combined_df = pd.concat(combined_list, ignore_index=True)

    # Convert result to Excel in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        combined_df.to_excel(writer, index=False, sheet_name="Combined")

    st.success("🎉 Files combined successfully!")

    st.download_button(
        label="⬇️ Download Combined Excel",
        data=output.getvalue(),
        file_name="Combined_Output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
