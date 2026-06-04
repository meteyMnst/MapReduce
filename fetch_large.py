import urllib.request
import urllib.parse
import json
import os
import time

os.makedirs("arama-motoru/data/extracted/AA", exist_ok=True)
FILE_PATH = "arama-motoru/data/extracted/AA/wiki_extended.json"
TARGET_COUNT = 1000
FETCHED = 0

print(f"Hedef: {TARGET_COUNT} makale çekilecek...")

# Dosyayı sıfırla
with open(FILE_PATH, "w", encoding="utf-8") as f:
    pass

while FETCHED < TARGET_COUNT:
    try:
        url = "https://tr.wikipedia.org/w/api.php?action=query&format=json&generator=random&grnnamespace=0&grnlimit=20&prop=extracts&explaintext=1"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 MapReduceTest/1.0'})
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        pages = data.get("query", {}).get("pages", {})
        if not pages:
            continue
            
        with open(FILE_PATH, "a", encoding="utf-8") as f:
            for page_id, page_data in pages.items():
                title = page_data.get("title", "")
                extract = page_data.get("extract", "").replace("\n", " ").replace("\r", " ")
                
                # Çok kısa makaleleri atla
                if len(extract) < 100:
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
        
        print(f"Toplam çekilen: {FETCHED} / {TARGET_COUNT}")
        time.sleep(0.5) # Wikipedia API'sini yormamak için ufak bir bekleme
        
    except Exception as e:
        print(f"Hata: {e}")
        time.sleep(2)

print(f"Başarıyla {FETCHED} makale indirildi!")
