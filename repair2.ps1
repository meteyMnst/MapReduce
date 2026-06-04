$ErrorActionPreference = 'Stop'
$aws = "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
$BUCKET = "arama-motoru-1780602048"
$REGION = "eu-central-1"
$MAPPER_ARN = "arn:aws:lambda:eu-central-1:599633425745:function:arama-mapper"

$json = @"
{
    "LambdaFunctionConfigurations": [
        {
            "LambdaFunctionArn": "$MAPPER_ARN",
            "Events": ["s3:ObjectCreated:*"],
            "Filter": {
                "Key": {
                    "FilterRules": [
                        { "Name": "prefix", "Value": "raw-pages/" },
                        { "Name": "suffix", "Value": ".json" }
                    ]
                }
            }
        }
    ]
}
"@
Set-Content -Path arama-motoru/policies/notification.json -Value $json
& $aws s3api put-bucket-notification-configuration --bucket $BUCKET --notification-configuration file://arama-motoru/policies/notification.json

Write-Output "Verileri S3'e tekrar yükleyip Map tetiklemesi yapılıyor..."
& $aws s3 rm s3://$BUCKET/raw-pages/ --recursive
& $aws s3 sync arama-motoru/data/s3_ready/raw-pages/ s3://$BUCKET/raw-pages/
Start-Sleep -Seconds 15

Write-Output "REDUCER TEKRAR ÇALIŞTIRILIYOR..."
& $aws lambda invoke --function-name arama-reducer --payload '{}' --region $REGION response.json | Out-Null
Get-Content response.json

Write-Output "API Testi Yapılıyor..."
$ENDPOINT = "https://to468ckmi4.execute-api.eu-central-1.amazonaws.com/prod/search"
try {
    $curlOut = Invoke-RestMethod -Uri "$ENDPOINT?q=bulut+bilişim" -Method Get
    Write-Output ($curlOut | ConvertTo-Json -Depth 5)
} catch {
    Write-Output "API Testi basarisiz oldu: $_"
}
