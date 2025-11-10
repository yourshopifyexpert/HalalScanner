# Chandra OCR Integration

HalalScanner now uses **Chandra OCR** from datalab-to for real text extraction from product photos!

## Features

✅ **Real OCR** - Actual text extraction from uploaded images
✅ **40+ Languages** - Arabic, Urdu, English, and more
✅ **Complex Layouts** - Handles product labels, tables, forms
✅ **Handwriting Support** - Can read handwritten ingredient lists
✅ **Lightweight** - Uses HuggingFace Inference API (no heavy models)

## How It Works

1. **User uploads photo** → Web UI converts to base64
2. **Backend processes** → ChandraOCRService sends to HuggingFace API
3. **Chandra extracts text** → Returns ingredient list
4. **Classification** → Rules engine analyzes ingredients
5. **Results displayed** → HALAL/HARAM/SUSPICIOUS verdict

## API Endpoint

```bash
curl -X POST https://halalscanner-api-production.up.railway.app/api/v1/scan/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "image_base64": "YOUR_BASE64_IMAGE_HERE",
    "language_hint": "en"
  }'
```

## Web Interface

Visit: **https://halalscanner-api-production.up.railway.app/**

1. Click upload area or drag and drop product photo
2. Image is automatically processed with Chandra OCR
3. Extracted text appears in ingredients box
4. Classification results shown instantly

## Optional: HuggingFace API Token

For higher rate limits, set `HUGGINGFACE_API_TOKEN` environment variable in Railway:

1. Go to Railway dashboard → Your service → Variables
2. Add: `HUGGINGFACE_API_TOKEN` = your token from https://huggingface.co/settings/tokens
3. Redeploy

## Fallback Behavior

If Chandra model is loading or unavailable:
- Automatically falls back to demo OCR
- Returns sample ingredients for testing
- No errors - graceful degradation

## Supported Languages

Arabic, English, French, German, Spanish, Urdu, Hindi, Chinese, Japanese, and 30+ more.

Perfect for scanning halal products from around the world!
