$ErrorActionPreference = 'Stop'
$aws = "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
$BUCKET = "arama-motoru-1780602048"
$REGION = "eu-central-1"
$MAPPER_ARN = "arn:aws:lambda:eu-central-1:599633425745:function:arama-mapper"

Write-Output "HATA 1 DÜZELTİLİYOR: S3 Notification Configuration"
$json = @"
{
    "LambdaFunctionConfigurations": [
        {
            "LambdaFunctionArn": "$MAPPER_ARN",
            "Events": ["s3:ObjectCreated:*"],
            "Filter": {
                "KeyFilterRules": [
                    { "Name": "prefix", "Value": "raw-pages/" },
                    { "Name": "suffix", "Value": ".json" }
                ]
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

Write-Output "HATA 2 DÜZELTİLİYOR: S3 Public Access Block & Policy"
& $aws s3api put-public-access-block --bucket $BUCKET --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false
Start-Sleep -Seconds 5
& $aws s3api put-bucket-policy --bucket $BUCKET --policy file://arama-motoru/policies/website.json

Write-Output "REDUCER TEKRAR ÇALIŞTIRILIYOR..."
& $aws lambda invoke --function-name arama-reducer --payload '{}' --region $REGION response.json
Get-Content response.json

Write-Output "TAMAMLANDI."
