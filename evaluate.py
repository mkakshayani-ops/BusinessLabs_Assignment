import json
import time

from chatbot import ask

# kind: "answer" = the help center should answer it, "refuse" = it should say "I don't know"
TESTS = [
    # Questions in the brief's own examples
    {"q": "how do refunds work", "kind": "answer"},
    {"q": "how are cancellations handled from the member's side", "kind": "answer"},
    # How-to questions in natural wording
    {"q": "how do I turn on staging mode", "kind": "answer"},
    {"q": "how do I manually approve new member signups", "kind": "answer"},
    {"q": "can I send a mass email campaign", "kind": "answer"},
    {"q": "how do I set up payment settings", "kind": "answer"},
    {"q": "how do I log in as a member", "kind": "answer"},
    {"q": "how do I edit the SEO of the member search results page", "kind": "answer"},
    {"q": "how do I forward emails to another address", "kind": "answer"},
    {"q": "how do I add a code snippet to every page", "kind": "answer"},
    # Questions that should be refused
    {"q": "what is the capital of France", "kind": "refuse"},
    {"q": "give me a pizza recipe", "kind": "refuse"},
    {"q": "who is the president of the United States", "kind": "refuse"},
    {"q": "help", "kind": "refuse"},
    {"q": "can you write me a python script", "kind": "refuse"},
    {"q": "what is the price of bitcoin today", "kind": "refuse"},
]

results = []
for t in TESTS:
    start = time.time()
    r = ask(t["q"])
    seconds = time.time() - start
    correct = (r["answered"] and t["kind"] == "answer") or (not r["answered"] and t["kind"] == "refuse")
    results.append({
        "question": t["q"], "expected": t["kind"], "answered": r["answered"],
        "correct": correct, "seconds": round(seconds, 1),
        "sources": [s["title"] for s in r["sources"]],
    })
    mark = "PASS" if correct else "FAIL"
    print(f"{mark} | expected={t['kind']:6} | answered={str(r['answered']):5} | {seconds:4.1f}s | {t['q']}")

passed = sum(r["correct"] for r in results)
print(f"\nScore: {passed}/{len(results)}")
print("Average time per question:", round(sum(r["seconds"] for r in results) / len(results), 1), "seconds")

with open("evaluation_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("Saved evaluation_results.json")