# AWS Bedrock Pipeline - Fixed Provider Routing

## ✅ Issue Identified & Fixed

**Problem:** Inconsistent provider string checking across agents caused AWS Bedrock mode to partially fail.

### Provider String Variations:
- Frontend/API sends: `provider="amazon_bedrock"`
- Some agents checked: `provider == "bedrock" or provider == "aws"`  
- Other agents checked: `provider == "amazon_bedrock"`

**Result:** Content Understanding and Explanation worked (checked for `"amazon_bedrock"`), but TTS, Avatar, and Video Composition failed (only checked for `"bedrock"` or `"aws"`).

---

## 🔧 Files Fixed

All agents now accept **all three variations**: `"amazon_bedrock"`, `"bedrock"`, `"aws"`

1. **agents/tts.py** - Line 40
   ```python
   # BEFORE
   if provider == "bedrock" or provider == "aws":
   
   # AFTER  
   if provider in ["bedrock", "aws", "amazon_bedrock"]:
   ```

2. **agents/avatar.py** - Line 91
   ```python
if provider in ["bedrock", "aws", "amazon_bedrock"]:
   ```

3. **agents/video_composition.py** - Line 71
   ```python
   if provider in ["bedrock", "aws", "amazon_bedrock"] and self.s3_bucket and self.mc_role_arn:
   ```

4. **agents/slide_generation.py** - Lines 99 & 108
   ```python
   if provider in ["bedrock", "aws", "amazon_bedrock"]:
   ```

---

## 🌩️ AWS Bedrock Pipeline - Complete Flow

When `provider="amazon_bedrock"` is set:

### 1. ✅ Content Understanding → Amazon Nova Pro v1
- **Cloud Service:** Amazon Bedrock Runtime
- **Model:** `amazon.nova-pro-v1:0`
- **Status:** Working ✓

### 2. ✅ Slide Generation → Amazon Titan Image v2 + Nova Canvas
- **Cloud Services:** 
  - `amazon.titan-image-generator-v2:0` (full slide synthesis)
  - `amazon.nova-canvas-v1:0` (background generation)
- **Status:** Working ✓

### 3. ✅ Explanation → Amazon Nova Pro v1
- **Cloud Service:** Amazon Bedrock Runtime
- **Model:** `amazon.nova-pro-v1:0`
- **Status:** Working ✓

### 4. ✅ TTS → Amazon Polly (NOW FIXED)
- **Cloud Service:** Amazon Polly
- **Voice Engine:** Neural TTS
- **Status:** Fixed - will now route to Polly ✓

### 5. ✅ Avatar → AWS SageMaker (NOW FIXED)
- **Cloud Services:**
  - AWS SageMaker Runtime
  - AWS S3 (asset storage)
- **Endpoint:** `wav2lip-endpoint` (requires setup)
- **Status:** Fixed - will route if configured ✓
- **Fallback:** Local Wav2Lip if endpoint not configured

### 6. ✅ Video Composition → AWS MediaConvert (NOW FIXED)
- **Cloud Services:**
  - AWS MediaConvert
  - AWS S3 (asset distribution)
- **Status:** Fixed - will route if configured ✓
- **Fallback:** Local MoviePy (default)

### 7. 📄 Ingestion → Always Local
- **No cloud option** (pdfplumber, PyMuPDF)

---

## 🎯 Required Environment Variables for Full AWS Mode

```env
# AWS Credentials (Required for all AWS services)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1

# TTS (Amazon Polly)
POLLY_VOICE=Joanna  # Optional, default: Joanna

# Avatar (SageMaker)
S3_BUCKET_NAME=your-bucket-name
SAGEMAKER_ENDPOINT_NAME=wav2lip-endpoint

# Video Composition (MediaConvert)
MEDIACONVERT_ROLE_ARN=arn:aws:iam::...:role/MediaConvertRole
```

---

## 📊 Previous Error Analysis

### Error from Log:
```
ERROR: WSServerHandshakeError: 403, message='Invalid response status'
url='wss://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1'
```

**Root Cause:** TTS Agent didn't recognize `provider="amazon_bedrock"` and fell back to Edge TTS, which was blocked by Microsoft (403 error).

**Solution:** Now routes to Amazon Polly when AWS mode is enabled.

---

## ✅ Pipeline Now Fully Consistent

All agents now properly recognize and route to AWS services when:
- `provider="amazon_bedrock"` (from frontend)
- `provider="bedrock"` (legacy)
- `provider="aws"` (legacy)

**Status:** All 5 cloud-capable agents now properly route to AWS! 🚀

---

**Date Fixed:** January 30, 2026  
**Version:** 1.0 (Post-fix)
