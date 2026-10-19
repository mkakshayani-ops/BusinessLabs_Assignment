import requests
from bs4 import BeautifulSoup

URL = "https://support.brilliantdirectories.com/support/sitemap.xml"

# 1. Download the sitemap file
response = requests.get(URL, timeout=15, headers={"User-Agent": "KnowledgeBrainBot/1.0"})
print("Status code:", response.status_code)

# 2. Read the XML
soup = BeautifulSoup(response.text, "xml")

# 3. Find all page entries
entries = soup.find_all("url")
print("Total pages found:", len(entries))

# 4. Show the first 10
for entry in entries[:10]:
    link = entry.find("loc").text
    lastmod = entry.find("lastmod")
    print(link, "|", lastmod.text if lastmod else "no date")

# 5. If there are no pages, this may be an index of other sitemaps
if len(entries) == 0:
    sitemaps = soup.find_all("sitemap")
    print("Sitemaps inside this file:", len(sitemaps))
    for s in sitemaps[:10]:
        print(s.find("loc").text)