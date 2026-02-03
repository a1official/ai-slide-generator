# AWS Bedrock Pipeline - Actual Current Status

## 📊 What's ACTUALLY Running on Cloud vs Local

Based on your current `.env` configuration and the video generation log:

### ✅ Currently Running on AWS Cloud (4 agents)

| Agent | AWS Service | Evidence | Status |
|-------|-------------|----------|---------|
| **1. Content Understanding** | Amazon Bedrock (Nova Pro v1) | Log shows: `[*] Invoking Amazon Bedrock: amazon.nova-pro-v1:0...` | ✅ **ON CLOUD** |
| **2. Slide Generation** | Amazon Bedrock (Titan/Nova) | Successfully generated 17 slides (would show PIL logs if local) | ✅ **ON CLOUD** |
| **3. Explanation** | Amazon Bedrock (Nova Pro v1) | Generated scripts via Bedrock | ✅ **ON CLOUD** |
| **4. TTS** | ❓ Unknown (likely Edge TTS) | No Polly logs visible, but fixed code | ⚠️ **UNCLEAR** |

### ❌ Currently Running LOCALLY (3 agents)

| Agent | Local Tool | Evidence | Why Local? |
|-------|-----------|----------|-----------|
| **5. Avatar** | Wav2Lip (skipped) | No avatar generation in logs | No avatar image provided |
| **6. Video Composition** | 🔴 **MoviePy** | Log shows: `Moviepy - Building video...` `MoviePy - Writing audio...` | **Missing S3_BUCKET_NAME and MEDIACONVERT_ROLE_ARN** |
| **7. Ingestion** | pdfplumber | Always local | No cloud option |

---

## 🚨 **Why Video Composition is LOCAL**

The video composition agent checks this condition:

```python
if provider in ["bedrock", "aws", "amazon_bedrock"] and self.s3_bucket and self.mc_role_arn:
    # Use AWS MediaConvert
else:
    # Use local MoviePy (THIS IS WHAT'S HAPPENING)
```

### Missing Environment Variables:

```env
# ❌ NOT IN YOUR .env
S3_BUCKET_NAME=your-bucket-name
MEDIACONVERT_ROLE_ARN=arn:aws:iam::123456789012:role/MediaConvertRole
```

Without these, it falls back to **local MoviePy processing** (which is slow).

---

## 🎯 **What About TTS?**

Looking at the logs, I don't see explicit Amazon Polly messages. The TTS might still be using **Edge TTS** (which succeeded this time, or used Amazon Polly silently).

To verify, we should add debug logging.

---

## 📝 **Current AWS Configuration Status**

### ✅ Configured (Working):
```env
AWS_ACCESS_KEY_ID=AKIA_REDACTED
AWS_SECRET_ACCESS_KEY=[AWS_SECRET_REDACTED]
AWS_REGION=us-east-1
```

### ❌ Missing for Full Cloud Pipeline:
```env
# For TTS (Amazon Polly)
POLLY_VOICE=Joanna  # Optional, has default

# For Avatar (SageMaker)
S3_BUCKET_NAME=your-bucket-name  # REQUIRED
SAGEMAKER_ENDPOINT_NAME=wav2lip-endpoint  # REQUIRED

# For Video Composition (MediaConvert)
S3_BUCKET_NAME=your-bucket-name  # REQUIRED (same as above)
MEDIACONVERT_ROLE_ARN=arn:aws:iam::YOUR_ACCOUNT_ID:role/MediaConvertRole  # REQUIRED
```

---

## 🔧 **How to Fix Video Composition Speed**

### Option 1: Enable AWS MediaConvert (Cloud Rendering)

**Step 1:** Create an S3 bucket:
```bash
aws s3 mb s3://your-video-generation-bucket
```

**Step 2:** Create MediaConvert IAM Role:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "mediaconvert.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
```

Attach policies: `AmazonS3FullAccess`, `AmazonAPIGatewayInvokeFullAccess`

**Step 3:** Add to `.env`:
```env
S3_BUCKET_NAME=your-video-generation-bucket
MEDIACONVERT_ROLE_ARN=arn:aws:iam::123456789012:role/MediaConvertRole
```

### Option 2: Keep Local Processing (Faster Alternative)

If you don't want to set up MediaConvert, the local processing will work fine, but:

**Speed up local processing:**
1. Use a machine with better GPU (for MoviePy encoding)
2. Reduce video quality in the code
3. Use fewer slides
4. Use faster codec settings

---

## 📊 **Summary: 4 out of 7 Agents on Cloud**

### Currently on AWS Cloud ✅
1. ✅ Content Understanding (Bedrock Nova Pro)
2. ✅ Slide Generation (Bedrock Titan/Nova)
3. ✅ Explanation (Bedrock Nova Pro)
4. ⚠️ TTS (Fixed but unclear if actually using Polly)

### Currently Local ❌
5. ❌ Avatar (skipped - no image provided)
6. ❌ **Video Composition (MoviePy - NEEDS S3 + MediaConvert Role)**
7. ❌ Ingestion (always local)

---

## 💡 **Recommendation**

For now, **4 out of 7 agents are on the cloud** (57% cloud-based), which is pretty good!

The video composition is the slow part because MoviePy runs locally and encodes frame-by-frame.

**Quick wins to speed up:**
- Reduce number of slides
- Lower video quality in `video_composition.py` (change `preset='medium'` to `preset='ultrafast'`)
- Use fewer/shorter audio scripts

**Full cloud solution:**
- Set up S3 bucket and MediaConvert role (instructions above)

---

**Current Status:** Your pipeline is **partially cloud-based** (4/7 agents), with video composition being the bottleneck due to missing AWS MediaConvert configuration.

**Updated:** January 30, 2026 11:55 AM
