import streamlit as st
import pandas as pd
import io
import uuid

# ------------------------------
# App Header
# ------------------------------
st.title("📂 Universal File Combiner Tool")
st.write("Upload CSV, Excel, or TXT files → Combine → Select Columns → Download Excel")

# ------------------------------
# File Upload
# ------------------------------
uploaded_files = st.file_uploader(
    "Upload your files",
    type=["csv", "xlsx", "xls", "txt", "tsv"],
    accept_multiple_files=True
)

# ------------------------------
# File Reader
# ------------------------------
def read_file(file):
    name = file.name.lower()

    if name.endswith(".csv"):
        return pd.read_csv(file, dtype=str)

    if name.endswith(".txt") or name.endswith(".tsv"):
        return pd.read_csv(file, dtype=str, sep=None, engine="python")

    if name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(file, dtype=str)

    return None

# ------------------------------
# Main Logic
# ------------------------------
if uploaded_files:
    combined_list = []

    for file in uploaded_files:
        df = read_file(file)
        if df is not None:
            df["source_file"] = file.name
            combined_list.append(df)
        else:
            st.warning(f"❌ Could not read: {file.name}")

    if not combined_list:
        st.error("No valid files to combine.")
        st.stop()

    combined_df = pd.concat(combined_list, ignore_index=True)
    st.success("🎉 Files combined successfully!")

    # ------------------------------
    # Column Selection
    # ------------------------------
    st.subheader("🔎 Column Selection")
    all_columns = combined_df.columns.tolist()

    search_text = st.text_input("Search columns:")

    if search_text:
        filtered_columns = [c for c in all_columns if search_text.lower() in c.lower()]
    else:
        filtered_columns = all_columns

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Select All"):
            st.session_state.selected_columns = filtered_columns

    with col2:
        if st.button("Clear All"):
            st.session_state.selected_columns = []

    selected_columns = st.multiselect(
        "Choose columns to include in output:",
        filtered_columns,
        default=st.session_state.get("selected_columns", filtered_columns),
        key="selected_columns"
    )

    if not selected_columns:
        st.warning("⚠️ Please select at least one column to download.")
        st.stop()

    final_df = combined_df[selected_columns]

    # ------------------------------
    # Excel Conversion
    # ------------------------------
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        final_df.to_excel(writer, index=False, sheet_name="Combined")

    # ------------------------------
    # File Name Logic
    # ------------------------------
    st.subheader("📄 Output File Name")

    user_filename = st.text_input(
        "Enter output file name (optional, without .xlsx):",
        placeholder="e.g. merged_data"
    )

    if user_filename.strip():
        final_filename = f"{user_filename.strip()}.xlsx"
    else:
        random_name = uuid.uuid4().hex[:8]
        final_filename = f"combined_{random_name}.xlsx"

    st.caption(f"📎 File will be downloaded as: **{final_filename}**")

    # ------------------------------
    # Download Button
    # ------------------------------
    st.download_button(
        label="⬇️ Download Excel (Selected Columns)",
        data=output.getvalue(),
        file_name=final_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
