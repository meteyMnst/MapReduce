$ErrorActionPreference = 'Stop'
$aws = "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
$BUCKET = "arama-motoru-1780602048"
$REGION = "eu-central-1"

Write-Output "1. Eski veriler temizleniyor..."
& $aws s3 rm s3://$BUCKET/raw-pages/ --recursive | Out-Null
& $aws s3 rm s3://$BUCKET/map-output/ --recursive | Out-Null
Remove-Item -Path arama-motoru/data/s3_ready/raw-pages/* -Force -ErrorAction SilentlyContinue

Write-Output "2. Wikipedia API'den makaleler hızlıca indiriliyor..."
python fetch_fast.py

Write-Output "3. İndirilen veriler AWS (MapReduce) için parçalanıyor..."
python step5.py

Write-Output "4. Veriler S3 Bucket'a gönderiliyor (500 Map Lambda tetiklenecek!)..."
& $aws s3 sync arama-motoru/data/s3_ready/raw-pages/ s3://$BUCKET/raw-pages/ | Out-Null
Write-Output "S3 Yüklemesi tamamlandı."

Write-Output "5. AWS Bulutunda tüm verilerin paralel işlenmesi (Map) için bekleniyor (45 saniye)..."
Start-Sleep -Seconds 45

Write-Output "6. Reducer çalıştırılıp devasa endeks oluşturuluyor..."
& $aws lambda invoke --function-name arama-reducer --payload '{}' --region $REGION response_load.json | Out-Null
Get-Content response_load.json

Write-Output "TAMAMLANDI. Frontend adresinden yeni arama yapabilirsiniz."
