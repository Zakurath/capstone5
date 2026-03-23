

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

CISA_FILE = BASE_DIR / "data" / "cisa_kev_data.json"
ATLAS_FILE = BASE_DIR / "data" / "atlas_data.json"
OUTPUT_FILE = BASE_DIR / "data" / "all_threats.json"


def load_json(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    all_records = []

    if CISA_FILE.exists():
        all_records.extend(load_json(CISA_FILE))

    if ATLAS_FILE.exists():
        all_records.extend(load_json(ATLAS_FILE))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(all_records)} total records to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
    