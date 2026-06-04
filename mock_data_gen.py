import os, json
os.makedirs("arama-motoru/data/extracted/AA", exist_ok=True)
articles = [
    {"id": "1", "revid": "1", "url": "https://tr.wikipedia.org/wiki/Bulut", "title": "Bulut bilişim", "text": "Bulut bilişim, bilgisayar kaynaklarının internet üzerinden sağlanmasıdır. Çok önemlidir."},
    {"id": "2", "revid": "2", "url": "https://tr.wikipedia.org/wiki/Tarih", "title": "Tarih", "text": "Tarih, geçmişte yaşamış insan topluluklarının faaliyetlerini yer ve zaman göstererek inceleyen bilim dalıdır."},
    {"id": "3", "revid": "3", "url": "https://tr.wikipedia.org/wiki/AWS", "title": "Amazon Web Services", "text": "AWS bir bulut bilişim platformudur."},
    {"id": "4", "revid": "4", "url": "https://tr.wikipedia.org/wiki/Antik", "title": "Antik Çağ", "text": "Antik Çağ, insanlık tarihinin en önemli dönemlerinden biridir. Tarih boyunca bir çok uygarlık kurulmuştur."}
]
with open("arama-motoru/data/extracted/AA/wiki_00.json", "w", encoding="utf-8") as f:
    for a in articles:
        f.write(json.dumps(a, ensure_ascii=False) + "\n")
