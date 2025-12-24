import streamlit as st
import pandas as pd
import io

st.title("📂 Universal File Combiner Tool")
st.write("Upload CSV, Excel, or TXT files → Combine → Select Columns → Download Excel")

uploaded_files = st.file_uploader(
    "Upload your files",
    type=["csv", "xlsx", "xls", "txt", "tsv"],
    accept_multiple_files=True
)

def read_file(file):
    name = file.name.lower()

    if name.endswith(".csv"):
        return pd.read_csv(file, dtype=str)

    if name.endswith(".txt") or name.endswith(".tsv"):
        return pd.read_csv(file, dtype=str, sep=None, engine="python")

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

    st.success("🎉 Files combined successfully!")

    st.subheader("🔽 Select columns you want in the final output")

    all_columns = list(combined_df.columns)

    selected_columns = st.multiselect(
        "Choose columns to include:",
        options=all_columns,
        default=all_columns  # by default export all
    )

    final_df = combined_df[selected_columns]

    # Convert result to Excel in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        final_df.to_excel(writer, index=False, sheet_name="Combined")

    st.download_button(
        label="⬇️ Download Excel with Selected Columns",
        data=output.getvalue(),
        file_name="Combined_Selected_Columns.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
