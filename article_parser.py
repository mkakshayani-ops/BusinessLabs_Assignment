import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "KnowledgeBrainBot/1.0"}


def get_article_id(url):
    """The number after /articles/ in the URL identifies the article."""
    match = re.search(r"/articles/(\d+)", url)
    return match.group(1) if match else None


def nearby_text(img):
    """Text around an image, so we know what the screenshot is about."""
    node = img.parent
    for _ in range(3):
        text = node.get_text(" ", strip=True) if node else ""
        if text:
            return text[:200]
        node = node.find_previous_sibling() if node else None
    return ""


def parse_article(url):
    response = requests.get(url, timeout=15, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")

    article = soup.find("article")
    if article is None:
        raise ValueError("No <article> tag found on this page")

    # Remove things that are not article content
    for tag in article(["script", "style", "nav", "footer"]):
        tag.decompose()

    h1 = soup.find("h1")
    title = h1.get_text(strip=True) if h1 else None

    body_text = article.get_text("\n", strip=True)

    headings = [
        {"level": h.name, "text": h.get_text(strip=True)}
        for h in article.find_all(["h2", "h3", "h4"])
    ]

    images = []
    for position, img in enumerate(article.find_all("img")):
        src = img.get("src")
        if not src or "/hit" in src:  # skip the view-counter tracking pixel
            continue
        images.append({
            "url": urljoin(url, src),
            "alt": img.get("alt"),
            "position": position,
            "nearby_text": nearby_text(img),
        })

    return {
        "article_id": get_article_id(url),
        "url": url,
        "title": title,
        "headings": headings,
        "body_text": body_text,
        "images": images,
        "content_hash": hashlib.sha256(body_text.encode("utf-8")).hexdigest(),
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    # Use a URL given on the command line, or the first one in the manifest
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        with open("manifest.json", "r", encoding="utf-8") as f:
            url = next(iter(json.load(f)))

    result = parse_article(url)

    print("Article ID:", result["article_id"])
    print("Title:", result["title"])
    print("Headings found:", len(result["headings"]))
    print("Body length:", len(result["body_text"]), "characters")
    print("Images found:", len(result["images"]))
    print("Content hash:", result["content_hash"][:16], "...")
    print("\nBody preview:\n", result["body_text"][:500])

    with open("parsed_sample.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print("\nSaved full record to parsed_sample.json")