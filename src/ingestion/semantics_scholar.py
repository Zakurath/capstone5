import requests
import json
from pathlib import Path

# Find project root
BASE_DIR = Path(__file__).resolve().parents[2]

save_path = BASE_DIR / "data/research_papers"
save_path.mkdir(parents=True, exist_ok=True)

file_path = save_path / "research_papers.json"

# just for testing purposes so it doesn't take forever to do.
MAX_RESULTS = 2000

# API endpoint
url = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"

query_params = {
    "query": "attacks against ai systems",
    "fields": "title,url,openAccessPdf",
    "year": "2023-",
}

response = requests.get(url, params=query_params).json()

print(f"Estimated {response.get('total', 0)} documents available")

retrieved = 0

with open(file_path, "w", encoding="utf-8") as file:

    while True:

        if "data" in response:

            for paper in response["data"]:

                if retrieved >= MAX_RESULTS:
                    break

                file.write(json.dumps(paper) + "\n")
                retrieved += 1

            print(f"Retrieved {retrieved} papers...")

        if retrieved >= MAX_RESULTS:
            break

        if "token" not in response:
            break

        query_params["token"] = response["token"]
        response = requests.get(url, params=query_params).json()

print(f"Done! Retrieved {retrieved} papers total")
print(f"Saved to {file_path}")


pdf_folder = BASE_DIR / "data/research_papers/pdfs"

pdf_folder.mkdir(parents=True, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0"
}

count = 0

with open(file_path, "r", encoding="utf-8") as f:

    for line in f:
        paper = json.loads(line)

        pdf_info = paper.get("openAccessPdf")

        if not pdf_info:
            continue

        pdf_url = pdf_info.get("url")

        if not pdf_url:
            continue
        paper_id = paper["paperId"]
        filename = pdf_folder / f"{paper_id}.pdf"

        try:
            r = requests.get(pdf_url, headers=headers, stream=True)

            if r.status_code == 200:
                with open(filename, "wb") as file:
                    for chunk in r.iter_content(8192):
                        file.write(chunk)

                print("Downloaded:", filename)
                count += 1

        except Exception as e:
            print("Failed:", pdf_url, e)

print("Total PDFs downloaded:", count)