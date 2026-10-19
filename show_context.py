import sys

from brain import retrieve

question = " ".join(sys.argv[1:])
r = retrieve(question)

print("Question:", question)
print("has_evidence:", r["has_evidence"], "| best_distance:", r["best_distance"], "\n")
for c in r["chunks"]:
    print(f"--- {c['distance']} | {c['title']}")
    print(c["text"][:700])
    print()