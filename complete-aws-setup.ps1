# AWS Complete Setup Script
# This script completes the AWS Bedrock configuration

Write-Host "=== AWS Bedrock Complete Setup ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Get AWS Account ID
Write-Host "[1/3] Getting AWS Account ID..." -ForegroundColor Yellow
$accountInfo = aws sts get-caller-identity | ConvertFrom-Json
$accountId = $accountInfo.Account
Write-Host "Account ID: $accountId" -ForegroundColor Green
Write-Host ""

# Step 2: Construct MediaConvert Role ARN
$roleArn = "arn:aws:iam::${accountId}:role/MediaConvertRole"
Write-Host "[2/3] MediaConvert Role ARN:" -ForegroundColor Yellow  
Write-Host "  $roleArn" -ForegroundColor Cyan
Write-Host ""

# Step 3: Update .env file
Write-Host "[3/3] Updating .env file..." -ForegroundColor Yellow
$envPath = ".\.env"
$envContent = Get-Content $envPath -Raw

# Replace the placeholder
$envContent = $envContent -replace "MEDIACONVERT_ROLE_ARN=PLACEHOLDER_UPDATE_WITH_YOUR_ROLE_ARN", "MEDIACONVERT_ROLE_ARN=$roleArn"

# Write back to file
$envContent | Set-Content $envPath -NoNewline
Write-Host "Updated .env with MediaConvert Role ARN" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "=== Configuration Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "AWS Resources Created:" -ForegroundColor Cyan
Write-Host "  S3 Bucket: ai-video-generator-bucket-2026" -ForegroundColor White
Write-Host "  IAM Role: MediaConvertRole" -ForegroundColor White
Write-Host "  Role ARN: $roleArn" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Restart backend: python app.py" -ForegroundColor White
Write-Host "  2. Generate video with provider=amazon_bedrock" -ForegroundColor White
Write-Host "  3. Video composition will now use AWS MediaConvert" -ForegroundColor White
Write-Host ""
