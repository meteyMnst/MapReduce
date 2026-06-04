import urllib.request
import urllib.parse
import json
import os
import sys

os.makedirs("arama-motoru/data/extracted/AA", exist_ok=True)
FILE_PATH = "arama-motoru/data/extracted/AA/wiki_extended.json"
TARGET_COUNT = 500
FETCHED = 0

print(f"Hedef: {TARGET_COUNT} makale Wikipedia API'sinden çekilecek...")
sys.stdout.flush()

with open(FILE_PATH, "w", encoding="utf-8") as f:
    pass

url_base = "https://tr.wikipedia.org/w/api.php?action=query&format=json&generator=random&grnnamespace=0&grnlimit=50&prop=extracts&exintro=1&explaintext=1"
continue_param = ""

while FETCHED < TARGET_COUNT:
    try:
        url = url_base + continue_param
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        pages = data.get("query", {}).get("pages", {})
        with open(FILE_PATH, "a", encoding="utf-8") as f:
            for page_id, page_data in pages.items():
                title = page_data.get("title", "")
                extract = page_data.get("extract", "").replace("\n", " ").replace("\r", " ")
                
                if len(extract) < 20:
                    continue
                    
                article = {
                    "id": page_id,
                    "revid": page_id,
                    "url": f"https://tr.wikipedia.org/wiki/{urllib.parse.quote(title)}",
                    "title": title,
                    "text": extract
                }
                f.write(json.dumps(article, ensure_ascii=False) + "\n")
                FETCHED += 1
                if FETCHED >= TARGET_COUNT:
                    break
        
        print(f"Çekilen: {FETCHED} / {TARGET_COUNT}")
        sys.stdout.flush()
        
        if "continue" in data:
            continue_param = ""
            for k, v in data["continue"].items():
                continue_param += f"&{k}={urllib.parse.quote(str(v))}"
        else:
            continue_param = ""
            
    except Exception as e:
        print(f"Hata: {e}")
        sys.stdout.flush()
