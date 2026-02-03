# 🔧 Amazon Titan Image Generator v2 - Resolution Fix

**Issue:** Validation errors when generating slides with Amazon Titan Image Generator v2

**Error Message:**
```
ValidationException: 400 Bad Request: Value of (width, height) is not valid. Given: (1280, 720).
```

---

## ❌ Problem

Amazon Titan Image Generator v2 **does not support arbitrary resolutions**. 

### Unsupported Resolution (Previous):
- Width: 1280
- Height: 720
- Aspect ratio: 16:9

---

## ✅ Solution

Updated to use **supported resolution**: 1024x1024

### Supported Resolutions for Amazon Titan Image Generator v2:

| Resolution | Aspect Ratio | Use Case |
|------------|-------------|----------|
| **1024x1024** | 1:1 (Square) | ✅ **Standard** |
| 768x768 | 1:1 (Square) | Smaller |
| 512x512 | 1:1 (Square) | Fastest |
| 768x1152 | 2:3 (Portrait) | Vertical |
| 384x576 | 2:3 (Portrait) | Smaller vertical |
| 1152x768 | 3:2 (Landscape) | Horizontal |
| 576x384 | 3:2 (Landscape) | Smaller horizontal |

**Note:** Amazon Titan does NOT support standard 16:9 (1920x1080 or 1280x720) resolutions.

---

## 🔧 Code Changes

### File: `agents/slide_generation.py`

**Changed in 2 locations:**

### 1. Titan Image Synthesis (Line 142-148)
```python
# BEFORE
"imageGenerationConfig": {
    "numberOfImages": 1,
    "height": 720,
    "width": 1280,
    "cfgScale": 10.0,
    "seed": random.randint(0, 100000)
}

# AFTER
"imageGenerationConfig": {
    "numberOfImages": 1,
    "height": 1024,
    "width": 1024,
    "cfgScale": 10.0,
    "seed": random.randint(0, 100000)
}
```

### 2. Nova Canvas Background (Line 182-188)
```python
# BEFORE
"imageGenerationConfig": {
    "numberOfImages": 1,
    "height": 720,
    "width": 1280,
    "cfgScale": 8.0,
    "seed": 0
}

# AFTER
"imageGenerationConfig": {
    "numberOfImages": 1,
    "height": 1024,
    "width": 1024,
    "cfgScale": 8.0,
    "seed": 0
}
```

---

## 📐 Impact

### Slide Display
- Generated images: **1024x1024** (square)
- Final slides: Still **1920x1080** (16:9)
- The square AI images are resized/cropped to fit the 1920x1080 slide canvas in `_create_canvas()` method

### Result
- ✅ No more validation errors
- ✅ Titan images generate successfully
- ✅ Slides still display at 1920x1080 in final video
- ⚠️ Square images may be cropped when fitted to 16:9 slides

---

## 🎯 Alternative Solution (Future)

If you want landscape slides directly from Titan, you could use:
```python
"height": 768,
"width": 1152  # 3:2 aspect ratio (closer to 16:9)
```

Or even better for presentations:
```python
"height": 576,
"width": 1024  # 16:9 aspect ratio approximation
```

But 1024x1024 is the safest and most supported option.

---

## ✅ Status

**Fixed!** Backend restarted with correct resolution settings.

Next video generation with Amazon Bedrock will now work without validation errors! 🎉

---

**Date Fixed:** January 30, 2026  
**File Modified:** `agents/slide_generation.py`
