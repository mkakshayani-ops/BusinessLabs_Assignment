import json
import os
import requests
from bs4 import BeautifulSoup

SITEMAP_URL = "https://support.brilliantdirectories.com/support/sitemap.xml"
MANIFEST_FILE = "manifest.json"


def fetch_sitemap_articles():
    """Download the sitemap and return {article_url: lastmod}."""
    response = requests.get(SITEMAP_URL, timeout=15, headers={"User-Agent": "KnowledgeBrainBot/1.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "xml")

    articles = {}
    for entry in soup.find_all("url"):
        link = entry.find("loc").text.strip()
        if "/solutions/articles/" not in link:
            continue  # skip folders and other pages
        lastmod = entry.find("lastmod")
        articles[link] = lastmod.text.strip() if lastmod else None
    return articles


def load_manifest():
    """Load the saved manifest, or start empty if this is the first run."""
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_manifest(manifest):
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


todays = fetch_sitemap_articles()
manifest = load_manifest()
counts = {"new": 0, "changed": 0, "unchanged": 0, "removed": 0}

# Compare today's sitemap with the saved manifest
for url, lastmod in todays.items():
    if url not in manifest:
        manifest[url] = {"lastmod": lastmod, "status": "new", "attempts": 0, "content_hash": None}
        counts["new"] += 1
    elif manifest[url]["lastmod"] != lastmod:
        manifest[url]["lastmod"] = lastmod
        manifest[url]["status"] = "changed"
        counts["changed"] += 1
    else:
        counts["unchanged"] += 1

# Anything saved earlier but missing from today's sitemap was removed
for url in manifest:
    if url not in todays and manifest[url]["status"] != "removed":
        manifest[url]["status"] = "removed"
        counts["removed"] += 1

save_manifest(manifest)
print("Articles in sitemap today:", len(todays))
print("Results:", counts)