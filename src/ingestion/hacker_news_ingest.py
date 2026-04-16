
import json
import time
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_FILE = BASE_DIR / "data" / "hacker_news_data.json"

TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
NEW_STORIES_URL = "https://hacker-news.firebaseio.com/v0/newstories.json"
ITEM_URL_TEMPLATE = "https://hacker-news.firebaseio.com/v0/item/{}.json"

KEYWORDS = [
    "ai",
    "artificial intelligence",
    "machine learning",
    "llm",
    "large language model",
    "prompt injection",
    "model poisoning",
    "adversarial",
    "deepfake",
    "cybersecurity",
    "security",
    "vulnerability",
    "exploit",
    "attack"
]


def is_ai_related(title: str, text: str = "") -> bool:
    combined = f"{title} {text}".lower()
    return any(keyword in combined for keyword in KEYWORDS)


def fetch_json(url: str):
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.json()


def normalize_story(item: dict) -> dict:
    title = item.get("title", "Untitled")
    text = item.get("text", "") or ""
    url = item.get("url", f"https://news.ycombinator.com/item?id={item.get('id', '')}")

    return {
        "id": f"HN-{item.get('id', '')}",
        "title": title,
        "source": "Hacker News",
        "url": url,
        "classification": "Hypothetical",
        "abstract": text if text else f"Hacker News story: {title}",
        "type": "story",
        "score": item.get("score", 0),
        "author": item.get("by", "unknown"),
        "time": item.get("time", 0)
    }


def main():
    print("Fetching Hacker News stories...")

    try:
        top_story_ids = fetch_json(TOP_STORIES_URL)
        new_story_ids = fetch_json(NEW_STORIES_URL)
    except Exception as e:
        print(f"Error fetching Hacker News story lists: {e}")
        return

    # Combine and remove duplicates while keeping order
    combined_ids = []
    seen = set()

    for story_id in top_story_ids[:100] + new_story_ids[:100]:
        if story_id not in seen:
            combined_ids.append(story_id)
            seen.add(story_id)

    hn_records = []

    for story_id in combined_ids:
        try:
            item = fetch_json(ITEM_URL_TEMPLATE.format(story_id))

            if not item:
                continue

            if item.get("type") != "story":
                continue

            title = item.get("title", "")
            text = item.get("text", "") or ""

            if not is_ai_related(title, text):
                continue

            hn_records.append(normalize_story(item))
            time.sleep(0.05)

        except Exception as e:
            print(f"Error fetching story {story_id}: {e}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(hn_records, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(hn_records)} Hacker News records to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()