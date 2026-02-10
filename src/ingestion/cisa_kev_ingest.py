
import requests
import json
from datetime import datetime

KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
OUTPUT_FILE = "data/active_exploitation.json"

def fetch_kev():
    response = requests.get(KEV_URL, timeout=10)
    response.raise_for_status()
    return response.json()

def normalize_kev(kev_data):
    normalized = []
    for item in kev_data.get("vulnerabilities", []):
        normalized.append({
            "source": "CISA KEV",
            "cve_id": item.get("cveID"),
            "vendor": item.get("vendorProject"),
            "product": item.get("product"),
            "description": item.get("shortDescription"),
            "date_added": item.get("dateAdded"),
            "due_date": item.get("dueDate"),
            "category": "Active Exploitation",
            "last_updated": datetime.utcnow().isoformat()
        })
    return normalized

def main():
    kev_data = fetch_kev()
    normalized_data = normalize_kev(kev_data)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(normalized_data, f, indent=2)

    print(f"Saved {len(normalized_data)} active exploitation records")

if __name__ == "__main__":
    main()
