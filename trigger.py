import boto3, json
lambda_client = boto3.client('lambda', region_name='eu-central-1')
s3 = boto3.client('s3')
bucket = 'arama-motoru-1780602048'

objects = s3.list_objects_v2(Bucket=bucket, Prefix='raw-pages/')['Contents']
for obj in objects:
    key = obj['Key']
    if not key.endswith('.json'): continue
    payload = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": bucket},
                    "object": {"key": key}
                }
            }
        ]
    }
    print(f"Invoking for {key}...")
    res = lambda_client.invoke(
        FunctionName='arama-mapper',
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    print(res['Payload'].read().decode('utf-8'))

print("Invoking reducer...")
res = lambda_client.invoke(
    FunctionName='arama-reducer',
    InvocationType='RequestResponse',
    Payload='{}'
)
print(res['Payload'].read().decode('utf-8'))
