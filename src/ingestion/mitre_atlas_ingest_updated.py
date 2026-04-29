from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import yaml

BASE_DIR = Path(__file__).resolve().parents[2]

# Use the cleaner source file already in your repo
INPUT_FILE_TECHNIQUES = BASE_DIR / "data" / "atlas_techniques.json"
OUTPUT_FILE_TECHNIQUES = BASE_DIR / "data" / "atlas_techniques_normalized.json"

INPUT_FILE_CASE_STUDIES = BASE_DIR / "data" / "atlas_case_studies.json"
OUTPUT_FILE_CASE_STUDIES = BASE_DIR / "data" / "atlas_case_studies_normalized.json"


def normalize_category(maturity: str | None) -> str:
    if not maturity:
        return "Demonstrated"

    mapping = {
        "feasible": "Hypothetical",
        "Demonstrated": "Demonstrated",
        "realized": "Active Exploitation",
        "Active Exploitation": "Active Exploitation",
        "exercise" : "Demonstrated",
        "incident" : "Active Exploitation",
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

        parent_technique = item.get("subtechnique-of", None)

        tags = []
        if tactic:
            tags.append(tactic)
        if name:
            tags.append(name)

        normalized.append({
            "title": name,
            "source": "MITRE ATLAS",
            "abstract": description,
            "classification": normalize_category(maturity),
            "risk_level": None,
            "url": f"https://atlas.mitre.org/techniques/{technique_id}",
            "id": technique_id,
            "tags": tags,
            "tactic": tactic,
            "type": "technique",
            "subtechniques": parent_technique,
            "last_updated": datetime.now(timezone.utc).isoformat()
        })

    return normalized

def normalize_mitre_case_studies(data: list[dict]) -> list[dict]:
    normalized = []

    for item in data:
        technique_id = item.get("id")
        name = item.get("name")
        description = item.get("summary")

        maturity = item.get("case-study-type")


        procedure = item.get("procedure")

        techniques_used = []




        normalized.append({
            "title": name,
            "source": "MITRE ATLAS",
            "abstract": description,
            "classification": normalize_category(maturity),
            "url": f"https://atlas.mitre.org/studies/{technique_id}",
            "id": technique_id,
            "techniques": item.get("procedure"),
            "type": "case study",
            "last_updated": datetime.now(timezone.utc).isoformat()
        })

    return normalized

def assign_mitigation(techniques, mitigations):
    mitigation_map = {}

    for mitigation in mitigations:
        for t in mitigation.get("techniques", []):
            tech_id = t["id"]

            mitigation_map.setdefault(tech_id, []).append({
                "mitigation_id": mitigation["id"],
                "mitigation_name": mitigation["name"],
                "use": t.get("use")
            })

    for tech in techniques:
        tech_id = tech.get("id")
        if tech_id in mitigation_map:
            tech["mitigations"] = mitigation_map[tech_id]


def main() -> None:
    # This is to pull the yaml file
    BASE_DIR = Path(__file__).resolve().parents[2]

    ATLAS_LOC = BASE_DIR / "data/atlas-data/dist/ATLAS.yaml"
    ATLAS_TECHNIQUES = BASE_DIR / "data/atlas_techniques.json"
    ATLAS_MITIGATIONS = BASE_DIR / "data/atlas_mitigations.json"
    ATLAS_CASE_STUDIES = BASE_DIR / "data/atlas_case_studies.json"

    with open(ATLAS_LOC) as f:
        # Parse YAML
        data = yaml.safe_load(f)

        first_matrix = data['matrices'][0]
        techniques = first_matrix['techniques']
        mitigations = first_matrix['mitigations']
        case_studies = data.get('case-studies', [])

        with open(ATLAS_TECHNIQUES, 'w') as json_file:
            # indent=4 makes the output human-readable (pretty-print)
            json.dump(techniques, json_file, indent=4, default=str)

        with open(ATLAS_MITIGATIONS, 'w') as json_file:
            json.dump(mitigations, json_file, indent=4, default=str)

        with open(ATLAS_CASE_STUDIES, 'w') as json_file:
            # indent=4 makes the output human-readable (pretty-print)
            json.dump(case_studies, json_file, indent=4, default=str)

    # Processes the MITRE ATLAS techniques
    if not INPUT_FILE_TECHNIQUES.exists():
        print(f"Error: {INPUT_FILE_TECHNIQUES} not found.")
        return

    with open(INPUT_FILE_TECHNIQUES, "r", encoding="utf-8") as f:
        mitre_data = json.load(f)

    normalized_data = normalize_mitre(mitre_data)

    assign_mitigation(normalized_data, mitigations)

    OUTPUT_FILE_TECHNIQUES.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE_TECHNIQUES, "w", encoding="utf-8") as f:
        json.dump(normalized_data, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(normalized_data)} MITRE ATLAS techniques to {OUTPUT_FILE_TECHNIQUES}")

    #Processes the MITRE ATLAS case studies
    if not INPUT_FILE_CASE_STUDIES.exists():
        print(f"Error: {INPUT_FILE_CASE_STUDIES} not found.")
        return

    with open(INPUT_FILE_CASE_STUDIES, "r", encoding="utf-8") as f:
        mitre_data = json.load(f)

    normalized_data = normalize_mitre_case_studies(mitre_data)

    OUTPUT_FILE_TECHNIQUES.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE_CASE_STUDIES, "w", encoding="utf-8") as f:
        json.dump(normalized_data, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(normalized_data)} MITRE ATLAS case studies to {OUTPUT_FILE_CASE_STUDIES}")


if __name__ == "__main__":
    main()
