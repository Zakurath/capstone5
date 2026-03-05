import json
import os
from datetime import datetime

INPUT_FILE = "data/raw/mitre_atlas.json"
OUTPUT_FILE = "data/mitre_threats.json"

def normalize_mitre(data):
    normalized = []

    for item in data:
        normalized.append({
            "source": "MITRE ATLAS",
            "technique_id": item.get("id"),
            "name": item.get("name"),
            "tactic": item.get("tactic"),
            "description": item.get("description"),
            "maturity": item.get("maturity"),
            "category": item.get("maturity"),  # Hypothetical / Demonstrated
            "reference": item.get("reference"),
            "last_updated": datetime.utcnow().isoformat()
        })

    return normalized


def main():
    if not os.path.exists(INPUT_FILE):
        print("Error: data/raw/mitre_atlas.json not found.")
        return

    # Load raw MITRE ATLAS threat data
    with open(INPUT_FILE, "r") as f:
        mitre_data = json.load(f)

    # Normalize threat fields into a unified schema
    normalized_data = normalize_mitre(mitre_data)

    os.makedirs("data", exist_ok=True)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(normalized_data, f, indent=2)

    print(f"Saved {len(normalized_data)} MITRE threat records to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
