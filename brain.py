import chromadb

DB_DIR = "chroma_db"
COLLECTION = "knowledge_brain"
MAX_DISTANCE = 1.25   # from calibrate.py: worst on-topic 0.934, best off-topic 1.546
N_RESULTS = 4

_client = chromadb.PersistentClient(path=DB_DIR)
_collection = _client.get_collection(COLLECTION)


def retrieve(question, n_results=N_RESULTS):
    """Find the best chunks for a question and decide if the evidence is enough."""
    result = _collection.query(query_texts=[question], n_results=n_results)

    chunks = []
    for doc, meta, dist in zip(
        result["documents"][0], result["metadatas"][0], result["distances"][0]
    ):
        chunks.append({
            "text": doc,
            "distance": round(dist, 3),
            "article_id": meta["article_id"],
            "title": meta["title"],
            "url": meta["url"],
            "image_count": meta["image_count"],
        })

    # Keep only chunks that are close enough to the question
    relevant = [c for c in chunks if c["distance"] <= MAX_DISTANCE]

    # One source entry per article, even if several chunks matched
    sources, seen = [], set()
    for c in relevant:
        if c["article_id"] not in seen:
            seen.add(c["article_id"])
            sources.append({
                "article_id": c["article_id"],
                "title": c["title"],
                "url": c["url"],
            })

    return {
        "question": question,
        "has_evidence": len(relevant) > 0,
        "best_distance": chunks[0]["distance"] if chunks else None,
        "chunks": relevant,
        "sources": sources,
    }