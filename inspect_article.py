import json
import requests
from bs4 import BeautifulSoup

# Take the first article URL from our manifest
with open("manifest.json", "r", encoding="utf-8") as f:
    manifest = json.load(f)

url = next(iter(manifest))
print("Fetching:", url)

response = requests.get(url, timeout=15, headers={"User-Agent": "KnowledgeBrainBot/1.0"})
print("Status code:", response.status_code)

# Save the raw page so we can open and study it
with open("sample_article.html", "w", encoding="utf-8") as f:
    f.write(response.text)

soup = BeautifulSoup(response.text, "lxml")

print("\nPage <title>:", soup.title.get_text(strip=True) if soup.title else None)
h1 = soup.find("h1")
print("First <h1>:", h1.get_text(strip=True) if h1 else None)

# Try likely containers for the main article text
for selector in ["article", "main", ".article-body", ".article-content", "#article-body"]:
    element = soup.select_one(selector)
    if element:
        text = element.get_text(" ", strip=True)
        print(f"\n[{selector}] found, {len(text)} characters")
        print("   Preview:", text[:200])
    else:
        print(f"\n[{selector}] not found")

# List the images on the page
images = soup.find_all("img")
print("\nTotal image tags on page:", len(images))
for img in images[:8]:
    print("  ", img.get("src"), "| alt:", img.get("alt"))