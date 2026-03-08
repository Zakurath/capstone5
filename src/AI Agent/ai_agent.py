import torch
import ollama
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
ollama.generate(
    model="llama3",
    prompt="warmup",
    options={"num_predict": 1}
)

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
# Loading research_papers.json for future use
# ----------------------------
file_path = BASE_DIR / "docs/research_papers.json"

research_data = []

with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        research_data.append(json.loads(line))

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
        with tqdm(total=len(chunks), desc=f"Summarizing {pdf_file.name}", position=1) as pbar:
            for idx, chunk in enumerate(chunks):

                summary = ollama.generate(
                    model="llama3",
                    prompt=f"You are an expert in AI Threats. Summarize the following text chunk:\n\n{chunk}",
                    options={"num_predict": 200}
                )["response"].strip()
                chunk_summaries.append(summary)

                if idx % 5 == 0:
                    save_intermediate(pdf_file, chunk_summaries)

                pbar.update(1)
                gc.collect()

    # Super-summary using last 5 chunks
    super_input = "\n".join(chunk_summaries[-5:])
    super_classification = ollama.generate(
        model="llama3",
        prompt=f"""You are an expert in AI Threats. Based on the following chunk summaries determine whether the article represents:

    Hypothetical
    Demonstrated
    Active Exploitation

    Return ONLY one of these three options. No extra information annd no extra puncuation. This will be going into a variable to be used later for sorting purposes.

    {super_input}
    """,
        options={"num_predict": 20, "temperature": 0}
    )["response"].strip()

    super_summary = ollama.generate(
        model="llama3",
        prompt=f"""You are an expert in AI Threats. Create a concise final summary of the article based on these chunk summaries:

    {super_input}
    """,
        options={"num_predict": 200, "temperature": 0.3}
    )["response"].strip()
    tqdm.write("=" * 80)
    tqdm.write(f"SUPER-Classification for {pdf_file.name}: {super_classification}")
    tqdm.write(f"SUPER-SUMMARY: {super_summary}")
    tqdm.write("=" * 80)

    pdf_title = None

    for search in research_data:
        if search.get("paperId") == pdf_file.stem:
            pdf_title = search.get("title")
            break

    # Store result
    all_summaries.append({
        "file": pdf_file.name,
        "title": pdf_title,
        "classification": super_classification,
        "chunk_summary": "\n".join(chunk_summaries),
        "super_summary": super_summary
    })

    # Save after each PDF
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = []

    existing.append(all_summaries[-1])

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)

    # Clear GPU memory
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

print(f"Saved summaries to {OUTPUT_FILE}")