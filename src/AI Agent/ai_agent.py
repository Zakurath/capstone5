import torch
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path
import json
from langchain_community.document_loaders import PyPDFLoader
from tqdm import tqdm
import gc

# ----------------------------
# Paths
# ----------------------------
BASE_DIR = Path(__file__).resolve().parents[2]
PDF_FOLDER = BASE_DIR / "docs/data"
OUTPUT_FILE = BASE_DIR / "docs/data/paper_summaries.json"
INTERMEDIATE_FOLDER = BASE_DIR / "docs/data/intermediate"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
INTERMEDIATE_FOLDER.mkdir(parents=True, exist_ok=True)

# ----------------------------
# LLM setup (GPU)
# ----------------------------
llm = OllamaLLM(model="llama3")  # Use GPU

# Chunk-level prompt
chunk_template = """You are an expert in AI Threats. Summarize the following text chunk:

{pdf}
"""
chunk_prompt = ChatPromptTemplate.from_template(chunk_template)
chunk_chain = chunk_prompt | llm

# Super-summary prompt (combine last 5 chunks)
super_template = """You are an expert in AI Threats. Based on the following chunk summaries please start with one of these threat categorizations:
"Hypothetical," "Demonstrated," or "Active Exploitation." Afterwards please provide a one paragraph summary on the paper.

{chunk_summaries}
"""
super_prompt = ChatPromptTemplate.from_template(super_template)
super_chain = super_prompt | llm

# ----------------------------
# Helpers
# ----------------------------
def chunk_text(text, chunk_size=1000, overlap=100):
    words = text.split()
    for i in range(0, len(words), chunk_size - overlap):
        yield " ".join(words[i:i+chunk_size])

def load_intermediate(pdf_file):
    inter_file = INTERMEDIATE_FOLDER / f"{pdf_file.stem}_chunks.json"
    if inter_file.exists():
        with open(inter_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_intermediate(pdf_file, chunk_summaries):
    inter_file = INTERMEDIATE_FOLDER / f"{pdf_file.stem}_chunks.json"
    with open(inter_file, "w", encoding="utf-8") as f:
        json.dump(chunk_summaries, f, indent=2)

# ----------------------------
# Main processing
# ----------------------------
all_summaries = []

pdf_files = [p for p in PDF_FOLDER.glob("*.pdf") if p.suffix.lower() == ".pdf" and p.read_bytes()[:4] == b"%PDF"]

for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
    # Skip PDFs already summarized
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)
            if any(d["file"] == pdf_file.name for d in existing):
                print(f"Skipping {pdf_file.name}, already summarized.")
                continue

    # Load PDF text
    loader = PyPDFLoader(str(pdf_file))
    docs = loader.load()
    text = " ".join([doc.page_content for doc in docs])
    del docs
    gc.collect()

    # Load or split into chunks
    chunk_summaries = load_intermediate(pdf_file)
    if not chunk_summaries:
        chunks = list(chunk_text(text))
        del text
        gc.collect()
        for idx, chunk in enumerate(tqdm(chunks, desc=f"Summarizing {pdf_file.name}", leave=False)):
            summary = chunk_chain.invoke({"pdf": chunk}).strip()
            chunk_summaries.append(summary)
            # Save intermediate every 5 chunks
            if idx % 5 == 0:
                save_intermediate(pdf_file, chunk_summaries)
            gc.collect()

    # Super-summary using last 5 chunks
    super_input = "\n".join(chunk_summaries[-5:])
    super_summary = super_chain.invoke({"chunk_summaries": super_input}).strip()

    print("\n" + "="*80)
    print(f"SUPER-SUMMARY for {pdf_file.name}:\n{super_summary}")
    print("="*80 + "\n")

    # Store result
    all_summaries.append({
        "file": pdf_file.name,
        "chunk_summary": "\n".join(chunk_summaries),
        "super_summary": super_summary
    })

    # Save after each PDF
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)
        all_summaries = existing + [all_summaries[-1]]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_summaries, f, indent=2)

    # Clear GPU memory
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

print(f"Saved summaries to {OUTPUT_FILE}")