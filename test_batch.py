import json
import time
from article_parser import parse_article

DELAY_SECONDS = 1   # polite pause between requests
HOW_MANY = 20

with open("manifest.json", "r", encoding="utf-8") as f:
    manifest = json.load(f)

urls = list(manifest.keys())[:HOW_MANY]

results = []
failures = []

for number, url in enumerate(urls, start=1):
    try:
        record = parse_article(url)
        results.append(record)
        title = (record["title"] or "")[:45]
        print(
            f"{number:2}/{HOW_MANY} OK     "
            f"images={len(record['images'])}  "
            f"headings={len(record['headings'])}  "
            f"chars={len(record['body_text'])}  | {title}"
        )
    except Exception as error:
        # One bad page must not stop the whole job
        failures.append({"url": url, "error": str(error)})
        print(f"{number:2}/{HOW_MANY} FAILED | {url[-45:]} | {error}")

    time.sleep(DELAY_SECONDS)

print("\nSucceeded:", len(results), "| Failed:", len(failures))

with_images = [r for r in results if r["images"]]
print("Articles with images:", len(with_images))
if with_images:
    example = with_images[0]
    print("\nExample article with images:", example["title"])
    print("URL:", example["url"])
    for img in example["images"][:3]:
        print("   image:", img["url"])
        print("   alt:  ", img["alt"])
        print("   near: ", img["nearby_text"][:100])

with open("test_batch.json", "w", encoding="utf-8") as f:
    json.dump({"results": results, "failures": failures}, f, indent=2, ensure_ascii=False)
print("\nSaved to test_batch.json")