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
PDF_FOLDER = BASE_DIR / "data/research_papers/pdfs"
OUTPUT_FILE = BASE_DIR / "data/research_papers/paper_summaries_pdf.json"
INTERMEDIATE_FOLDER = BASE_DIR / "data/research_papers/intermediate"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
INTERMEDIATE_FOLDER.mkdir(parents=True, exist_ok=True)

# ----------------------------
# LLM setup (GPU)
# ----------------------------

ollama.generate(
    model="mistral",
    prompt="warmup",
    options={"num_predict": 1}
)

# ----------------------------
# Helpers
# ----------------------------
def chunk_text(text, chunk_size=900, overlap=100):
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
file_path = BASE_DIR / "data/research_papers/research_papers.json"

research_data = []

with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        research_data.append(json.loads(line))



# ----------------------------
# Main processing
# ----------------------------
all_summaries = []

pdf_files = [p for p in PDF_FOLDER.glob("*.pdf") if p.suffix.lower() == ".pdf" and p.read_bytes()[:4] == b"%PDF"]

existing = []

if OUTPUT_FILE.exists():
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        existing = json.load(f)

# Fast lookup set
existing_files = {d["file"] for d in existing}

for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
    # Skip PDFs already summarized
    if pdf_file.name in existing_files:
        print(f"Skipping {pdf_file.name}, already summarized.")
        continue

    # Load PDF text
    loader = PyPDFLoader(str(pdf_file))
    docs = loader.load()
    text = " ".join([doc.page_content for doc in docs])
    del docs

    # Load or split into chunks
    chunk_summaries = load_intermediate(pdf_file)
    if not chunk_summaries:
        chunks = list(chunk_text(text))
        del text
        with tqdm(total=len(chunks), desc=f"Summarizing {pdf_file.name}", position=1) as pbar:
            for idx, chunk in enumerate(chunks):

                summary = ollama.generate(
                    model="llama3",
                    prompt=f"Summarize the following AI threat research text. Focus on the attack mechanism and impact.:\n\n{chunk}",
                    options={"num_predict": 120,
                             "num_ctx": 2048,
                             "num_gpu": 1,
                             "num_thread": 8
                             }
                )["response"].strip()
                chunk_summaries.append(summary)

                if idx % 5 == 0:
                    save_intermediate(pdf_file, chunk_summaries)

                pbar.update(1)

    # Super-summary using last 5 chunks
    super_input = "\n".join(chunk_summaries[-5:])
    super_classification = ollama.generate(
        model="llama3",
        prompt=f"""Based on the following chunk summaries determine whether the article represents:

    Hypothetical
    Demonstrated
    Active Exploitation

    Return ONLY one of these three options. No extra information and no extra punctuation. This will be going into a variable to be used later for sorting purposes.

    {super_input}
    """,
        options={"num_predict": 200,
        "num_ctx": 2048,
        "num_gpu": 1,
        "num_batch": 512,
        "num_thread": 8,
        "temperature": 0}
    )["response"].strip()

    super_input = "\n".join(chunk_summaries)

    super_summary = ollama.generate(
        model="llama3",
        prompt=f"""Create a concise professional summary (1–2 paragraphs) of this AI security research paper using the summaries below.

    Focus on:
    - attack method
    - technical mechanism
    - real-world impact

    Summaries:
    {super_input}
    """,
        options={
            "num_predict": 320,
            "num_ctx": 2048,
            "num_gpu": 1,
            "num_thread": 8,
            "num_batch": 512,
            "temperature": 0.3
        }
    )["response"].strip()

    tqdm.write("=" * 80)
    tqdm.write(f"SUPER-Classification for {pdf_file.name}: {super_classification}")
    tqdm.write(f"SUPER-SUMMARY: {super_summary}")
    tqdm.write("=" * 80)

    pdf_title = None
    pdf_url = None

    for search in research_data:
        if search.get("paperId") == pdf_file.stem:
            pdf_title = search.get("title")
            pdf_url = search.get("url")
            break

    # Store result
    summary_data = {
        "file": pdf_file.name,
        "title": pdf_title,
        "url": pdf_url,
        "classification": super_classification,
        "chunk_summary": "\n".join(chunk_summaries),
        "super_summary": super_summary
    }

    existing.append(summary_data)
    existing_files.add(pdf_file.name)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)

    # Clear GPU memory
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

print(f"Saved summaries to {OUTPUT_FILE}")