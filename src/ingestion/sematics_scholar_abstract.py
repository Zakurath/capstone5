import requests
import json
import time
from pathlib import Path

# -----------------------------
# File Locations
# -----------------------------
BASE_DIR = Path(__file__).resolve().parents[2]

save_path = BASE_DIR / "data/research_papers_abstract"
save_path.mkdir(parents=True, exist_ok=True)

file_path_papers = save_path / "research_papers_abstract.json"
file_path_ids = save_path / "paperID.json"

MAX_RESULTS = 2000
MAX_TRIES = 5
current_tries = 0

# -----------------------------
# API endpoints
# -----------------------------
url = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
batch_url = "https://api.semanticscholar.org/graph/v1/paper/batch"

query_params = {
    "query": "attacks against ai systems",
    "fields": "paperId,title,url",
    "year": "2023-",
}

resp = requests.get(url, params=query_params)

if resp.status_code != 200:
    raise RuntimeError(resp.text)

response = resp.json()

print(f"Estimated {response.get('total', 0)} documents available")

retrieved = 0

# -----------------------------
# Load existing IDs
# -----------------------------
existing_ids = set()

if file_path_ids.exists():
    with open(file_path_ids, "r", encoding="utf-8") as f:
        for line in f:
            existing_ids.add(line.strip())

print(f"Loaded {len(existing_ids)} existing papers")

# -----------------------------
# Primary Loop
# -----------------------------
with open(file_path_papers, "a", encoding="utf-8") as paper_file, \
     open(file_path_ids, "a", encoding="utf-8") as id_file:

    while True:

        if "data" not in response:
            break

        paper_ids = [paper["paperId"] for paper in response["data"]]

        # batch in groups of 100
        for i in range(0, len(paper_ids), 100):
            if current_tries == MAX_TRIES:
                break

            if retrieved >= MAX_RESULTS:
                break

            chunk = paper_ids[i:i+100]

            time.sleep(3)

            batch_resp = requests.post(
                batch_url,
                params={"fields": "paperId,title,url,abstract"},
                json={"ids": chunk}
            )

            if batch_resp.status_code == 429:
                print("Rate limited, sleeping 30s...")
                time.sleep(30)
                current_tries += 1
                continue

            papers = batch_resp.json()

            for paper in papers:

                if retrieved >= MAX_RESULTS:
                    break

                paper_id = paper["paperId"]

                if paper_id in existing_ids:
                    continue

                paper_file.write(json.dumps(paper) + "\n")
                id_file.write(paper_id + "\n")

                existing_ids.add(paper_id)
                retrieved += 1

        if retrieved >= MAX_RESULTS:
            break

        if "token" not in response:
            break

        query_params["token"] = response["token"]

        resp = requests.get(url, params=query_params)

        if resp.status_code != 200:
            print("Pagination error:", resp.text)
            break

        response = resp.json()

print(f"Done! Retrieved {retrieved} new papers")
print(f"Saved to {file_path_papers}")