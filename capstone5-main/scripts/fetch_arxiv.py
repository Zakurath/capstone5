import json
import requests
import xml.etree.ElementTree as ET
from pathlib import Path

ARXIV_URL = "http://export.arxiv.org/api/query"
BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_FILE = BASE_DIR / "data" / "arxiv_threat_data.json"

SEARCH_TERMS = [
    "prompt injection",
    "llm security",
    "data poisoning machine learning",
    "model extraction attack",
    "adversarial machine learning",
    "rag security",
    "privacy leakage language models",
    "backdoor attacks deep learning"
]


def guess_category(title: str, abstract: str) -> str:
    text = f"{title} {abstract}".lower()
    if any(word in text for word in ["hypothetical", "future", "challenge", "risk", "misalignment"]):
        return "Hypothetical"
    return "Demonstrated"


def guess_risk(title: str, abstract: str) -> str:
    text = f"{title} {abstract}".lower()
    if any(word in text for word in ["poison", "backdoor", "model extraction", "data leakage", "privacy leakage"]):
        return "High"
    if any(word in text for word in ["adversarial", "evasion", "jailbreak"]):
        return "Medium"
    return "Medium"


def guess_tactic(title: str, abstract: str) -> str:
    text = f"{title} {abstract}".lower()
    if any(word in text for word in ["prompt injection", "adversarial", "jailbreak"]):
        return "Execution"
    if any(word in text for word in ["poison", "reward manipulation"]):
        return "Impact"
    if any(word in text for word in ["extract", "leak", "inference", "privacy"]):
        return "Collection"
    if any(word in text for word in ["backdoor", "rag", "trojan"]):
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
    if "extract" in text or "stealing" in text:
        tags.append("Model Extraction")
    if "backdoor" in text or "trojan" in text:
        tags.append("Backdoor")
    if "privacy" in text or "leak" in text:
        tags.append("Privacy")
    if "rag" in text or "retrieval-augmented" in text:
        tags.append("RAG")
    if "agent" in text:
        tags.append("AI Agents")

    return tags if tags else ["AI Security"]


def guess_mitigations(title: str, abstract: str) -> list[str]:
    text = f"{title} {abstract}".lower()
    mitigations = []

    if "prompt injection" in text or "jailbreak" in text:
        mitigations.extend(["Prompt filtering", "Input validation"])
    if "poison" in text:
        mitigations.extend(["Dataset validation", "Anomaly detection"])
    if "extract" in text or "stealing" in text:
        mitigations.extend(["Rate limiting", "Monitoring"])
    if "backdoor" in text or "trojan" in text:
        mitigations.append("Model auditing")
    if "privacy" in text or "leak" in text:
        mitigations.append("Data minimization")
    if "adversarial" in text:
        mitigations.append("Adversarial training")
    if "rag" in text:
        mitigations.extend(["Source verification", "Context filtering"])

    unique = []
    for item in mitigations:
        if item not in unique:
            unique.append(item)

    return unique if unique else ["Monitoring"]


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

    results = []
    for entry in root.findall("atom:entry", ns):
        title = entry.findtext("atom:title", default="", namespaces=ns).strip().replace("\n", " ")
        abstract = entry.findtext("atom:summary", default="", namespaces=ns).strip().replace("\n", " ")
        published = entry.findtext("atom:published", default="", namespaces=ns).strip()

        paper_url = entry.findtext("atom:id", default="", namespaces=ns).strip()
        arxiv_id = paper_url.split("/")[-1] if paper_url else "unknown"

        item = {
            "title": title,
            "source": "arXiv",
            "abstract": abstract,
            "url": paper_url,   # ✅ IMPORTANT
            "category": guess_category(title, abstract),
            "risk_level": guess_risk(title, abstract),
            "external_id": f"arXiv:{arxiv_id}",
            "tags": guess_tags(title, abstract),
            "tactic": guess_tactic(title, abstract),
            "classification": guess_category(title, abstract),
            "case_studies": [],
            "mitigations": guess_mitigations(title, abstract),
            "last_updated": published[:10] if published else ""
        }

        results.append(item)

    return results


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
    print("AUTO SCRIPT RUNNING...")

    all_items = []

    for term in SEARCH_TERMS:
        try:
            results = fetch_arxiv(term, max_results=8)
            all_items.extend(results)
            print(f"Fetched {len(results)} papers for: {term}")
        except Exception as e:
            print(f"Error fetching '{term}': {e}")

    all_items = dedupe_by_title(all_items)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_items, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(all_items)} entries to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
