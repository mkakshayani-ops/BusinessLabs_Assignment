import chromadb

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("knowledge_brain")

on_topic = [
    "how do I send a mass email",
    "how do I edit the SEO of my search results page",
    "how do I activate staging mode",
    "how do I set up payment settings",
    "how do members sign up on my site",
    "how do I add a code snippet to every page",
    "how do I forward emails",
    "how do members upgrade or downgrade their plan",
]

off_topic = [
    "what is the capital of France",
    "who won the cricket world cup",
    "give me a pizza recipe",
    "how do I fix my car engine",
    "what is the weather today",
    "explain quantum physics",
]


def best_match(question):
    result = collection.query(query_texts=[question], n_results=1)
    return result["distances"][0][0], result["metadatas"][0][0]["title"]


print("ON-TOPIC questions (should be answered)")
on_distances = []
for q in on_topic:
    dist, title = best_match(q)
    on_distances.append(dist)
    print(f"  {dist:.3f} | {q}  ->  {title[:45]}")

print("\nOFF-TOPIC questions (should be 'I don't know')")
off_distances = []
for q in off_topic:
    dist, title = best_match(q)
    off_distances.append(dist)
    print(f"  {dist:.3f} | {q}  ->  {title[:45]}")

print(f"\nWorst on-topic distance : {max(on_distances):.3f}")
print(f"Best off-topic distance : {min(off_distances):.3f}")