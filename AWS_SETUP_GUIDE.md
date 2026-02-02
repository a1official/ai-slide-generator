# 🌩️ Complete AWS Bedrock Setup Guide

**Goal:** Configure all 7 agents to use AWS services (100% cloud-based pipeline)

**Current Status:** 4/7 agents on cloud (57%)  
**Target Status:** 6/7 agents on cloud (86%) - Ingestion always stays local

---

## 📋 Prerequisites

✅ You already have:
- AWS Account with credentials
- AWS Access Key ID: `AKIA_REDACTED`
- AWS Region: `us-east-1`

---

## 🚀 Step-by-Step AWS Configuration

### **Step 1: Create S3 Bucket** (Required for Avatar + Video Composition)

Run this command to create an S3 bucket:

```bash
aws s3 mb s3://ai-video-generator-bucket --region us-east-1
```

Or use the AWS Console:
1. Go to: https://s3.console.aws.amazon.com/s3/
2. Click "Create bucket"
3. Bucket name: `ai-video-generator-bucket` (must be globally unique)
4. Region: `US East (N. Virginia) us-east-1`
5. Leave other settings as default
6. Click "Create bucket"

**Note the bucket name**, you'll need it for `.env`

---

### **Step 2: Create IAM Role for MediaConvert** (Required for Video Composition)

#### Option A: Using AWS CLI

```bash
# 1. Create trust policy file
cat > mediaconvert-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Service": "mediaconvert.amazonaws.com"
    },
    "Action": "sts:AssumeRole"
  }]
}
EOF

# 2. Create the role
aws iam create-role \
  --role-name MediaConvertRole \
  --assume-role-policy-document file://mediaconvert-trust-policy.json

# 3. Attach S3 access policy
aws iam attach-role-policy \
  --role-name MediaConvertRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# 4. Attach MediaConvert policy
aws iam attach-role-policy \
  --role-name MediaConvertRole \
  --policy-arn arn:aws:iam::aws:policy/AWSElementalMediaConvertFullAccess

# 5. Get the role ARN (SAVE THIS!)
aws iam get-role --role-name MediaConvertRole --query 'Role.Arn' --output text
```

#### Option B: Using AWS Console

1. Go to: https://console.aws.amazon.com/iam/home#/roles
2. Click "Create role"
3. Select "AWS service" → "MediaConvert"
4. Click "Next"
5. Attach policies:
   - `AmazonS3FullAccess`
   - `AWSElementalMediaConvertFullAccess`
6. Click "Next"
7. Role name: `MediaConvertRole`
8. Click "Create role"
9. Click on the created role and **copy the ARN** (looks like: `arn:aws:iam::123456789012:role/MediaConvertRole`)

---

### **Step 3: (Optional) Create SageMaker Endpoint for Avatar** 

**Note:** This is complex and expensive. For now, you can skip this and use local Wav2Lip for avatars.

If you want cloud-based avatar generation, you'll need to:
1. Deploy Wav2Lip model to SageMaker
2. Create an inference endpoint
3. Configure endpoint name in `.env`

**Recommended:** Skip this for now, let avatar run locally.

---

### **Step 4: Update .env File**

Add these lines to your `.env`:

```env
# S3 Bucket (for avatar assets and video composition)
S3_BUCKET_NAME=ai-video-generator-bucket

# MediaConvert Role ARN (replace with your actual ARN from Step 2)
MEDIACONVERT_ROLE_ARN=arn:aws:iam::YOUR_ACCOUNT_ID:role/MediaConvertRole

# Amazon Polly Voice (optional, defaults to Joanna)
POLLY_VOICE=Joanna

# SageMaker Endpoint for Avatar (optional, skip for now)
# SAGEMAKER_ENDPOINT_NAME=wav2lip-endpoint
```

---

## 🎯 **Quick Setup Commands**

Run these commands in PowerShell to set everything up:

```powershell
# 1. Create S3 bucket
aws s3 mb s3://ai-video-generator-bucket --region us-east-1

# 2. Create MediaConvert trust policy
@'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "mediaconvert.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
'@ | Out-File -FilePath mediaconvert-trust-policy.json -Encoding utf8

# 3. Create IAM role
aws iam create-role --role-name MediaConvertRole --assume-role-policy-document file://mediaconvert-trust-policy.json

# 4. Attach policies
aws iam attach-role-policy --role-name MediaConvertRole --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
aws iam attach-role-policy --role-name MediaConvertRole --policy-arn arn:aws:iam::aws:policy/AWSElementalMediaConvertFullAccess

# 5. Get role ARN (copy this!)
aws iam get-role --role-name MediaConvertRole --query 'Role.Arn' --output text

# 6. Enable Bedrock models (if not already enabled)
# This must be done via AWS Console: https://console.aws.amazon.com/bedrock/
# Enable: Amazon Nova Pro, Amazon Titan Image Generator v2, Amazon Nova Canvas
```

---

## 🔍 **Verify AWS CLI is Configured**

First, check if AWS CLI is installed and configured:

```bash
aws --version
aws sts get-caller-identity
```

If you get an error, install AWS CLI:
- Windows: https://awscli.amazonaws.com/AWSCLIV2.msi
- Or via pip: `pip install awscli`

Then configure:
```bash
aws configure
# Enter your access key, secret key, region (us-east-1), and output format (json)
```

---

## 📊 **After Configuration**

Once you've completed the steps above, your `.env` should look like this:

```env
# Groq API Key
GROQ_API_KEY=gsk_REDACTEDnR5H

# Model Configuration
GROQ_MODEL=llama-3.3-70b-versatile

# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID=AKIA_REDACTED
AWS_SECRET_ACCESS_KEY=[AWS_SECRET_REDACTED]
AWS_REGION=us-east-1

# NEW: S3 and MediaConvert
S3_BUCKET_NAME=ai-video-generator-bucket
MEDIACONVERT_ROLE_ARN=arn:aws:iam::123456789012:role/MediaConvertRole

# Amazon Polly (TTS)
POLLY_VOICE=Joanna

# Edge TTS Voice (fallback)
TTS_VOICE=en-US-JennyNeural

# Wav2Lip Configuration (local fallback)
WAV2LIP_PATH=./Wav2Lip
WAV2LIP_CHECKPOINT=checkpoints/wav2lip_gan.pth

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Output Directories
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs
```

---

## ✅ **Final Cloud Pipeline Status**

After configuration:

| Agent | Service | Status |
|-------|---------|--------|
| 1. Ingestion | Local (pdfplumber) | Always local |
| 2. Content Understanding | Amazon Bedrock Nova Pro | ✅ Cloud |
| 3. Slide Generation | Amazon Bedrock Titan/Nova | ✅ Cloud |
| 4. Explanation | Amazon Bedrock Nova Pro | ✅ Cloud |
| 5. TTS | Amazon Polly | ✅ Cloud |
| 6. Avatar | Local Wav2Lip | ⚠️ Local (cloud optional) |
| 7. Video Composition | AWS MediaConvert | ✅ **Cloud** 🎉 |

**Result:** 5/7 agents on cloud = **71% cloud-based**  
With SageMaker avatar: 6/7 = **86% cloud-based**

---

## 💰 **Cost Estimate**

Approximate costs for AWS services:

- **Amazon Bedrock (Nova Pro)**: ~$0.003 per 1K input tokens, $0.015 per 1K output
- **Amazon Bedrock (Titan Image v2)**: ~$0.008 per image
- **Amazon Polly**: $4 per 1 million characters (very cheap)
- **AWS MediaConvert**: ~$0.015 per minute of output video
- **S3 Storage**: ~$0.023 per GB/month

**Estimated cost per 10-minute video:** $0.50 - $1.50

---

## 🚀 **Next Steps**

1. Run the setup commands above
2. Update your `.env` with the new values
3. Restart the backend: `Ctrl+C` then `python app.py`
4. Try generating a new video with `provider="amazon_bedrock"`

**Video composition will now be much faster on AWS MediaConvert!** 🎉

---

**Need help with any step? Let me know!**
