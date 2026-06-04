import json, boto3, re, urllib.parse, os
from collections import Counter
s3 = boto3.client('s3')
BUCKET = os.environ['BUCKET_NAME']
STOP_WORDS = set(["bir","ve","bu","da","de","için","ile","çok","daha","olan","olarak","gibi","sonra","ise","her","bütün","kadar","the","and","for","are","but","not","you","all","can","had","was","one","our","out","day","get","has","him","his","how","man","new","now","old","see","two","way","who","boy","did","its","let","put","say","she","too","use","yok","var","ki","mi","ama","ya","hem","hiç","bile","şey","o","a","is","in","it","to","of","with","on","that","this","at","by","an","be","or","from","have","they","will"])

def tokenize(text):
    if not text: return []
    words = re.findall(r'\b[a-zA-ZçğıöşüÇĞİÖŞÜ]{3,}\b', str(text).lower())
    cleaned = []
    for w in words:
        w = w.replace("ı","i").replace("ş","s").replace("ğ","g").replace("ü","u").replace("ö","o").replace("ç","c")
        if w not in STOP_WORDS: cleaned.append(w)
    return cleaned

def lambda_handler(event, context):
    try:
        record = event['Records'][0]['s3']
        bucket = record['bucket']['name']
        key = urllib.parse.unquote_plus(record['object']['key'])
        if not key.startswith('raw-pages/') or not key.endswith('.json'):
            return {'statusCode':200, 'body':'Atlandi'}
        obj = s3.get_object(Bucket=bucket, Key=key)
        article = json.loads(obj['Body'].read().decode('utf-8'))
        doc_id = article['doc_id']
        words = tokenize(article.get('title','') + " " + article.get('content',''))
        tf = dict(Counter(words))
        result = {"doc_id":doc_id, "title":article.get('title',''), "url":article.get('url',''), "word_count":len(words), "tf":tf}
        out_key = f"map-output/{doc_id}_map.json"
        s3.put_object(Bucket=bucket, Key=out_key, Body=json.dumps(result, ensure_ascii=False), ContentType='application/json')
        print(f"MAPPED: {doc_id} -> {len(tf)} kelime")
        return {'statusCode':200, 'body':f'Mapped {doc_id}'}
    except Exception as e:
        print(f"HATA: {e}")
        raise
