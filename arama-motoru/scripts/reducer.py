import json, boto3, os, math
from collections import defaultdict
s3 = boto3.client('s3')
BUCKET = os.environ['BUCKET_NAME']

def lambda_handler(event, context):
    try:
        resp = s3.list_objects_v2(Bucket=BUCKET, Prefix='map-output/')
        if 'Contents' not in resp: return {'statusCode':404, 'body':'map-output bos'}
        files = [o for o in resp['Contents'] if o['Key'].endswith('.json')]
        total_docs = len(files)
        print(f"Toplam {total_docs} map dosyasi")
        inverted = defaultdict(dict)
        doc_meta = {}
        for obj in files:
            key = obj['Key']
            try:
                body = s3.get_object(Bucket=BUCKET, Key=key)['Body'].read().decode('utf-8')
                data = json.loads(body)
                doc_id = data['doc_id']
                doc_meta[doc_id] = {"title":data.get('title',''), "url":data.get('url',''), "word_count":data.get('word_count',0)}
                for word, tf_val in data.get('tf',{}).items():
                    inverted[word][doc_id] = tf_val
            except Exception as e:
                print(f"HATA okuma ({key}): {e}")
                continue
        final_index = {}
        for word, postings in inverted.items():
            df = len(postings)
            idf = math.log(total_docs / df) if df > 0 else 0
            final_index[word] = {"df":df, "idf":round(idf,4), "postings":[]}
            for doc_id, tf in postings.items():
                tfidf = tf * idf
                final_index[word]["postings"].append({"doc_id":doc_id, "tf":tf, "tfidf":round(tfidf,4)})
            final_index[word]["postings"].sort(key=lambda x: x['tfidf'], reverse=True)
        output = {"metadata":{"total_docs":total_docs,"total_terms":len(final_index)}, "doc_meta":doc_meta, "index":final_index}
        s3.put_object(Bucket=BUCKET, Key='final-index/inverted_index.json', Body=json.dumps(output, ensure_ascii=False), ContentType='application/json')
        print(f"INDEKS TAMAMLANDI: {len(final_index)} terim, {total_docs} dokuman")
        return {'statusCode':200, 'body':f'Indeksleme tamam: {len(final_index)} terim'}
    except Exception as e:
        print(f"KRITIK HATA: {e}")
        raise
