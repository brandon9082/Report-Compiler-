import os
import re
import pickle
from pathlib import Path
from datetime import datetime
from llama_index.core import Settings, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings


Settings.llm = Ollama(model="tinyllama", request_timeou=t=60.0)


print("✅ Ollama LLM successfully loaded.")


# === Settings ===
Settings.embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")

# === Paths ===
REPORT_TITLE = "Q1 2025 Residential Real Estate Outlook"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = Path("output")
output_dir.mkdir(parents=True, exist_ok=True)

OUTPUT_FILENAME = f"residential_real_estate_outlook_Q1_2025_{timestamp}.md"
OUTPUT_PATH = output_dir / OUTPUT_FILENAME
NODES_PATH = "data/nodes.pkl"

# === Load TextNodes ===
print("📦 Loading text nodes...")
with open(NODES_PATH, "rb") as f:
    all_nodes = pickle.load(f)

# === Build Vector Index ===
print("🔍 Building vector index...")
index = VectorStoreIndex(all_nodes)
query_engine = index.as_query_engine(similarity_top_k=20)  # k is the number of chunks used by the LLM, increase k for more context

# === Cleanup function to remove unwanted metadata and line numbers ===
def clean_response_text(text: str) -> str:
    lines = text.splitlines()
    cleaned = []
    skip_next = False
    for line in lines:
        line = line.strip()
        if skip_next:
            skip_next = False
            continue
        if line.startswith("Context information is below."):
            skip_next = True
            continue
        if any(line.startswith(prefix) for prefix in ["source_url:", "filename:", "title:", "Query:", "Answer:"]):
            continue
        # Remove line numbers (e.g., "10 ", "23 ")
        line = re.sub(r"^\d{1,3}\s+", "", line)
        cleaned.append(line)
    return "\n".join(cleaned).strip()

# === Prompts ===
report_structure = {
    "Overview Table": "Create a concise table showing Price Index, Rental Index, Take-up, Pipeline Supply, and Vacancy Rate. Use realistic estimates if not found.",
    "Overview Summary": "Write a brief 3–4 sentence paragraph summarizing the key highlights of the overview table. Focus on highest or lowest figures.", #probably can get rid of this
    "Macroeconomic Trends": "Summarize macroeconomic factors influencing the real estate market such as household income, HDB price ceilings, foreign investment, and stamp duty impacts.",
    "Sales Market": "Discuss new home and resale market sales, supported by any available figures. Include insight and comparisons.",
    "Sales Launches": "Describe the state of new project launches this quarter and absorption trends.", #include pdfs from the annex
    "Prices": "Analyze price trends in private and public segments. Mention any sharp increases or decreases.",
    "Leasing Markets": "Summarize rental demand, volume, and vacancy changes.",
    "Executive Condominiums": "Comment on the EC market – demand, pricing, and government policies.",
    "Outlook": "Provide a forward-looking statement about real estate market trends, risks, and expectations."
}

# === Generate Report ===
print("✏️ Generating industry outlook report...")
report_lines = [f"# {REPORT_TITLE}\n"]

for section_title, prompt in report_structure.items():
    print(f"\n🧠 Generating: {section_title}")
    response = query_engine.query(prompt)

    raw_text = response.response if hasattr(response, "response") else str(response)
    cleaned_text = clean_response_text(raw_text)

    report_lines.append(f"\n## {section_title}\n")
    report_lines.append(cleaned_text)

# === Save Report ===
with open(OUTPUT_PATH, "w") as f:
    f.write("\n".join(report_lines))

print(f"\n✅ Report saved to: {OUTPUT_PATH}")
