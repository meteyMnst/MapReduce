$ErrorActionPreference = 'Stop'
$aws = "C:\Program Files\Amazon\AWSCLIV2\aws.exe"

$REGION = & $aws configure get region
$ACCOUNT_ID = & $aws sts get-caller-identity --query Account --output text
$SUFFIX = [int][double]::Parse((Get-Date (Get-Date).ToUniversalTime() -UFormat %s))
$BUCKET = "arama-motoru-$SUFFIX"
$ROLE = "AramaMotoruRole"

Write-Output "=== DEĞİŞKENLER ==="
Write-Output "REGION: $REGION"
Write-Output "ACCOUNT_ID: $ACCOUNT_ID"
Write-Output "BUCKET: $BUCKET"
Write-Output "ROLE: $ROLE"

Write-Output "=== ADIM 2: IAM ROLÜ ==="
try {
    & $aws iam create-role --role-name $ROLE --assume-role-policy-document file://arama-motoru/policies/trust.json | Out-Null
    Write-Output "Rol oluşturuldu."
} catch {
    Write-Output "Rol zaten var olabilir."
}
& $aws iam attach-role-policy --role-name $ROLE --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
& $aws iam attach-role-policy --role-name $ROLE --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
$ROLE_ARN = & $aws iam get-role --role-name $ROLE --query 'Role.Arn' --output text

Write-Output "IAM Rolünün aktif olması bekleniyor (15 saniye)..."
Start-Sleep -Seconds 15

Write-Output "=== ADIM 3: S3 BUCKET ==="
& $aws s3 mb s3://$BUCKET --region $REGION
& $aws s3api put-object --bucket $BUCKET --key raw-pages/ | Out-Null
& $aws s3api put-object --bucket $BUCKET --key map-output/ | Out-Null
& $aws s3api put-object --bucket $BUCKET --key final-index/ | Out-Null

Write-Output "=== ADIM 4: MAPPER LAMBDA ==="
Compress-Archive -Path arama-motoru/scripts/mapper.py -DestinationPath arama-motoru/scripts/mapper.zip -Force
& $aws lambda create-function --function-name arama-mapper --runtime python3.11 --handler mapper.lambda_handler --role $ROLE_ARN --zip-file fileb://arama-motoru/scripts/mapper.zip --timeout 60 --memory-size 256 --environment "Variables={BUCKET_NAME=$BUCKET}" --region $REGION | Out-Null
& $aws lambda add-permission --function-name arama-mapper --statement-id S3Trigger --action lambda:InvokeFunction --principal s3.amazonaws.com --source-arn "arn:aws:s3:::$BUCKET" | Out-Null
$MAPPER_ARN = & $aws lambda get-function --function-name arama-mapper --query 'Configuration.FunctionArn' --output text

$notificationConfig = "{`"LambdaFunctionConfigurations`":[{`"LambdaFunctionArn`":`"$MAPPER_ARN`",`"Events`":[`"s3:ObjectCreated:*`"],`"Filter`":{`"KeyFilterRules`":[{`"Name`":`"prefix`",`"Value`":`"raw-pages/`"},{`"Name`":`"suffix`",`"Value`":`".json`"}]}}]}"
& $aws s3api put-bucket-notification-configuration --bucket $BUCKET --notification-configuration $notificationConfig

Write-Output "=== ADIM 5: VERİYİ YÜKLE (MAP OTOMATİK TETİKLENECEK) ==="
& $aws s3 sync arama-motoru/data/s3_ready/raw-pages/ s3://$BUCKET/raw-pages/
Write-Output "Yükleme tamam. 15 saniye bekle ve map-output kontrol et..."
Start-Sleep -Seconds 15
$mapCount = (& $aws s3 ls s3://$BUCKET/map-output/ | Measure-Object).Count
Write-Output "Map Output Dosya Sayısı: $mapCount"

Write-Output "=== ADIM 6: REDUCER LAMBDA ==="
Compress-Archive -Path arama-motoru/scripts/reducer.py -DestinationPath arama-motoru/scripts/reducer.zip -Force
& $aws lambda create-function --function-name arama-reducer --runtime python3.11 --handler reducer.lambda_handler --role $ROLE_ARN --zip-file fileb://arama-motoru/scripts/reducer.zip --timeout 300 --memory-size 512 --environment "Variables={BUCKET_NAME=$BUCKET}" --region $REGION | Out-Null
& $aws lambda invoke --function-name arama-reducer --payload '{}' --region $REGION response.json
Write-Output "Reducer Sonucu:"
Get-Content response.json
Write-Output "Final Index durumu:"
& $aws s3 ls s3://$BUCKET/final-index/

Write-Output "=== ADIM 7: SEARCH LAMBDA + API GATEWAY ==="
Compress-Archive -Path arama-motoru/scripts/search.py -DestinationPath arama-motoru/scripts/search.zip -Force
& $aws lambda create-function --function-name arama-search --runtime python3.11 --handler search.lambda_handler --role $ROLE_ARN --zip-file fileb://arama-motoru/scripts/search.zip --timeout 30 --memory-size 512 --environment "Variables={BUCKET_NAME=$BUCKET}" --region $REGION | Out-Null

$API_ID = & $aws apigateway create-rest-api --name 'AramaMotoruAPI' --query 'id' --output text
$ROOT_ID = & $aws apigateway get-resources --rest-api-id $API_ID --query 'items[0].id' --output text
$SEARCH_RES = & $aws apigateway create-resource --rest-api-id $API_ID --parent-id $ROOT_ID --path-part search --query 'id' --output text

& $aws apigateway put-method --rest-api-id $API_ID --resource-id $SEARCH_RES --http-method GET --authorization-type NONE --request-parameters "method.request.querystring.q=true" | Out-Null
$SEARCH_ARN = & $aws lambda get-function --function-name arama-search --query 'Configuration.FunctionArn' --output text

& $aws apigateway put-integration --rest-api-id $API_ID --resource-id $SEARCH_RES --http-method GET --type AWS_PROXY --integration-http-method POST --uri "arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/${SEARCH_ARN}/invocations" | Out-Null
& $aws lambda add-permission --function-name arama-search --statement-id apigateway-search --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/GET/search" | Out-Null

& $aws apigateway create-deployment --rest-api-id $API_ID --stage-name prod | Out-Null
$ENDPOINT = "https://${API_ID}.execute-api.${REGION}.amazonaws.com/prod/search"
Write-Output "API ENDPOINT: $ENDPOINT"

Write-Output "=== ADIM 8: FRONTEND ==="
$htmlContent = Get-Content arama-motoru/scripts/index.html -Raw
$htmlContent = $htmlContent -replace 'ENDPOINT_URL', $ENDPOINT
Set-Content -Path arama-motoru/scripts/index.html -Value $htmlContent

& $aws s3 cp arama-motoru/scripts/index.html s3://$BUCKET/index.html
& $aws s3 website s3://$BUCKET/ --index-document index.html --error-document index.html

$policy = "{`"Version`":`"2012-10-17`",`"Statement`":[{`"Effect`":`"Allow`",`"Principal`":`"*`",`"Action`":`"s3:GetObject`",`"Resource`":`"arn:aws:s3:::$BUCKET/*`"}]}"
Set-Content -Path arama-motoru/policies/website.json -Value $policy
& $aws s3api put-bucket-policy --bucket $BUCKET --policy file://arama-motoru/policies/website.json

$FRONTEND = "http://${BUCKET}.s3-website.${REGION}.amazonaws.com"
Write-Output "FRONTEND: $FRONTEND"

Write-Output "=== ADIM 10: RAPOR ÇIKTISI ==="
Write-Output "Bucket: $BUCKET"
Write-Output "Mapper: arama-mapper"
Write-Output "Reducer: arama-reducer"
Write-Output "Search: arama-search"
Write-Output "API: $ENDPOINT"
Write-Output "Frontend: $FRONTEND"
Write-Output "Indeks: s3://$BUCKET/final-index/inverted_index.json"
Write-Output "MapReduce mantigi: Mapper (kelime -> doc_id+tf), Reducer (kelime -> [doc_id, tfidf])"
