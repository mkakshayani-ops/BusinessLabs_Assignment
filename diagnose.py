import sys

from brain import retrieve

question = " ".join(sys.argv[1:]) or "How do i send a mass email"
r = retrieve(question)

print("Question:", question)
print("has_evidence:", r["has_evidence"], "| best_distance:", r["best_distance"])
print("Chunks that passed the cutoff:", len(r["chunks"]))
for c in r["chunks"]:
    print(f"  {c['distance']} | {c['title'][:50]} | {c['text'][:90]!r}")