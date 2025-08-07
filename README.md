# 🏗️ Report Generator (PDF/HTML → Structured Report)

## 📌 Overview

This project creates a fully offline, AI-powered pipeline that:

- Converts **PDFs** and **web pages** into structured text chunks
- Embeds and stores them in a vector database using **Docling** + **HuggingFace**
- Queries the vector index to generate a report from compiled content
- Outputs the final result in **Markdown**
- Offers a **Streamlit** UI to preview, clean, and export the report as **PDF** or **Word (.docx)**

---

## 🧭 Instructions

### 1. Add Your Sources and Index
- Add webpage URLs to `html_sources.txt` (one per line)
- Place local PDFs in the `sources/` folder

### 2.Index

-Run the docling_indexer.py file to generate vector embeddings, these will be stored in the "data" folder as text nodes

### 3. Generate Outlook Report
-The report will be saved in the output/ folder as a .md (Markdown) file.
-Each run will generate a timestamped report to ensure no files are overwritten.
-If you want to disable the LLM and generate a simple report from the indexed content (e.g. for testing), run the MockLLM_generator.py file instead.

### 4. Preview and Export via Streamlit

run the streamlit app from terminal through the command: streamlit run streamlit_app.py

-You can preview the generated Markdown report interactively.

-Export the report as a PDF or Word (.docx) file.

-Drag-and-drop a different .md file to switch the report being viewed.

#### 5. Ad Hoc Customizations: 

->Change the report structure array in the generate_outlook.py/MockLLM_generator.py file to change the prompt accordingly.
->Change the LLM model used in the generate_outlook.py file here: 
Settings.llm = Ollama(model="  ", request_timeou=t=60.0)

<pre> ```text real_estate_outlook/ │ ├── data/ # Indexed vectors saved as nodes.pkl ├── sources/ # Folder with input PDF files ├── html_sources.txt # List of HTML source URLs ├── output/ # Generated reports (.md, .pdf, .docx) │ ├── docling_indexer.py # Embeds PDFs and HTML into vector format ├── generate_outlook.py # Generates report using vector DB and LLM ├── MockLLM_generator.py # Fallback version without LLM ├── app_streamlit.py # Streamlit UI for report viewing/export ├── requirements.txt # Python dependencies └── README.md # This file ``` </pre>


