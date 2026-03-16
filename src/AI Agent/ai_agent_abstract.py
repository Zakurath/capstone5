import torch
import ollama
from pathlib import Path
import json
from tqdm import tqdm
import gc

# ----------------------------
# Paths
# ----------------------------
BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_FILE = BASE_DIR / "data/research_papers_abstract/paper_summaries_abstract.json"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# ----------------------------
# LLM setup (GPU)
# ----------------------------

ollama.generate(
    model="llama3",
    prompt="warmup",
    options={"num_predict": 1}
)

# ----------------------------
# Loading research_papers.json for future use
# ----------------------------
file_path = BASE_DIR / "data/research_papers_abstract/research_papers_abstract.json"

research_data = []

with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        research_data.append(json.loads(line))



# ----------------------------
# Main processing
# ----------------------------
existing = []

if OUTPUT_FILE.exists():
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        existing = json.load(f)

existing_files = {d.get("file") for d in existing if d.get("file")}

for paper in tqdm(research_data, desc="Processessing Abstracts"):
    paper_id = paper.get("paperID")

    if paper_id in existing_files:
        continue


    abstract = paper.get("abstract")

    if not abstract:
        continue

    super_classification = ollama.generate(
        model="llama3",
        prompt=f"""Based on the following chunk summaries determine whether the article represents:

    Hypothetical
    Demonstrated
    Active Exploitation

    Return ONLY one of these three options. No extra information and no extra punctuation. This will be going into a variable to be used later for sorting purposes.

    {abstract}
    """,
        options={"num_predict": 200,
        "num_ctx": 1028,
        "num_gpu": 1,
        "num_batch": 512,
        "num_thread": 8,
        "temperature": 0}
    )["response"].strip()

    # Store result
    summary_data = {
        "paperId": paper.get("paperId"),
        "title": paper.get("title"),
        "url": paper.get("url"),
        "classification": super_classification,
        "abstract": paper.get("abstract"),
    }

    existing.append(summary_data)
    existing_files.add(paper.get("paperId"))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)

    # Clear GPU memory
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

print(f"Saved summaries to {OUTPUT_FILE}")