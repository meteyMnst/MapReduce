import json, boto3, os, re
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
        params = event.get('queryStringParameters') or {}
        query = params.get('q', '')
        if not query:
            return {'statusCode':400, 'headers':{'Content-Type':'application/json','Access-Control-Allow-Origin':'*'}, 'body':json.dumps({'error':'q parametresi gerekli'})}
        idx_obj = s3.get_object(Bucket=BUCKET, Key='final-index/inverted_index.json')
        idx_data = json.loads(idx_obj['Body'].read().decode('utf-8'))
        index = idx_data['index']
        doc_meta = idx_data['doc_meta']
        query_words = tokenize(query)
        if not query_words:
            return {'statusCode':200, 'headers':{'Content-Type':'application/json','Access-Control-Allow-Origin':'*'}, 'body':json.dumps({'results':[],'query':query})}
        scores = {}
        for word in query_words:
            if word not in index: continue
            for posting in index[word]['postings']:
                doc_id = posting['doc_id']
                scores[doc_id] = scores.get(doc_id, 0) + posting['tfidf']
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        results = []
        for doc_id, score in sorted_results[:20]:
            meta = doc_meta.get(doc_id, {})
            results.append({"doc_id":doc_id, "title":meta.get('title','Bilinmiyor'), "url":meta.get('url',''), "score":round(score,4)})
        return {'statusCode':200, 'headers':{'Content-Type':'application/json','Access-Control-Allow-Origin':'*'}, 'body':json.dumps({'query':query,'query_terms':query_words,'total_found':len(sorted_results),'results':results}, ensure_ascii=False)}
    except Exception as e:
        return {'statusCode':500, 'headers':{'Content-Type':'application/json','Access-Control-Allow-Origin':'*'}, 'body':json.dumps({'error':str(e)})}
