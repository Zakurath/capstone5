import ollama
from pathlib import Path
import json

from tqdm import tqdm

def update_abstracts():
    # ----------------------------
    # Paths
    # ----------------------------
    base_dir = Path(__file__).resolve().parents[2]
    output_file = base_dir / "data/research_papers_abstract/paper_summaries_abstract2.json"
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
    
        Hypothetical - being shown to work in research or academic settings,
        Demonstrated - being shown to be effective in red team exercise or demonstration on a realistic AI-enabled system, 
        Active Exploitation - being shown as used by a threat actor in a real-world incident target an AI-enabled systems.
    
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


def update_cisa_kev():
    # ----------------------------
    # Paths
    # ----------------------------
    base_dir = Path(__file__).resolve().parents[2]
    output_file = base_dir / "data/cisa_kev_processed.json"
    processed_cisa_kev = base_dir / "data/cisa_kev_processed.txt"
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
    file_path = base_dir / "data/cisa_kev_data.json"

    cisa_data = []

    with open(file_path, 'r', encoding="utf-8") as file:
        cisa_data = json.load(file)

    # ----------------------------
    # Main processing
    # ----------------------------
    keyword = ["machine learning", "artificial intelligence", "llm", "large language model",
                "neural network", "deep learning", "model inference", "model training",
                "pytorch", "tensorflow", "keras", "jax", "onnx",
                "langchain", "llamaindex", "langflow", "autogen", "crewai",
                "vector database", "embedding", "rag", "retrieval augmented",
                "pinecone", "weaviate", "milvus", "chroma", "qdrant",
                "inference", "model api", "model endpoint", "model serving",
                "huggingface", "vllm", "ollama", "triton",
                "prompt injection", "data poisoning", "model extraction", "model inversion",
                "adversarial", "jailbreak", "token flooding", "ai agent"]
    existing = []
    processed = []
    to_process = []

    if output_file.exists():
        with open(output_file, "r", encoding="utf-8") as f:
            existing = json.load(f)

    if processed_cisa_kev.exists():
        with open(processed_cisa_kev, "r", encoding="utf-8") as f:
            processed = json.load(f)

    for search in cisa_data:
        title = search.get("title")
        summary = search.get("summary")

        if not summary:
            continue
        if not title:
            continue

        if any(word in summary.lower() for word in keyword):
            to_process.append(search)
            continue

        if title in processed:
            continue

    for paper in tqdm(to_process, desc="Processing Cisa Kev entries"):

        summary = paper.get("summary")
        title = paper.get("title")

        classification = ollama.generate(
            model="llama3",
            prompt=f""" 
            
                            
                You are a cybersecurity analyst specializing in AI and machine learning threats.
                
                Determine whether this CISA Known Exploited Vulnerability (KEV) impacts AI, machine learning, or LLM-based systems.
                
                Classify TRUE if the vulnerability affects ANY of the following:
                
                AI / ML Systems:
                - Machine learning frameworks (PyTorch, TensorFlow, Keras, JAX, ONNX)
                - LLM infrastructure (LangChain, LlamaIndex, agents, RAG pipelines)
                - Model training pipelines
                - Model inference services
                - AI APIs or AI microservices
                
                AI Infrastructure:
                - GPU compute infrastructure used for AI
                - Kubernetes clusters hosting AI workloads
                - ML notebooks (Jupyter, MLflow, Kubeflow)
                - Vector databases (Pinecone, Weaviate, Chroma, Milvus)
                - AI orchestration tools or workflow automation used for AI
                
                AI Attack Categories:
                - Prompt injection
                - Data poisoning
                - Model extraction
                - Model inversion
                - Adversarial ML
                - AI supply chain compromise
                - AI agent abuse
                - LLM plugin or tool exploitation
                
                Also classify TRUE if:
                - The vulnerability affects software commonly used in AI pipelines
                - The vulnerability enables compromise of AI models, training data, or inference services
                
                Classify FALSE only if:
                - The vulnerability is clearly unrelated to AI or ML systems
                
                Vulnerability:
                Title: {title}
                Description: {summary}
                
                Think carefully before answering.
                
                Return ONLY one word:
                true
                false
        """,
            options={"num_predict": 20,
                     "num_ctx": 1028,
                     "num_gpu": 1,
                     "num_batch": 512,
                     "num_thread": 8,
                     "temperature": 0}
        )["response"].strip()

        classification = classification.strip()

        processed.append(title)

        classification = classification.lower()

        is_ai_related = "true" in classification

        if not is_ai_related:
            continue

        # Store result
        url = f"https://www.cve.org/CVERecord?id={title}"

        summary_data = {
            "title": title,
             "source": "Cisa Kev",
              "url": url,
              "classification": paper.get("category"),
             "abstract": summary,
            }

        existing.append(summary_data)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)

    with open(processed_cisa_kev, "w", encoding="utf-8") as f:
        json.dump(processed, f, indent=2)

if __name__ == "__main__":
    update_cisa_kev()