


import requests
import json
from datetime import datetime, timezone
from pathlib import Path

KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_FILE = BASE_DIR / "data" / "cisa_kev_data.json"


def fetch_kev() -> dict:
    response = requests.get(KEV_URL, timeout=30)
    response.raise_for_status()
    return response.json()


def normalize_kev(kev_data: dict) -> list[dict]:
    normalized = []

    for item in kev_data.get("vulnerabilities", []):
        cve_id = item.get("cveID")
        vendor = item.get("vendorProject")
        product = item.get("product")
        description = item.get("shortDescription")

        normalized.append({
            "title": cve_id,
            "source": "CISA KEV",
            "summary": description,
            "category": "Active Exploitation",
            "risk_level": "High",
            "url": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
            "external_id": cve_id,
            "tags": [tag for tag in [vendor, product] if tag],
            "vendor": vendor,
            "product": product,
            "date_added": item.get("dateAdded"),
            "due_date": item.get("dueDate"),
            "last_updated": datetime.now(timezone.utc).isoformat()
        })

    return normalized


def main() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    kev_data = fetch_kev()
    normalized_data = normalize_kev(kev_data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(normalized_data, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(normalized_data)} CISA KEV records to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
    