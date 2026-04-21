import requests
import xml.etree.ElementTree as ET
import json
from pathlib import Path

ARXIV_URL = "http://export.arxiv.org/api/query"
OUTPUT_FILE = Path("capstone5/data/arxiv_threat_data.json")

SEARCH_TERMS = [
    "prompt injection",
    "llm security",
    "data poisoning machine learning",
    "model extraction attack",
    "adversarial machine learning",
    "rag security",
]

def guess_category(title: str, abstract: str) -> str:
    text = f"{title} {abstract}".lower()
    if any(x in text for x in ["survey", "challenge", "risk", "future", "misalignment"]):
        return "Hypothetical"
    return "Demonstrated"

def guess_risk(title: str, abstract: str) -> str:
    text = f"{title} {abstract}".lower()
    if any(x in text for x in ["data leakage", "poisoning", "model extraction", "backdoor"]):
        return "High"
    if any(x in text for x in ["adversarial", "evasion"]):
        return "Medium"
    return "Medium"

def guess_tactic(title: str, abstract: str) -> str:
    text = f"{title} {abstract}".lower()
    if "prompt injection" in text or "adversarial" in text:
        return "Execution"
    if "poison" in text:
        return "Impact"
    if "extract" in text or "leak" in text or "inference" in text:
        return "Collection"
    if "backdoor" in text or "rag" in text:
        return "Persistence"
    return "Impact"

def guess_tags(title: str, abstract: str) -> list[str]:
    text = f"{title} {abstract}".lower()
    tags = []

    if "prompt injection" in text:
        tags.append("Prompt Injection")
    if "llm" in text or "language model" in text:
        tags.append("LLM Security")
    if "poison" in text:
        tags.append("Data Poisoning")
    if "adversarial" in text:
        tags.append("Adversarial ML")
    if "extract" in text:
        tags.append("Model Extraction")
    if "backdoor" in text or "trojan" in text:
        tags.append("Backdoor")
    if "privacy" in text or "leak" in text:
        tags.append("Privacy")
    if "rag" in text or "retrieval-augmented" in text:
        tags.append("RAG")

    return tags if tags else ["AI Security"]

def guess_mitigations(title: str, abstract: str) -> list[str]:
    text = f"{title} {abstract}".lower()
    mitigations = []

    if "prompt injection" in text:
        mitigations.extend(["Prompt filtering", "Input validation"])
    if "poison" in text:
        mitigations.extend(["Dataset validation", "Anomaly detection"])
    if "extract" in text:
        mitigations.extend(["Rate limiting", "Monitoring"])
    if "backdoor" in text:
        mitigations.append("Model auditing")
    if "privacy" in text or "leak" in text:
        mitigations.append("Data minimization")
    if "adversarial" in text:
        mitigations.append("Adversarial training")
    if "rag" in text:
        mitigations.extend(["Source verification", "Context filtering"])

    seen = []
    for m in mitigations:
        if m not in seen:
            seen.append(m)
    return seen if seen else ["Monitoring"]

def fetch_arxiv(query: str, max_results: int = 10) -> list[dict]:
    params = {
        "search_query": f'all:"{query}"',
        "start": 0,
        "max_results": max_results,
    }
    response = requests.get(ARXIV_URL, params=params, timeout=30)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    entries = []
    for entry in root.findall("atom:entry", ns):
        title = entry.findtext("atom:title", default="", namespaces=ns).strip().replace("\n", " ")
        abstract = entry.findtext("atom:summary", default="", namespaces=ns).strip().replace("\n", " ")
        published = entry.findtext("atom:published", default="", namespaces=ns).strip()
        paper_id = entry.findtext("atom:id", default="", namespaces=ns).strip()

        arxiv_id = paper_id.split("/")[-1] if paper_id else "unknown"

        item = {
            "title": title,
            "source": "arXiv",
            "abstract": abstract,
            "category": guess_category(title, abstract),
            "risk_level": guess_risk(title, abstract),
            "external_id": f"arXiv:{arxiv_id}",
            "tags": guess_tags(title, abstract),
            "tactic": guess_tactic(title, abstract),
            "classification": guess_category(title, abstract),
            "case_studies": [],
            "mitigations": guess_mitigations(title, abstract),
            "last_updated": published[:10] if published else "",
        }
        entries.append(item)

    return entries

def dedupe_by_title(items: list[dict]) -> list[dict]:
    seen = set()
    output = []
    for item in items:
        key = item["title"].strip().lower()
        if key not in seen:
            seen.add(key)
            output.append(item)
    return output

def main() -> None:
    all_items = []

    for term in SEARCH_TERMS:
        try:
            results = fetch_arxiv(term, max_results=10)
            all_items.extend(results)
            print(f"Fetched {len(results)} entries for: {term}")
        except Exception as e:
            print(f"Error fetching '{term}': {e}")

    all_items = dedupe_by_title(all_items)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_items, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(all_items)} entries to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
