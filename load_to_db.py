import glob
import json
import re
from collections import Counter

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

ARTICLES_DIR = "data/articles"
MANIFEST_FILE = "manifest.json"
DB_DIR = "chroma_db"
COLLECTION = "knowledge_brain"

# Splits at paragraphs, then sentences, then words. The overlap keeps context
# between neighbouring chunks.
splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=100)


def article_id_from_url(url):
    match = re.search(r"/articles/(\d+)", url)
    return match.group(1) if match else None


client = chromadb.PersistentClient(path=DB_DIR)
collection = client.get_or_create_collection(COLLECTION)
counts = Counter()

# 1. Load new and changed articles
for path in glob.glob(f"{ARTICLES_DIR}/*.json"):
    with open(path, "r", encoding="utf-8") as f:
        record = json.load(f)

    aid = record["article_id"]
    existing = collection.get(where={"article_id": aid}, limit=1, include=["metadatas"])

    if existing["ids"] and existing["metadatas"][0]["content_hash"] == record["content_hash"]:
        counts["skipped_unchanged"] += 1      # no duplicates
        continue

    if existing["ids"]:
        collection.delete(where={"article_id": aid})   # remove the old version
        counts["updated"] += 1
    else:
        counts["added"] += 1

    chunks = splitter.split_text(record["body_text"])
    collection.add(
        ids=[f"{aid}_{i}" for i in range(len(chunks))],
        documents=[f"{record['title']}\n{c}" for c in chunks],
        metadatas=[{
            "article_id": aid,
            "url": record["url"],
            "title": record["title"],
            "chunk_index": i,
            "content_hash": record["content_hash"],
            "image_count": len(record["images"]),
        } for i in range(len(chunks))],
    )

# 2. Delete chunks of articles that were removed from the help center
with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
    manifest = json.load(f)

for url, info in manifest.items():
    if info["status"] == "removed":
        aid = article_id_from_url(url)
        if aid and collection.get(where={"article_id": aid}, limit=1)["ids"]:
            collection.delete(where={"article_id": aid})
            counts["removed_from_db"] += 1

print("Results:", dict(counts))
print("Total chunks in database:", collection.count())