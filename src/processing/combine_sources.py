import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

HACKER_NEWS_FILE = BASE_DIR / "data" / "the_hacker_news_data.json"
CISA_FILE = BASE_DIR / "data" / "cisa_kev_processed.json"
ATLAS_TECHNIQUES_FILE = BASE_DIR / "data" / "atlas_techniques_normalized.json"
ATLAS_CASE_STUDIES_FILE = BASE_DIR / "data" / "atlas_case_studies_normalized.json"
PAPERS_FILE = BASE_DIR / "data" / "research_papers_abstract" / "paper_summaries_abstract2.json"
FAKE_FILE = BASE_DIR / "data" / "fake_threats.json"
ARXIV_FILE = BASE_DIR / "data" / "arxiv_threat_data.json"

OUTPUT_FILE = BASE_DIR / "data" / "all_threats.json"


def load_json(path: Path) -> list[dict]:
    if not path.exists():
        print(f"Warning: File not found -> {path}")
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            print(f"Warning: Expected a list in {path}, but got {type(data).__name__}")
            return []
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return []


def main() -> None:
    all_records = []

    # Load processed CISA KEV
    cisa_records = load_json(CISA_FILE)
    all_records.extend(cisa_records)
    print(f"Loaded {len(cisa_records)} CISA KEV records.")

    # Load MITRE ATLAS techniques
    atlas_techniques = load_json(ATLAS_TECHNIQUES_FILE)
    all_records.extend(atlas_techniques)
    print(f"Loaded {len(atlas_techniques)} MITRE ATLAS technique records.")

    # Load MITRE ATLAS case studies
    atlas_case_studies = load_json(ATLAS_CASE_STUDIES_FILE)
    all_records.extend(atlas_case_studies)
    print(f"Loaded {len(atlas_case_studies)} MITRE ATLAS case study records.")

    # Load Semantic Scholar papers
    paper_records = load_json(PAPERS_FILE)
    all_records.extend(paper_records)
    print(f"Loaded {len(paper_records)} Semantic Scholar paper records.")

    # Load Hacker News stories
    hacker_news_records = load_json(HACKER_NEWS_FILE)
    all_records.extend(hacker_news_records)
    print(f"Loaded {len(hacker_news_records)} Hacker News records.")

    # Load arXiv reserach papers
    arXiv_records = load_json(ARXIV_FILE)
    all_records.extend(arXiv_records)
    print(f"Loaded {len(arXiv_records)} arXiv research papers.")

    # Load fake data for poisoning demonstration
    fake_records = load_json(FAKE_FILE)
    all_records.extend(fake_records)
    print(f"Loaded {len(fake_records)} fake threat records.")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(all_records)} total records to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
