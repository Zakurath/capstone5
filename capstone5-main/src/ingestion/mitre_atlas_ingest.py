from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

# Use the cleaner source file already in your repo
INPUT_FILE = BASE_DIR / "data" / "atlas_threats.json"
OUTPUT_FILE = BASE_DIR / "data" / "atlas_data.json"


def normalize_category(maturity: str | None) -> str:
    if not maturity:
        return "Demonstrated"

    mapping = {
        "Hypothetical": "Hypothetical",
        "Demonstrated": "Demonstrated",
        "Realized": "Active Exploitation",
        "Active Exploitation": "Active Exploitation"
    }
    return mapping.get(maturity, "Demonstrated")


def normalize_mitre(data: list[dict]) -> list[dict]:
    normalized = []

    for item in data:
        technique_id = item.get("id")
        name = item.get("name")
        description = item.get("description")
        tactic = item.get("tactic")
        maturity = item.get("maturity")
        reference = item.get("reference")

        tags = []
        if tactic:
            tags.append(tactic)
        if name:
            tags.append(name)

        normalized.append({
            "title": name,
            "source": "MITRE ATLAS",
            "abstract": description,
            "category": normalize_category(maturity),
            "risk_level": None,
            "url": reference,
            "external_id": technique_id,
            "tags": tags,
            "tactic": tactic,
            "classification": maturity,
            "case_studies": item.get("case_studies", []),
            "mitigations": item.get("mitigations", []),
            "last_updated": datetime.now(timezone.utc).isoformat()
        })

    return normalized


def main() -> None:
    if not INPUT_FILE.exists():
        print(f"Error: {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        mitre_data = json.load(f)

    normalized_data = normalize_mitre(mitre_data)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(normalized_data, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(normalized_data)} MITRE ATLAS records to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
    