from brain import retrieve

questions = [
    "how do I send a mass email",                        # should have evidence
    "how do I activate staging mode",                    # should have evidence
    "what is the capital of France",                     # should have none
    "how do I reset my password",                        # tricky
    "how are refunds and cancellations handled",         # in the brief, may not be crawled yet
    "help",                                              # vague
]

for q in questions:
    r = retrieve(q)
    print(f"\nQ: {q}")
    print(f"   has_evidence={r['has_evidence']}  best_distance={r['best_distance']}")
    for s in r["sources"][:3]:
        print("   source:", s["title"][:55])