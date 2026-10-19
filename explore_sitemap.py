import requests
from bs4 import BeautifulSoup
from collections import Counter

URL = "https://support.brilliantdirectories.com/support/sitemap.xml"

response = requests.get(URL, timeout=15, headers={"User-Agent": "KnowledgeBrainBot/1.0"})
soup = BeautifulSoup(response.text, "xml")
entries = soup.find_all("url")
print("Total URLs:", len(entries))

kinds = Counter()
examples = {}
dates = Counter()
seen = set()
duplicates = 0

for entry in entries:
    link = entry.find("loc").text.strip()

    # Skip duplicates (the guide asks for this)
    if link in seen:
        duplicates += 1
        continue
    seen.add(link)

    # Decide what type of page this is, based on the web address
    if "/solutions/articles/" in link:
        kind = "article"
    elif "/solutions/folders/" in link:
        kind = "folder"
    else:
        kind = "other"

    kinds[kind] += 1
    examples.setdefault(kind, []).append(link)

    lastmod = entry.find("lastmod")
    if lastmod:
        dates[lastmod.text[:10]] += 1

print("Duplicates removed:", duplicates)
print("\nPage types:", dict(kinds))

print("\nExamples:")
for kind, links in examples.items():
    print(kind)
    for l in links[:2]:
        print("   ", l)

print("\nDifferent last-changed dates:", len(dates))
print("Most common dates:", dates.most_common(5))