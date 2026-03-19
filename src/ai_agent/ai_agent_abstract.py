import torch
import ollama
from pathlib import Path
import json
from tqdm import tqdm
import gc

def update_abstracts():
    # ----------------------------
    # Paths
    # ----------------------------
    base_dir = Path(__file__).resolve().parents[2]
    output_file = base_dir / "data/research_papers_abstract/paper_summaries_abstract.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

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
    file_path = base_dir / "data/research_papers_abstract/research_papers_abstract.json"

    research_data = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            research_data.append(json.loads(line))

    # ----------------------------
    # Main processing
    # ----------------------------
    existing = []
    to_process = []

    if output_file.exists():
        with open(output_file, "r", encoding="utf-8") as f:
            existing = json.load(f)

    existing_files = {d.get("paperId") for d in existing if d.get("paperId")}

    for search in research_data:
        paper_id = search.get("paperId")
        abstract = search.get("abstract")

        if not abstract:
            continue
        if not paper_id:
            continue

        if paper_id in existing_files:
            continue
        else:
            to_process.append(search)

    for paper in tqdm(to_process, desc="Processing Abstracts"):

        abstract = paper.get("abstract")
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

        valid_labels = {"Hypothetical", "Demonstrated", "Active Exploitation"}
        super_classification = super_classification.strip()

        if super_classification not in valid_labels:
            super_classification = "Unknown"

        # Store result
        summary_data = {
            "paperId": paper.get("paperId"),
            "title": paper.get("title"),
            "source": "Semantic Scholar", 
            "url": paper.get("url"),
            "classification": super_classification,
            "abstract": paper.get("abstract"),
        }

        existing.append(summary_data)
        existing_files.add(paper.get("paperId"))


    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)

if __name__ == "__main__":
    update_abstracts()