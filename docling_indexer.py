import os
import warnings
from urllib.parse import urlparse
from pathlib import Path
import pickle

# === Force CPU usage and disable MPS/CUDA for compatibility ===
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TRANSFORMERS_NO_MPS"] = "1"

import torch
torch.backends.mps.is_available = lambda: False
torch.backends.mps.is_built = lambda: False
warnings.filterwarnings("ignore", message="'pin_memory' argument is set as true but not supported on MPS now")

# === Imports ===
from sentence_transformers import SentenceTransformer
from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from llama_index.core.schema import TextNode

# === Config ===
DATA_OUTPUT = "data/nodes.pkl"
os.makedirs("data", exist_ok=True)

# === Load Inputs: HTML URLs + Local PDFs ===
with open("html_sources.txt", "r") as f:
    url_inputs = [line.strip() for line in f if line.strip() and not line.startswith("#")]

pdf_folder = Path("sources")
pdf_inputs = []
if pdf_folder.exists() and any(pdf_folder.glob("*.pdf")):
    pdf_inputs = [f.as_uri() for f in pdf_folder.glob("*.pdf")]
    print(f"📄 Found {len(pdf_inputs)} PDF(s) in sources/ folder.")
else:
    print("📂 No PDFs found in sources/ folder — skipping.")

# Combine all sources into one list
all_inputs = url_inputs + pdf_inputs

# === Initialize converter, chunker, embedder ===
converter = DocumentConverter()
chunker = HybridChunker(merge_peers=True)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# === Process Documents ===
all_nodes = []

for url in all_inputs:
    try:
        print(f"📥 Processing: {url}")
        result = converter.convert(url)
        chunks = list(chunker.chunk(dl_doc=result.document))

        fallback_filename = urlparse(url).netloc + urlparse(url).path
        title = getattr(result.document, "title", None) or fallback_filename
        texts = [chunk.text[:2000] for chunk in chunks]
        vectors = embedder.encode(texts)



        for i, chunk in enumerate(chunks):
            node = TextNode(
                text=texts[i],
                embedding=vectors[i],
                metadata={
                    "source_url": url,
                    "filename": fallback_filename,
                    "title": title
                }
            )
            all_nodes.append(node)

    except Exception as e:
        print(f"❌ Failed to process {url}: {e}")

# === Save to disk ===
with open(DATA_OUTPUT, "wb") as f:
    pickle.dump(all_nodes, f)

# === Summary ===
print(f"\n✅ Created {len(all_nodes)} TextNodes from {len(all_inputs)} sources")
print(f"🔗 Web sources: {len(url_inputs)}")
print(f"📄 Local PDFs: {len(pdf_inputs)}")


# === Preview first 5 chunks ===
preview_count = min(5, len(all_nodes))
print(f"\n🔍 Showing first {preview_count} chunk previews:\n" + "=" * 40)

for i in range(preview_count):
    node = all_nodes[i]
    print(f"\n--- Chunk {i + 1} ---")
    print(f"Title: {node.metadata.get('title')}")
    print(f"Filename: {node.metadata.get('filename')}")
    print(f"Source URL: {node.metadata.get('source_url')}")
    print(f"Text Preview: {node.text[:300]}...")
