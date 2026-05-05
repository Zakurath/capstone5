import json
from pathlib import Path
import feedparser

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_FILE = BASE_DIR / "data" / "the_hacker_news_data.json"

FEED_URL = "https://thehackernews.com/feeds/posts/default"

AI_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "llm",
    "large language model", "chatgpt", "openai", "deepfake",
    "prompt injection", "model poisoning", "adversarial ai"
]

CYBER_KEYWORDS = [
    "cybersecurity", "security", "vulnerability", "exploit",
    "attack", "malware", "ransomware", "breach", "threat",
    "zero-day", "phishing", "backdoor", "data leak"
]


def is_ai_security_related(title, summary):
    text = f"{title} {summary}".lower()

    has_ai = any(keyword in text for keyword in AI_KEYWORDS)
    has_cyber = any(keyword in text for keyword in CYBER_KEYWORDS)

    return has_ai and has_cyber


def classify_article(title, summary):
    text = f"{title} {summary}".lower()

    if any(k in text for k in ["exploited in the wild", "active exploitation", "zero-day", "actively exploited"]):
        return "Active Exploitation"

    if any(k in text for k in ["malware", "ransomware", "breach", "attack", "backdoor", "exploit"]):
        return "Demonstrated"

    return "Hypothetical"


def main():
    print("Fetching The Hacker News feed...")

    feed = feedparser.parse(FEED_URL)
    records = []

    for entry in feed.entries:
        title = entry.get("title", "Untitled")
        summary = entry.get("summary", "")
        link = entry.get("link", "")

        if not is_ai_security_related(title, summary):
            continue

        records.append({
            "id": f"THN-{len(records) + 1}",
            "title": title,
            "source": "The Hacker News",
            "url": link,
            "classification": classify_article(title, summary),
            "abstract": summary if summary else f"The Hacker News article: {title}",
            "type": "news"
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(records)} The Hacker News records to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
