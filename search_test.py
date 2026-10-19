import sys

import chromadb

question = " ".join(sys.argv[1:]) or "Can I send a mass email campaign?"

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("knowledge_brain")
results = collection.query(query_texts=[question], n_results=3)

print("Question:", question)
for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
    print(f"\nDistance: {dist:.3f}  (lower = closer match)")
    print("Title:", meta["title"])
    print("URL:", meta["url"])
    print("Text:", doc[:200].replace("\n", " "))