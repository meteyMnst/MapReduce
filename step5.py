import json, os, uuid
os.makedirs("arama-motoru/data/s3_ready/raw-pages", exist_ok=True)
for root, dirs, files in os.walk("arama-motoru/data/extracted"):
    for fname in files:
        if not fname.endswith(".json"): continue
        with open(os.path.join(root, fname), "r", encoding="utf-8") as f:
            for line in f:
                line=line.strip()
                if not line: continue
                article=json.loads(line)
                doc_id=f"doc_{uuid.uuid4().hex[:8]}"
                out={"doc_id":doc_id,"title":article.get("title",""),"url":f"https://tr.wikipedia.org/wiki/{article.get('title','').replace(' ','_')}","content":article.get("text","")}
                with open(f"arama-motoru/data/s3_ready/raw-pages/{doc_id}.json","w",encoding="utf-8") as outf:
                    json.dump(out,outf,ensure_ascii=False)
print(f"Hazirlanan dosya: {len(os.listdir('arama-motoru/data/s3_ready/raw-pages'))}")
