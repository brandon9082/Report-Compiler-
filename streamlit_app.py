import streamlit as st
from pathlib import Path
import tempfile
import pypandoc

# === METADATA CLEANER ===
def clean_metadata(text: str) -> str:
    skip_prefixes = (
        'source_url:', 'filename:', 'title:',
        'query:', 'answer:',
        'context information is below', 'given the context',
        '---------------------', 'trailing query', 'trailing answer'
    )
    lines = text.splitlines()
    return '\n'.join(
        line for line in lines
        if not any(line.strip().lower().startswith(prefix) for prefix in skip_prefixes)
    )

# === STREAMLIT SETUP ===
st.set_page_config(page_title="🏠 Real Estate Outlook Viewer", layout="wide")
st.title("📊 Q1 2025 Real Estate Outlook")

# === FILE UPLOAD OR DEFAULT ===
uploaded_file = st.sidebar.file_uploader("📁 Upload a Markdown report", type=["md"])
default_path = Path("output/residential_real_estate_outlook_Q1_2025.md")

if uploaded_file:
    raw_text = uploaded_file.read().decode("utf-8")
    st.sidebar.success("✅ Using uploaded file.")
elif default_path.exists():
    raw_text = default_path.read_text()
    st.sidebar.success("✅ Using default report file.")
else:
    st.warning("⚠️ No markdown report found. Please upload a .md file or run generate_outlook.py.")
    st.stop()

# === TOGGLE FOR CLEANING ===
strip = st.checkbox("🧼 Strip metadata", value=True)
final_text = clean_metadata(raw_text) if strip else raw_text

# === PREVIEW ===
st.markdown("### 📄 Report Preview")
st.markdown(final_text, unsafe_allow_html=False)

# === DOWNLOAD MARKDOWN ===
st.download_button(
    label="📥 Download Markdown",
    data=final_text,
    file_name="real_estate_report_cleaned.md" if strip else "real_estate_report_raw.md",
    mime="text/markdown"
)

# === EXPORT TO PDF & DOCX ===
st.markdown("### 📤 Export as PDF or DOCX")

col1, col2 = st.columns(2)

with col1:
    if st.button("📄 Export to PDF"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            pypandoc.convert_text(
                final_text,
                to='pdf',
                format='md',
                outputfile=tmp_pdf.name,
                extra_args=['--standalone']
            )
            with open(tmp_pdf.name, "rb") as f:
                st.download_button(
                    label="⬇️ Download PDF",
                    data=f,
                    file_name="real_estate_report.pdf",
                    mime="application/pdf"
                )

with col2:
    if st.button("📝 Export to DOCX"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_docx:
            pypandoc.convert_text(
                final_text,
                to='docx',
                format='md',
                outputfile=tmp_docx.name,
                extra_args=['--standalone']
            )
            with open(tmp_docx.name, "rb") as f:
                st.download_button(
                    label="⬇️ Download DOCX",
                    data=f,
                    file_name="real_estate_report.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
