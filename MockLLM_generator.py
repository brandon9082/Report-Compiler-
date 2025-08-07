import os
import pickle
from pathlib import Path
from llama_index.core import Settings, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# === Settings ===
Settings.llm = None
Settings.embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")

# === Paths ===
REPORT_TITLE = "Q1 2025 Residential Real Estate Outlook"
OUTPUT_FILENAME = "residential_real_estate_outlook_Q1_2025.md"
OUTPUT_PATH = Path("output") / OUTPUT_FILENAME
NODES_PATH = "data/nodes.pkl"

# Ensure output folder exists
os.makedirs(OUTPUT_PATH.parent, exist_ok=True)

# === Load TextNodes ===
with open(NODES_PATH, "rb") as f:
    all_nodes = pickle.load(f)

# === Build Vector Index ===
index = VectorStoreIndex(all_nodes)
query_engine = index.as_query_engine()

# === Report structure ===
report_structure = {
    "Overview Table": "Create a concise table showing Price Index, Rental Index, Take-up, Pipeline Supply, and Vacancy Rate. Use realistic estimates if not found.",
    "Overview Summary": "Write a brief 3-4 sentence paragraph summarizing the key highlights of the overview table. Focus on highest or lowest figures.",
    "Macroeconomic Trends": "Summarize macroeconomic factors influencing the real estate market such as household income, HDB price ceilings, foreign investment, and stamp duty impacts.",
    "Sales Market": "Discuss new home and resale market sales, supported by any available figures. Include insight and comparisons.",
    "Sales Launches": "Describe the state of new project launches this quarter and absorption trends.",
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
    report_lines.append(f"\n## {section_title}\n")
    report_lines.append(str(response))

# === Save Report ===
with open(OUTPUT_PATH, "w") as f:
    f.write("\n".join(report_lines))

print(f"\n✅ Report saved to: {OUTPUT_PATH}")